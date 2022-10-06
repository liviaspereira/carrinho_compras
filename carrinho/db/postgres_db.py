from sqlmodel import create_engine, SQLModel, Session
from os import environ

db_url = environ.get("DATABASE_URI")
engine = create_engine(db_url)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


