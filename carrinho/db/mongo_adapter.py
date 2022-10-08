import logging
from typing import Any, List

import models
from fastapi import Depends
from pydantic import BaseModel, EmailStr
from pymongo.errors import DuplicateKeyError, PyMongoError

from carrinho.db.base import BaseAdapter
from carrinho.db.exception import ObjetoNaoEncontrado, ObjetoNaoModificado
from carrinho.db.mondo_db import DataBase, get_db


class MongoBaseAdapter(BaseAdapter):
    def __init__(self, collection):
        self.collection = collection

    async def create(self, data: BaseModel) -> BaseModel:
        try:
            await self.collection.insert_one(data.dict())
            return data
        except DuplicateKeyError as e:
            logging.error(e)
            raise

    async def update(
        self,
        data: BaseModel,
        id: Any,
        key: str,
        update_key: str,
    ) -> BaseModel:
        updated = await self.collection.update_one(
            {key: id}, {"$addToSet": {update_key: data.dict()}}
        )
        if updated.matched_count == 0:
            raise ObjetoNaoEncontrado
        if updated.modified_count == 0:
            raise ObjetoNaoModificado
        return data

    async def get(self, id: Any, key: str) -> BaseModel:
        try:
            data = await self.collection.find_one({key: id})
            return data
        except Exception as e:
            logging.error(e)
            return

    async def get_all(self, skip: int = 0, limit: int = 10) -> List[BaseModel]:
        try:
            cursor = self.collection.find().skip(skip).limit(limit)
            data = await cursor.to_list(length=limit)
            return data
        except Exception as e:
            logging.error(e)
            return

    async def delete(self, id: Any, key: str):
        try:
            data = await self.collection.delete_one({key: id})
            if data.deleted_count == 0:
                return False
            return True
        except PyMongoError as e:
            logging.error(e)
            raise


class UserAdapter(MongoBaseAdapter):
    async def create(self, data: models.Usuario) -> models.Usuario:
        return await super().create(data)

    async def create_addr(
        self,
        email: EmailStr,
        endereco: models.Endereco,
    ) -> models.Usuario:
        return await super().update(endereco, email, "email", update_key="endereco")

    async def get(self, email: EmailStr) -> models.Usuario:
        return await super().get(email, key="email")

    async def get_all(self, skip: int = 0, limit: int = 10) -> List[models.Usuario]:
        return await super().get_all(skip=skip, limit=limit)

    async def delete(self, email: EmailStr):
        return await super().delete(email, key="email")

    async def remover_endereco(self, endereco: models.Endereco, email):
        updated = await self.collection.update_one(
            {"email": email},
            {
                "$pull": {
                    "endereco": {
                        "rua": endereco.rua,
                        "cep": endereco.cep,
                        "cidade": endereco.cidade,
                        "estado": endereco.estado,
                    }
                }
            },
        )
        if updated.matched_count == 0:
            raise ObjetoNaoEncontrado
        if updated.modified_count == 0:
            raise ObjetoNaoModificado
        return endereco


class ProductAdapter(MongoBaseAdapter):
    async def create(self, data: models.Produto) -> models.Produto:
        return await super().create(data)

    async def get(self, id_produto: int) -> models.Produto:
        return await super().get(id_produto, key="id")

    async def delete(self, id_produto: int):
        return await super().delete(id_produto, key="id")


async def get_user_adapter(db: DataBase = Depends(get_db)) -> UserAdapter:
    user_adapter = UserAdapter(db.users_collection)
    return user_adapter


async def get_produto_adapter(db: DataBase = Depends(get_db)) -> ProductAdapter:
    product_adapter = ProductAdapter(db.product_collection)
    return product_adapter
