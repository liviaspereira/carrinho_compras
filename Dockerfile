FROM python:3.10.7-bullseye
WORKDIR /code
COPY ./requeriments.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
COPY ./carrinho /code/carrinho
CMD ["uvicorn", "carrinho.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]