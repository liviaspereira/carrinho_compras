from typing import Any

from fastapi import Depends
from pydantic import EmailStr
from sqlmodel import Session, SQLModel, select

from carrinho import models
from carrinho.db.base import BaseAdapter
from carrinho.db.postgres_db import get_session
from carrinho.schemas import Endereco, Produto, Usuario


class PostgresBaseAdapter(BaseAdapter):
    def __init__(self, session):
        self.session = session
        self.type = SQLModel

    async def create(self, data: SQLModel) -> SQLModel:
        self.session.add(data.dict(exclude_none=True))

        self.session.commit()

    async def update(
        self,
        data: SQLModel,
        id: Any,
        key: str,
        update_key: str,
    ) -> SQLModel:
        pass

    async def get(self, id: Any, key: str) -> SQLModel:
        statement = select(self.type).where(self.type)
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

    async def create(self, data: Usuario) -> Usuario:
        usuario = Usuario(**data.dict(exclude_none=True))
        self.session.add(usuario)

        self.session.commit()
        self.session.refresh(usuario)
        return usuario

    async def get(self, email: EmailStr) -> Usuario:
        statement = select(Usuario).where(Usuario.email == email)
        results = self.session.exec(statement)
        usuario = results.one()
        return usuario

    async def get_all(self) -> list[Usuario]:
        statement = select(Usuario)
        results = self.session.exec(statement)
        usuarios = results.all()
        return usuarios

    async def delete(self, email: EmailStr):
        statement = select(Usuario).where(Usuario.email == email)
        results = self.session.exec(statement)
        usuario = results.one()
        statement = (
            select(Endereco)
            .where(
                Endereco.usuario_id == usuario.id,
            ))
        results = self.session.exec(statement)
        enderecos = results.all()
        for endereco in enderecos:
            self.session.delete(endereco)
        self.session.delete(usuario)
        self.session.commit()


class AddressAdapter(PostgresBaseAdapter):
    def __init__(self, session):
        self.session = session

    async def create(self, email: EmailStr, endereco: models.Endereco) -> Endereco:
        statement = select(Usuario).where(Usuario.email == email)
        results = self.session.exec(statement)  # roda o select
        usuario = results.one()
        endereco = Endereco(
            usuario_id=usuario.id,
            rua=endereco.rua,
            cep=endereco.cep,
            cidade=endereco.cidade,
            estado=endereco.estado,
        )  # ou endereco = Endereco(usuario_id=usuario.id, **endereco.dict())
        self.session.add(endereco)
        self.session.commit()
        self.session.refresh(endereco)
        return endereco

    async def delete(self, email: EmailStr, endereco: models.Endereco):
        statement = (
            select(Endereco)
            .join(Usuario)
            .where(
                Endereco.cep == endereco.cep,
                Endereco.cidade == endereco.cidade,
                Endereco.estado == endereco.estado,
                Endereco.usuario_id == Usuario.id,
                Usuario.email == email,
            )
        )
        results = self.session.exec(statement)
        endereco = results.one()

        self.session.delete(endereco)
        self.session.commit()


class ProductAdapter(PostgresBaseAdapter):
    def __init__(self, session):
        self.session = session
        self.type = Produto

    async def create(self, data: Produto) -> Produto:
        produto = Produto(**data.dict(exclude_none=True))
        self.session.add(produto)

        self.session.commit()
        self.session.refresh(produto)
        return produto

    async def get(self, id: int) -> Produto:
        statement = select(Produto).where(Produto.id == id)
        results = self.session.exec(statement)
        produto = results.one()
        return produto

    async def filter(self, **kwargs: dict[str, str]) -> Produto:
        statement = select(Produto)
        for key, value in kwargs.items():
            statement = statement.where(
                getattr(Produto, key) == value
            )  # where(Produto.key == value)
        results = self.session.exec(statement)
        produto = results.one()
        return produto
    
    async def delete(self, id: int):
        statement = select(Produto).where(Produto.id == id)
        results = self.session.exec(statement)
        produto = results.one()
    
        self.session.delete(produto)
        self.session.commit()


    async def update(self, id: int, data: models.ProdutoFilter) -> Produto: # data = aos produtos novos
        statement = select(Produto).where(Produto.id == id)
        results = self.session.exec(statement)
        produto = results.one()
        update_data = data.dict(exclude_none=True)
        for key, value in update_data.items():
            setattr(produto, key, value)
        self.session.add(produto)
        self.session.commit()

        self.session.refresh(produto)
        return produto
        

async def get_user_adapter(session: Session = Depends(get_session)) -> UserAdapter:
    user_adapter = UserAdapter(session)
    return user_adapter


async def get_address_adapter(
    session: Session = Depends(get_session),
) -> AddressAdapter:
    address_adapter = AddressAdapter(session)
    return address_adapter


async def get_product_adapter(
    session: Session = Depends(get_session),
) -> ProductAdapter:
    product_adapter = ProductAdapter(session)
    return product_adapter