from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field, condecimal


# Classe representando os dados do endereço do cliente
class Endereco(BaseModel):
    rua: str
    cep: str
    cidade: str
    estado: str


# Classe representando os dados do cliente
class Usuario(BaseModel):
    nome: str
    enderecos: Optional[List[Endereco]] = Field(default_factory=list)
    email: EmailStr
    senha: str = Field(min_length=3)


# Classe representando os dados do produto
class ProdutoFilter(BaseModel):
    nome: Optional[str] = None
    descricao: Optional[str] = None
    marca: Optional[str] = None
    tamanho: Optional[int] = None
    cor: Optional[str] = None
    preco: Optional[condecimal(max_digits=10, decimal_places=2)] = None
