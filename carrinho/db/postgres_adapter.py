from carrinho.db.base import BaseAdapter
from sqlmodel import SQLModel, select
from typing import Any
from pydantic import EmailStr

from carrinho.schemas import Usuario, Endereco
from carrinho import models

class PostgresBaseAdapter(BaseAdapter):
    def __init__(self, session):
        self.session = session
        self.type = SQLModel


    async def create(self, data: SQLModel) -> SQLModel:
        self.session.add(data)

        self.session.commit()

    async def update(
        self,
        data: SQLModel,
        id: Any,
        key: str,
        update_key: str,
    ) -> SQLModel:
        pass

    async def get(self, id: Any, key:str) -> SQLModel:
        statement = select(self.type).where(self.type )
        results = self.session.exec(statement)
        usuario = results.one()


    async def get_all(self, skip: int = 0, limit: int = 10) -> list[SQLModel]:
        pass

    async def delete(self, id: Any, key: str):
        pass


class UserAdapter(PostgresBaseAdapter):
    def __init__(self, session):
        self.session = session
        self.type = Usuario

    async def get(self, email:EmailStr) -> Usuario:
        statement = select(Usuario).where(Usuario.email == email)
        results = self.session.exec(statement)
        usuario = results.one()
        return usuario

    async def get_all(self) -> list[Usuario]:
        statement = select(Usuario)
        results = self.session.exec(statement)
        usuarios = results.all()
        return usuarios

    async def delete(self, email:EmailStr):
        statement = select(Usuario).where(Usuario.email == email)
        results = self.session.exec(statement)
        usuario = results.one()

        self.session.delete(usuario)
        self.session.commit()


class AddressAdapter(PostgresBaseAdapter):
    def __init__(self, session):
        self.session = session

    async def create(self, email: EmailStr, endereco: models.Endereco) -> Endereco:
        statement = select(Usuario).where(Usuario.email == email)
        results = self.session.exec(statement) # roda o select
        usuario = results.one()
        endereco = Endereco(usuario_id=usuario.id, rua=endereco.rua, cep=endereco.cep, cidade=endereco.cidade, estado=endereco.estado) # ou endereco = Endereco(usuario_id=usuario.id, **endereco.dict())
        self.session.add(endereco)
        self.session.commit()
        return endereco

    async def delete(self, email:EmailStr):
        statement = select(Usuario).where(Usuario.email == email)
        results = self.session.exec(statement)
        usuario = results.one()

        self.session.delete(usuario)
        self.session.commit()
