from typing import Optional

from pydantic import EmailStr, condecimal
from sqlmodel import Field, Relationship, SQLModel


# Classe representando os dados do cliente
class Usuario(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nome: str
    email: EmailStr = Field(unique=True)
    senha: str = Field(min_length=3)

    enderecos: list["Endereco"] = Relationship(back_populates="usuario")


class Endereco(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    rua: str
    cep: str
    cidade: str
    estado: str

    usuario_id: int = Field(foreign_key="usuario.id")
    usuario: Optional[Usuario] = Relationship(back_populates="enderecos")


class Produto(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nome: str
    descricao: str
    marca: str
    tamanho: int
    cor: str
    preco: condecimal(max_digits=10, decimal_places=2)
