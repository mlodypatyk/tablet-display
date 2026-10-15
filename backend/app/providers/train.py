from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import httpx
from bs4 import BeautifulSoup

from ..config import Settings
from .base import Provider

BASE = "https://rozklad-pkp.pl"
STATION_SEARCH = f"{BASE}/station/search"
STATION_BOARD = f"{BASE}/pl/sq"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0 Safari/537.36"
    ),
    "Accept-Language": "pl-PL,pl;q=0.9",
}


class TrainProvider(Provider):
    key = "train"

    def __init__(self, settings: Settings):
        self.settings = settings
        self._eva_id = settings.train_eva_id or ""

    async def _resolve_eva_id(self, client: httpx.AsyncClient) -> str:
        if self._eva_id:
            return self._eva_id
        resp = await client.get(
            STATION_SEARCH, params={"term": self.settings.train_station_name}
        )
        resp.raise_for_status()
        data = resp.json()
        if isinstance(data, list):
            data = data[0] if data else {}
        self._eva_id = str(data.get("value", ""))
        return self._eva_id

    async def fetch(self) -> dict:
        tz = ZoneInfo(self.settings.timezone)
        now = datetime.now(tz)

        async with httpx.AsyncClient(timeout=20, headers=HEADERS) as client:
            eva_id = await self._resolve_eva_id(client)
            if not eva_id:
                raise RuntimeError("Nie udało się rozpoznać stacji")

            params = {
                "ld": "mobil",
                "input": eva_id,
                "boardType": "dep",
                "time": now.strftime("%H:%M"),
                "maxJourneys": self.settings.train_max_departures,
                "start": "yes",
            }
            resp = await client.get(STATION_BOARD, params=params)
            resp.raise_for_status()

        departures = _parse_board(resp.text, tz, now)
        return {
            "station": self.settings.train_station_name,
            "departures": departures,
        }


def _parse_board(html: str, tz: ZoneInfo, now: datetime) -> list[dict]:
    soup = BeautifulSoup(html, "lxml")
    table = soup.find("table", id="wyniki")
    if table is None:
        return []

    departures: list[dict] = []
    for row in table.find_all("tr"):
        time_el = row.find("span", class_="time")
        if time_el is None:
            continue

        train_el = row.find("span", class_="train-name")
        cat_el = row.find("img", class_="transport-type")
        dest_el = row.find("span", class_="bold")
        dest_link = dest_el.find("a") if dest_el else None
        superhide = row.find("td", class_="superhide")
        track_el = superhide.find_previous_sibling("td") if superhide else None

        prognosis = row.select_one(".prognosis-column img")
        status = "ontime"
        if prognosis is not None and "rt_delay" in prognosis.get("src", ""):
            status = "delayed"

        track = track_el.get_text(" ", strip=True) if track_el else ""
        track = " ".join(track.split()).replace("&nbsp;", "")

        time_text = time_el.get_text(strip=True)
        try:
            dep_dt = datetime.strptime(time_text, "%H:%M").replace(tzinfo=tz)
            dep_dt = dep_dt.replace(year=now.year, month=now.month, day=now.day)
            if dep_dt < now - timedelta(minutes=1):
                dep_dt += timedelta(days=1)
            minutes = max(0, int((dep_dt - now).total_seconds() // 60))
        except ValueError:
            minutes = None

        departures.append(
            {
                "time": time_text,
                "destination": dest_link.get_text(strip=True) if dest_link else "",
                "train": train_el.get_text(strip=True) if train_el else "",
                "category": cat_el.get("alt", "") if cat_el else "",
                "track": track,
                "status": status,
                "minutes": minutes,
            }
        )

    return departures
