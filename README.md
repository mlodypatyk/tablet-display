# Tablet Display

A wall-tablet dashboard that polls a local JSON backend once a minute and shows:

- current weather (Open-Meteo, metric)
- upcoming departures from configured Warsaw public-transit stops (ZTM)
- upcoming train departures from Warszawa Praga station

Backend: FastAPI (Python). Frontend: React + Vite. Polish UI.

## Structure

```
backend/            FastAPI service that aggregates all sources into one JSON
  app/
    main.py         app entry, /api/dashboard, serves built frontend
    config.py       loads config.toml + .env
    registry.py     assembles data-source providers
    cache.py        background refresh loop + last-good cache
    providers/      one module per data source (pluggable)
frontend/           React + Vite app (Polish UI)
config.toml         backend configuration (transit stops, train station, ...)
```

## Prerequisites

- Python 3.11+ (3.13 tested)
- Node.js 18+ and npm

## Backend setup

```powershell
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

# copy and fill in the ZTM API key (optional but recommended)
Copy-Item .env.example .env
```

### ZTM API key (transit)

Register for a free key at <https://api.um.warszawa.pl>, then put it in `backend/.env`:

```
ZTM_APIKEY=your-key-here
```

Until a key is set, the backend serves clearly-marked sample data so the UI still
works end to end.

### Transit stops

Edit `backend/config.toml` and add one `[[transit.stops]]` block per stop. Each stop
needs the ZTM `busstop_id` (zespół przystankowy) and `busstop_nr` (słupek).

The API's name-search endpoint is currently broken, so the practical way to find the
numbers is either:

- open a stop's timetable on the ZTM site (e.g. <https://www.wtp.waw.pl/rozklady-jazdy/>)
  and read them from the resulting URL, or
- download the GTFS feed `stops.txt` from <https://mkuran.pl/gtfs/warsaw.zip> and join
  `stop_id` (`busstopId` + zero-padded `busstopNr`, e.g. `700901`) to the stop name.

A known-good example (included) is `busstop_id = "7009"`, `busstop_nr = "01"`
(Marszałkowska).

## Frontend setup

```powershell
cd frontend
npm install
```

## Run (development)

Two terminals:

```powershell
# 1) backend
cd backend
.venv\Scripts\activate
uvicorn app.main:app --reload

# 2) frontend dev server (proxies /api -> localhost:8000)
cd frontend
npm run dev
```

Open <http://localhost:5173> on the tablet.

## Run (production, single process)

```powershell
cd frontend
npm run build

cd ..\backend
.venv\Scripts\activate
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

The backend detects `frontend/dist` and serves it, so point the tablet at
`http://<server-ip>:8000`. Data refreshes every `refresh_seconds` (default 60s).

## API

`GET /api/dashboard`

```json
{
  "generated_at": "2026-10-15T20:57:27+00:00",
  "sources": { "weather": "ok", "transit": "ok", "train": "ok" },
  "weather": { "temperature": 9.6, "description": "...", "daily": { "min": 8.6, "max": 13.4 } },
  "transit": { "stops": [ { "name": "...", "number": "01", "departures": [ { "line": "3", "direction": "...", "time": "23:07", "minutes": 11 } ] } ] },
  "train": { "station": "Warszawa Praga", "departures": [ { "time": "23:01", "destination": "Piaseczno", "train": "SKW 11234", "track": "I/2", "status": "ontime", "minutes": 3 } ] }
}
```

When a source fails, its top-level key becomes `null` and `sources[<key>]` reports
`stale` (serving last-good data) or `error` (no data yet).

## Adding a new data source

1. Add a provider in `backend/app/providers/` subclassing `Provider` with a unique
   `key` and an async `fetch()` that returns a `dict`.
2. Register it in `backend/app/registry.py`.
3. Add a card component in `frontend/src/components/` and render it in
   `frontend/src/App.tsx`.
