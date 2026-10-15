from abc import ABC, abstractmethod


class Provider(ABC):
    key: str = ""

    @abstractmethod
    async def fetch(self) -> dict:
        raise NotImplementedError
