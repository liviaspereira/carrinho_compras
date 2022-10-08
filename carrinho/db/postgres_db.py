from os import environ

from sqlmodel import Session, SQLModel, create_engine

db_url = environ.get("DATABASE_URI")
engine = create_engine(db_url)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
