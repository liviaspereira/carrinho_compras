import email
from json import encoder
import logging
from venv import create
from pymongo.errors import DuplicateKeyError, PyMongoError
from typing import List, Any
from pydantic import BaseModel, EmailStr
from motor.motor_asyncio import AsyncIOMotorCollection
import models


class ObjetoNaoEncontrado(Exception):
    """Quando for feito uma update e o matched_count == 0"""


class ObjetoNaoModificado(Exception):
    """Quando o update for igual a um existente"""


class BaseAdapter:
    async def create(
        self, collection: AsyncIOMotorCollection, data: BaseModel
    ) -> BaseModel:
        try:
            await collection.insert_one(data.dict())
            return data
        except DuplicateKeyError as e:
            logging.error(e)
            raise

    async def update(
        self,
        collection: AsyncIOMotorCollection,
        data: BaseModel,
        id: Any,
        key: str,
        update_key: str,
    ) -> BaseModel:
        updated = await collection.update_one(
            {key: id}, {"$addToSet": {update_key: data.dict()}}
        )
        if updated.matched_count == 0:
            raise ObjetoNaoEncontrado
        if updated.modified_count == 0:
            raise ObjetoNaoModificado
        return data

    async def get(
        self, collection: AsyncIOMotorCollection, id: Any, key: str
    ) -> BaseModel:
        try:
            data = await collection.find_one({key: id})
            return data
        except Exception as e:
            logging.error(e)
            return

    async def get_all(
        self, collection: AsyncIOMotorCollection, skip: int = 0, limit: int = 10
    ) -> List[BaseModel]:
        try:
            cursor = collection.find().skip(skip).limit(limit)
            data = await cursor.to_list(length=limit)
            return data
        except Exception as e:
            logging.error(e)
            return

    async def delete(self, collection: AsyncIOMotorCollection, id: Any, key: str):
        try:
            data = await collection.delete_one({key: id})
            if data.deleted_count == 0:
                return False
            return True
        except PyMongoError as e:
            logging.error(e)
            raise


class UserAdapter(BaseAdapter):
    async def create(
        self, collection: AsyncIOMotorCollection, data: models.Usuario
    ) -> models.Usuario:
        return await super().create(collection, data)

    async def create_addr(
        self,
        collection: AsyncIOMotorCollection,
        email: EmailStr,
        endereco: models.Endereco,
    ) -> models.Usuario:
        return await super().update(
            collection, endereco, email, "email", update_key="endereco"
        )

    async def get(
        self, collection: AsyncIOMotorCollection, email: EmailStr
    ) -> models.Usuario:
        return await super().get(collection, email, key="email")

    async def get_all(
        self, collection: AsyncIOMotorCollection, skip: int = 0, limit: int = 10
    ) -> List[models.Usuario]:
        return await super().get_all(collection, skip=skip, limit=limit)

    async def delete(self, collection: AsyncIOMotorCollection, email: EmailStr):
        return await super().delete(collection, email, key="email")

    async def remover_endereco(
        self, collection: AsyncIOMotorCollection, endereco: models.Endereco, email
    ):
        updated = await collection.update_one(
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


class ProductAdapter(BaseAdapter):
    async def create(
        self, collection: AsyncIOMotorCollection, data: models.Produto
    ) -> models.Produto:
        return await super().create(collection, data)

    async def get(
        self, collection: AsyncIOMotorCollection, id_produto: int
    ) -> models.Produto:
        return await super().get(collection, id_produto, key="id")

    async def delete(self, collection: AsyncIOMotorCollection, id_produto: int):
        return await super().delete(collection, id_produto, key="id")
