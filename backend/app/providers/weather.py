import httpx

from ..config import Settings
from .base import Provider

WMO_DESCRIPTIONS = {
    0: "Bezchmurnie",
    1: "Przeważnie bezchmurnie",
    2: "Częściowe zachmurzenie",
    3: "Pochmurno",
    45: "Mgła",
    48: "Szron mglisty",
    51: "Lekka mżawka",
    53: "Mżawka",
    55: "Intensywna mżawka",
    56: "Lekka mżawka marznąca",
    57: "Mżawka marznąca",
    61: "Słaby deszcz",
    63: "Deszcz",
    65: "Intensywny deszcz",
    66: "Deszcz marznący",
    67: "Intensywny deszcz marznący",
    71: "Słaby śnieg",
    73: "Śnieg",
    75: "Intensywny śnieg",
    77: "Ziarna śniegu",
    80: "Słabe przelotne opady deszczu",
    81: "Przelotne opady deszczu",
    82: "Intensywne przelotne opady",
    85: "Przelotne opady śniegu",
    86: "Intensywne przelotne opady śniegu",
    95: "Burza",
    96: "Burza z gradem",
    99: "Burza z silnym gradem",
}

URL = "https://api.open-meteo.com/v1/forecast"


class WeatherProvider(Provider):
    key = "weather"

    def __init__(self, settings: Settings):
        self.settings = settings

    async def fetch(self) -> dict:
        params = {
            "latitude": self.settings.weather_lat,
            "longitude": self.settings.weather_lon,
            "timezone": self.settings.timezone,
            "current": (
                "temperature_2m,apparent_temperature,relative_humidity_2m,"
                "weather_code,wind_speed_10m"
            ),
            "daily": "weather_code,temperature_2m_max,temperature_2m_min",
            "forecast_days": 1,
        }
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(URL, params=params)
            resp.raise_for_status()
            data = resp.json()

        current = data["current"]
        daily = data["daily"]
        code = int(current["weather_code"])
        daily_code = int(daily["weather_code"][0])

        return {
            "temperature": round(float(current["temperature_2m"]), 1),
            "apparent": round(float(current["apparent_temperature"]), 1),
            "humidity": int(current["relative_humidity_2m"]),
            "wind": round(float(current["wind_speed_10m"]), 1),
            "code": code,
            "description": WMO_DESCRIPTIONS.get(code, ""),
            "daily": {
                "code": daily_code,
                "description": WMO_DESCRIPTIONS.get(daily_code, ""),
                "max": round(float(daily["temperature_2m_max"][0]), 1),
                "min": round(float(daily["temperature_2m_min"][0]), 1),
            },
        }
