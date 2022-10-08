from typing import Any

from pydantic import BaseModel


class BaseAdapter:
    async def create(self, data: BaseModel) -> BaseModel:
        pass

    async def update(
        self,
        data: BaseModel,
        id: Any,
        key: str,
        update_key: str,
    ) -> BaseModel:
        pass

    async def get(self, id: Any, key: str) -> BaseModel:
        pass

    async def get_all(self, skip: int = 0, limit: int = 10) -> list[BaseModel]:
        pass

    async def delete(self, id: Any, key: str):
        pass
