from typing import Optional
from sqlmodel import Field, SQLModel, Relationship
from pydantic import EmailStr

# Classe representando os dados do cliente
class Usuario(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nome: str
    email: EmailStr = Field(unique=True)
    senha: str = Field(min_length=3)

    enderecos: list["Endereco"] = Relationship()

class Endereco(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    rua: str
    cep: str
    cidade: str
    estado: str

    usuario_id: int = Field(foreign_key="usuario.id")
    usuario: Optional[Usuario] = Relationship()
    


