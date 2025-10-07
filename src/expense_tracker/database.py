from contextlib import contextmanager
from kink import di

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base


ENGINE = create_engine(di["db_url"])
SESSION_LOCAL = sessionmaker(autocommit=False, autoflush=False, bind=ENGINE)
BASE = declarative_base()


@contextmanager
def get_db():
    db = SESSION_LOCAL()

    try:
        yield db
    finally:
        db.close()
