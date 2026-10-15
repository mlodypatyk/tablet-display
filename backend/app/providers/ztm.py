import asyncio
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import httpx

from ..config import Settings, Stop
from .base import Provider

ZTM_URL = "https://api.um.warszawa.pl/api/action/dbtimetable_get"

# Identyfikatory "metod" API ZTM (dbtimetable_get)
LINES_METHOD = "88cd555f-6f31-43ca-9de4-66c479ad5942"      # linie obsługujące słupek
TIMETABLE_METHOD = "e923fa0e-d96c-43f9-ae6e-60518c9f3238"  # rozkład danej linii


def _filter_sort(
    departures: list[dict], now: datetime, tz: ZoneInfo, limit: int
) -> list[dict]:
    upcoming: list[dict] = []
    for dep in departures:
        time_str = dep.get("time", "")
        try:
            t = datetime.strptime(time_str, "%H:%M:%S").time()
        except ValueError:
            continue
        dep_dt = datetime.combine(now.date(), t, tzinfo=tz)
        if dep_dt < now - timedelta(minutes=1):
            continue
        dep["time"] = t.strftime("%H:%M")
        dep["minutes"] = max(0, int((dep_dt - now).total_seconds() // 60))
        upcoming.append(dep)

    upcoming.sort(key=lambda d: d["minutes"])
    return upcoming[:limit]


class ZtmProvider(Provider):
    key = "transit"

    def __init__(self, settings: Settings):
        self.settings = settings

    async def _lines(self, client: httpx.AsyncClient, stop: Stop) -> list[str]:
        params = {
            "id": LINES_METHOD,
            "busstopId": stop.busstop_id,
            "busstopNr": stop.busstop_nr,
            "apikey": self.settings.ztm_apikey,
        }
        resp = await client.get(ZTM_URL, params=params)
        resp.raise_for_status()
        result = resp.json().get("result")
        if not isinstance(result, list):
            return []

        lines: list[str] = []
        for item in result:
            for pair in item.get("values", []):
                if pair.get("key") == "linia":
                    lines.append(pair.get("value"))
        return lines

    async def _departures_for_line(
        self, client: httpx.AsyncClient, stop: Stop, line: str
    ) -> list[dict]:
        params = {
            "id": TIMETABLE_METHOD,
            "busstopId": stop.busstop_id,
            "busstopNr": stop.busstop_nr,
            "line": line,
            "apikey": self.settings.ztm_apikey,
        }
        resp = await client.get(ZTM_URL, params=params)
        resp.raise_for_status()
        result = resp.json().get("result")
        if not isinstance(result, list):
            return []

        departures: list[dict] = []
        for row in result:
            d = {pair.get("key"): pair.get("value") for pair in row}
            departures.append(
                {
                    "line": line,
                    "direction": d.get("kierunek") or "",
                    "time": d.get("czas") or "",
                }
            )
        return departures

    async def fetch(self) -> dict:
        if not self.settings.ztm_apikey:
            raise RuntimeError("Brak klucza API ZTM (ZTM_APIKEY)")

        tz = ZoneInfo(self.settings.timezone)
        now = datetime.now(tz)
        stops_out: list[dict] = []

        async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
            for stop in self.settings.stops:
                lines = await self._lines(client, stop)
                per_line = await asyncio.gather(
                    *(
                        self._departures_for_line(client, stop, line)
                        for line in lines
                    )
                )
                all_deps: list[dict] = []
                for line_deps in per_line:
                    all_deps.extend(line_deps)

                departures = _filter_sort(
                    all_deps, now, tz, self.settings.transit_max_departures
                )
                stops_out.append(
                    {
                        "name": stop.name,
                        "number": stop.busstop_nr,
                        "departures": departures,
                    }
                )

        return {"stops": stops_out}


class MockZtmProvider(Provider):
    """Zwraca przykładowe dane, dopóki nie ma klucza ZTM."""

    key = "transit"

    def __init__(self, settings: Settings):
        self.settings = settings

    async def fetch(self) -> dict:
        tz = ZoneInfo(self.settings.timezone)
        now = datetime.now(tz)
        stops: list[dict] = []

        for idx, stop in enumerate(self.settings.stops):
            departures = []
            for offset in (3, 11, 18, 26):
                dep_dt = now + timedelta(minutes=offset)
                departures.append(
                    {
                        "line": ["3", "25", "N44"][idx % 3],
                        "direction": "Kierunek przykładowy",
                        "time": dep_dt.strftime("%H:%M"),
                        "minutes": offset,
                    }
                )
            stops.append(
                {
                    "name": stop.name,
                    "number": stop.busstop_nr,
                    "departures": departures,
                    "mock": True,
                }
            )

        return {"stops": stops, "mock": True}
