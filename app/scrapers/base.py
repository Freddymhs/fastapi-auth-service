from abc import ABC, abstractmethod
from typing import Any


class BaseScraper(ABC):
    @abstractmethod
    async def scrape(self) -> Any: ...

    @abstractmethod
    async def parse(self, raw_data: Any) -> Any: ...

    @abstractmethod
    async def save(self, parsed_data: Any) -> None: ...

    async def run(self) -> None:
        raw = await self.scrape()
        parsed = await self.parse(raw)
        await self.save(parsed)
