import asyncio
import logging
from datetime import datetime, timezone

from .providers.base import Provider

logger = logging.getLogger(__name__)


class DashboardCache:
    def __init__(self, providers: list[Provider], refresh_seconds: int):
        self.providers = providers
        self.refresh_seconds = refresh_seconds
        self._data: dict = {}
        self._last_good: dict[str, dict] = {}
        self._sources: dict[str, str] = {}
        self._lock = asyncio.Lock()
        self._task: asyncio.Task | None = None

    async def refresh(self) -> dict:
        async def run(provider: Provider):
            try:
                result = await provider.fetch()
                self._last_good[provider.key] = result
                return provider.key, result, "ok"
            except Exception as exc:  # noqa: BLE001
                logger.warning("Provider %s failed: %s", provider.key, exc)
                status = "stale" if provider.key in self._last_good else "error"
                return provider.key, self._last_good.get(provider.key), status

        results = await asyncio.gather(*(run(p) for p in self.providers))

        payload: dict = {"generated_at": datetime.now(timezone.utc).isoformat()}
        sources: dict[str, str] = {}
        for key, data, status in results:
            sources[key] = status
            payload[key] = data

        payload["sources"] = sources

        async with self._lock:
            self._data = payload
            self._sources = sources

        return payload

    async def snapshot(self) -> dict:
        async with self._lock:
            if not self._data:
                return {}
            return dict(self._data)

    def start(self):
        async def loop():
            while True:
                try:
                    await self.refresh()
                except Exception as exc:  # noqa: BLE001
                    logger.exception("Refresh loop error: %s", exc)
                await asyncio.sleep(self.refresh_seconds)

        self._task = asyncio.create_task(loop())

    async def stop(self):
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
