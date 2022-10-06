from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field
from decimal import Decimal

# Classe representando os dados do endereço do cliente
class Endereco(BaseModel):
    rua: str
    cep: str
    cidade: str
    estado: str


# Classe representando os dados do cliente
class Usuario(BaseModel):
    nome: str
    endereco: Optional[List[Endereco]] = Field(default_factory=list)
    email: EmailStr
    senha: str = Field(min_length=3)


# Classe representando os dados do produto
class Produto(BaseModel):
    id: int = Field(unique=True, index=True)
    nome: str
    descricao: str
    preco: Decimal = Field(max_digits=10, decimal_places=2)


# Classe representando o carrinho de compras de um cliente com uma lista de produtos
class CarrinhoDeCompras(BaseModel):

    id_usuario: int = Field(unique=True, index=True)

    id_produtos: List[Produto] = Field(default_factory=list)

    preco_total: float
    quantidade_de_produtos: int
