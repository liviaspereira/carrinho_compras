from fastapi import Depends, FastAPI, HTTPException
from pydantic import EmailStr
from sqlalchemy.exc import IntegrityError, NoResultFound
from fastapi.encoders import jsonable_encoder
from carrinho import models
import logging
from carrinho.db.postgres_adapter import (AddressAdapter, ProductAdapter,
                                          UserAdapter, get_address_adapter,
                                          get_product_adapter,
                                          get_user_adapter)
from carrinho.db.postgres_db import create_db_and_tables
from carrinho.schemas import Endereco, Produto, Usuario

app = FastAPI()

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

@app.post("/usuario/", status_code=201, response_model=Usuario)
async def criar_usuário(
    usuario: Usuario,
    adapter: UserAdapter = Depends(get_user_adapter),
):
    logger.info("Tentando criar cliente")
    try:
        return await adapter.create(usuario)
    except IntegrityError:
        raise HTTPException(status_code=409, detail="Usuário já existe")

    except Exception:
        raise HTTPException(status_code=400, detail="Falha ao inserir")


@app.get("/usuario/{email}/", response_model=Usuario)
async def retornar_usuario(
    email: EmailStr,
    adapter: UserAdapter = Depends(get_user_adapter),
):
    try:
        return await adapter.get(email)

    except NoResultFound:
        raise HTTPException(status_code=404, detail="Usuário não encontado")
    except Exception:
        raise HTTPException(status_code=400, detail="Falha ao inserir")


@app.delete("/usuario/", status_code=204)
async def deletar_usuario(
    email: EmailStr,
    adapter: UserAdapter = Depends(get_user_adapter),
):
    try:
        await adapter.delete(email)
    except Exception as e:
        breakpoint()
        raise HTTPException(status_code=400, detail="Falha ao deletar")


@app.post("/endereco/", status_code=201, response_model=models.Endereco)
async def criar_endereco(
    email: EmailStr,
    endereco: models.Endereco,
    adapter: AddressAdapter = Depends(get_address_adapter),
):
    try:
        return await adapter.create(email, endereco)

    except NoResultFound:
        raise HTTPException(status_code=404, detail="Usuário não encontado")
    except Exception:
        raise HTTPException(status_code=400, detail="Falha ao inserir")


@app.delete("/endereco/")
async def deletar_endereco(
    endereco: models.Endereco,
    email: EmailStr,
    adapter: AddressAdapter = Depends(get_address_adapter),
):
    try:
        await adapter.delete(email, endereco)
    except NoResultFound:
        raise HTTPException(status_code=404, detail="Endereço não encontado")
    except Exception:
        raise HTTPException(status_code=400, detail="Falha ao deletar")


@app.post(
    "/produto/", status_code=201, response_model=Produto
)  # pega o retorno da função e converte para um models.Produto
async def criar_produto(
    produto: Produto,
    adapter: ProductAdapter = Depends(get_product_adapter),
):
    try:
        return await adapter.create(produto)
    except Exception:
        raise HTTPException(status_code=400, detail="Falha ao inserir")


@app.get("/produto/{id_produto}/", response_model=Produto)
async def retornar_produto(
    id_produto: int,
    adapter: ProductAdapter = Depends(get_product_adapter),
):
    try:
        return await adapter.get(id_produto)

    except NoResultFound:
        raise HTTPException(status_code=404, detail="Produto não encontado")
    except Exception:
        raise HTTPException(status_code=400, detail="Falha ao buscar")


@app.get("/produto/", response_model=Produto)
async def filtrar_produto(
    produto: models.ProdutoFilter,
    adapter: ProductAdapter = Depends(get_product_adapter),
):
    try:
        return await adapter.filter(**produto.dict(exclude_none=True))
    except NoResultFound:
        raise HTTPException(status_code=404, detail="Produto não encontado")
    except Exception:
        raise HTTPException(status_code=400, detail="Falha ao buscar")


@app.delete("/produto/{id_produto}/")
async def deletar_produto(
    id_produto: int,
    adapter: ProductAdapter = Depends(get_product_adapter),
):
    try:
        await adapter.delete(id_produto)
    except NoResultFound:
        raise HTTPException(status_code=404, detail="Produto não encontado")
    except Exception:
        raise HTTPException(status_code=400, detail="Falha ao deletar")


@app.patch("/produto/{produto_id}", response_model=Produto)   
async def update(produto_id: int, produto: models.ProdutoFilter, adapter: ProductAdapter = Depends(get_product_adapter)
):
    try:
        return await adapter.update(produto_id, produto)
    except NoResultFound:
        raise HTTPException(status_code=404, detail="Produto não encontado")
    except Exception:
        raise HTTPException(status_code=400, detail="Falha ao atualizar")
    


# # Se não existir usuário com o id_usuario ou id_produto retornar falha,
# # se não existir um carrinho vinculado ao usuário, crie o carrinho
# # e retornar OK
# # senão adiciona produto ao carrinho e retornar OK
# @app.post("/carrinho/{id_usuario}/{id_produto}/")
# async def adicionar_carrinho(id_usuario: int, id_produto: int):
#     if id_usuario not in db_usuarios:
#         return FALHA
#     if id_produto not in db_produtos:
#         return FALHA

#     if id_usuario not in db_carrinhos:
#         carrinho_compras = models.CarrinhoDeCompras(
#             id_usuario=id_usuario,
#             id_produtos=[db_produtos[id_produto]],
#             preco_total=db_produtos[id_produto].preco,
#             quantidade_de_produtos=1,
#         )
#         db_carrinhos[id_usuario] = carrinho_compras
#     else:
#         db_carrinhos[id_usuario].id_produtos.append(db_produtos[id_produto])
#         db_carrinhos[id_usuario].preco_total += db_produtos[id_produto].preco
#         db_carrinhos[id_usuario].quantidade_de_produtos += 1
#     return OK


# # Se não existir carrinho com o id_usuario retornar falha,
# # senão retorna o carrinho de compras.
# @app.get("/carrinho/{id_usuario}/")
# async def retornar_carrinho(id_usuario: int):
#     if id_usuario not in db_carrinhos:
#         return FALHA
#     return db_carrinhos[id_usuario]


# # Se não existir carrinho com o id_usuario retornar falha,
# # senão retorna o o número de itens e o valor total do carrinho de compras.
# @app.get("/carrinho/{id_usuario}/total")
# async def retornar_total_carrinho(id_usuario: int):
#     if id_usuario not in db_carrinhos:
#         return FALHA

#     return (
#         db_carrinhos[id_usuario].preco_total,
#         db_carrinhos[id_usuario].quantidade_de_produtos,
#     )


# # Se não existir usuário com o id_usuario retornar falha,
# # senão deleta o carrinho correspondente ao id_usuario e retornar OK
# @app.delete("/carrinho/{id_usuario}/")
# async def deletar_carrinho(id_usuario: int):
#     if id_usuario not in db_usuarios:
#         return FALHA
#     del db_carrinhos[id_usuario]
#     return OK


@app.get("/")
async def bem_vinda():
    site = "Seja bem vinda"
    return site.replace("\n", "")


@app.on_event("startup")
def on_startup():
    create_db_and_tables()
