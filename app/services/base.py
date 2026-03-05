from abc import ABC, abstractmethod
from typing import Any


class BaseService(ABC):
    @abstractmethod
    async def get(self, entity_id: Any) -> Any: ...

    @abstractmethod
    async def get_all(self, *, offset: int = 0, limit: int = 100) -> list[Any]: ...

    @abstractmethod
    async def create(self, data: Any) -> Any: ...

    @abstractmethod
    async def update(self, entity_id: Any, data: Any) -> Any: ...

    @abstractmethod
    async def delete(self, entity_id: Any) -> None: ...
