from pymongo.errors import PyMongoError
from fastapi import FastAPI, Depends, HTTPException
import models
from database import DataBase, get_db
from mongo_adapter import (
    ProductAdapter,
    UserAdapter,
    ObjetoNaoModificado,
    ObjetoNaoEncontrado,
)
from pydantic import EmailStr

app = FastAPI()

OK = "OK"
FALHA = "FALHA"

@app.post("/usuario/", status_code=201, response_model=models.Usuario)
async def criar_usuário(
    usuario: models.Usuario,
    adapter: UserAdapter = Depends(UserAdapter),
    db: DataBase = Depends(get_db),
):
    try:
        return await adapter.create(db.users_collection, usuario)
    except Exception as e:
        raise HTTPException(status_code=400, detail="Falha ao inserir")


@app.get("/usuario/{email}/", response_model=models.Usuario)
async def retornar_usuario(
    email: EmailStr,
    adapter: UserAdapter = Depends(UserAdapter),
    db: DataBase = Depends(get_db),
):
    usuario = await adapter.get(db.users_collection, email)
    if usuario is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return usuario


@app.delete("/usuario/", status_code=204)
async def deletar_usuario(
    email: EmailStr,
    adapter: UserAdapter = Depends(UserAdapter),
    db: DataBase = Depends(get_db),
):
    try:
        is_deleted = await adapter.delete(db.users_collection, email)
        if not is_deleted:
            raise HTTPException(status_code=400, detail="Usuário não existe")
    except PyMongoError:
        raise HTTPException(status_code=400, detail="Falha ao deletar")


@app.post("/endereco/", status_code=201, response_model=models.Endereco)
async def criar_endereco(
    email: EmailStr,
    endereco: models.Endereco,
    adapter: UserAdapter = Depends(UserAdapter),
    db: DataBase = Depends(get_db),
):
    try:
        return await adapter.create_addr(db.users_collection, email, endereco)

    except ObjetoNaoEncontrado:
        raise HTTPException(status_code=404, detail="Usuário não encontado")
    except ObjetoNaoModificado:
        raise HTTPException(status_code=200, detail="Nada foi modificados")
    except Exception:
        raise HTTPException(status_code=400, detail="Falha ao inserir")


@app.delete("/endereco/")
async def deletar_endereco(
    endereco: models.Endereco,
    email: EmailStr,
    adapter: UserAdapter = Depends(UserAdapter),
    db: DataBase = Depends(get_db),
):
    try:
        is_deleted = await adapter.remover_endereco(
            db.users_collection, endereco, email
        )
        if not is_deleted:
            raise HTTPException(status_code=400, detail="Endereço não existe")
    except PyMongoError as e:
        raise HTTPException(status_code=400, detail="Falha ao deletar")


@app.post(
    "/produto/", status_code=201, response_model=models.Produto
)  # pega o retorno da função e converte para um models.Usuario
async def criar_produto(
    produto: models.Produto,
    adapter: ProductAdapter = Depends(ProductAdapter),
    db: DataBase = Depends(get_db),
):
    try:
        return await adapter.create(db.product_collection, produto)
    except Exception as e:
        raise HTTPException(status_code=400, detail="Falha ao inserir")


@app.get("/produto/{id_produto}/", response_model=models.Produto)
async def retornar_produto(
    id_produto: int,
    adapter: ProductAdapter = Depends(ProductAdapter),
    db: DataBase = Depends(get_db),
):
    produto = await adapter.get(db.product_collection, id_produto)
    if produto is None:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    return produto


@app.delete("/produto/{id_produto}/", response_model=models.Produto)
async def deletar_produto(
    id_produto: int,
    adapter: ProductAdapter = Depends(ProductAdapter),
    db: DataBase = Depends(get_db),
):
    try:
        is_deleted = await adapter.delete(db.product_collection, id_produto)
        if not is_deleted:
            raise HTTPException(status_code=400, detail="Produto não existe")
    except PyMongoError:
        raise HTTPException(status_code=400, detail="Falha ao deletar")


# Se não existir usuário com o id_usuario ou id_produto retornar falha,
# se não existir um carrinho vinculado ao usuário, crie o carrinho
# e retornar OK
# senão adiciona produto ao carrinho e retornar OK
@app.post("/carrinho/{id_usuario}/{id_produto}/")
async def adicionar_carrinho(id_usuario: int, id_produto: int):
    if id_usuario not in db_usuarios:
        return FALHA
    if id_produto not in db_produtos:
        return FALHA

    if id_usuario not in db_carrinhos:
        carrinho_compras = models.CarrinhoDeCompras(
            id_usuario=id_usuario,
            id_produtos=[db_produtos[id_produto]],
            preco_total=db_produtos[id_produto].preco,
            quantidade_de_produtos=1,
        )
        db_carrinhos[id_usuario] = carrinho_compras
    else:
        db_carrinhos[id_usuario].id_produtos.append(db_produtos[id_produto])
        db_carrinhos[id_usuario].preco_total += db_produtos[id_produto].preco
        db_carrinhos[id_usuario].quantidade_de_produtos += 1
    return OK


# Se não existir carrinho com o id_usuario retornar falha,
# senão retorna o carrinho de compras.
@app.get("/carrinho/{id_usuario}/")
async def retornar_carrinho(id_usuario: int):
    if id_usuario not in db_carrinhos:
        return FALHA
    return db_carrinhos[id_usuario]


# Se não existir carrinho com o id_usuario retornar falha,
# senão retorna o o número de itens e o valor total do carrinho de compras.
@app.get("/carrinho/{id_usuario}/total")
async def retornar_total_carrinho(id_usuario: int):
    if id_usuario not in db_carrinhos:
        return FALHA

    return (
        db_carrinhos[id_usuario].preco_total,
        db_carrinhos[id_usuario].quantidade_de_produtos,
    )


# Se não existir usuário com o id_usuario retornar falha,
# senão deleta o carrinho correspondente ao id_usuario e retornar OK
@app.delete("/carrinho/{id_usuario}/")
async def deletar_carrinho(id_usuario: int):
    if id_usuario not in db_usuarios:
        return FALHA
    del db_carrinhos[id_usuario]
    return OK


@app.get("/")
async def bem_vinda():
    site = "Seja bem vinda"
    return site.replace("\n", "")
