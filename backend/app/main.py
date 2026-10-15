import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from .cache import DashboardCache
from .config import Settings
from .registry import build_providers

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = Settings.load()
cache = DashboardCache(build_providers(settings), settings.refresh_seconds)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await cache.refresh()
    cache.start()
    yield
    await cache.stop()


app = FastAPI(title="Tablet Display", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/dashboard")
async def dashboard():
    data = await cache.snapshot()
    if not data:
        return JSONResponse(
            status_code=503,
            content={"generated_at": None, "sources": {}, "detail": "not ready"},
        )
    return data


@app.get("/api/health")
async def health():
    return {"status": "ok"}


frontend_dist = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"
if frontend_dist.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dist), html=True), name="static")
