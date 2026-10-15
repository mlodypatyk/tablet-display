import os
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = BASE_DIR / "config.toml"


@dataclass
class Stop:
    name: str
    busstop_id: str
    busstop_nr: str


@dataclass
class Settings:
    weather_lat: float = 52.2297
    weather_lon: float = 21.0122
    timezone: str = "Europe/Warsaw"
    refresh_seconds: int = 60
    transit_max_departures: int = 6
    train_max_departures: int = 8
    stops: list[Stop] = field(default_factory=list)
    train_station_name: str = "Warszawa Praga"
    train_eva_id: str = ""
    ztm_apikey: str = ""

    @classmethod
    def load(cls, config_path: Path = CONFIG_PATH) -> "Settings":
        data: dict = {}
        if config_path.exists():
            with config_path.open("rb") as fh:
                data = tomllib.load(fh)

        load_dotenv(BASE_DIR / ".env")

        s = cls()
        weather = data.get("weather", {})
        s.weather_lat = float(weather.get("latitude", s.weather_lat))
        s.weather_lon = float(weather.get("longitude", s.weather_lon))
        s.timezone = weather.get("timezone", s.timezone)

        general = data.get("general", {})
        s.refresh_seconds = int(general.get("refresh_seconds", s.refresh_seconds))

        transit = data.get("transit", {})
        s.transit_max_departures = int(
            transit.get("max_departures", s.transit_max_departures)
        )
        for stop in transit.get("stops", []):
            s.stops.append(
                Stop(
                    name=str(stop["name"]),
                    busstop_id=str(stop["busstop_id"]),
                    busstop_nr=str(stop["busstop_nr"]),
                )
            )

        train = data.get("train", {})
        s.train_station_name = train.get("station_name", s.train_station_name)
        s.train_eva_id = str(train.get("eva_id", ""))
        s.train_max_departures = int(
            train.get("max_departures", s.train_max_departures)
        )

        s.ztm_apikey = os.getenv("ZTM_APIKEY", "").strip()
        return s
