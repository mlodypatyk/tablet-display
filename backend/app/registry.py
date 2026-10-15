from .config import Settings
from .providers.base import Provider
from .providers.train import TrainProvider
from .providers.weather import WeatherProvider
from .providers.ztm import MockZtmProvider, ZtmProvider


def build_providers(settings: Settings) -> list[Provider]:
    providers: list[Provider] = [
        WeatherProvider(settings),
        TrainProvider(settings),
    ]

    if settings.ztm_apikey:
        providers.append(ZtmProvider(settings))
    else:
        providers.append(MockZtmProvider(settings))

    return providers
