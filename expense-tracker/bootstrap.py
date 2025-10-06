# pylint: disable=import-outside-toplevel

from os import getenv
from kink import di

DEFAULT_DB_URL = "sqlite:///./expense_db.db"
di["db_url"] = getenv("DATABASE_URL", DEFAULT_DB_URL)


def initialize():
    from .database import get_db, BASE, ENGINE
    BASE.metadata.create_all(bind=ENGINE)
    di["db_session_context"] = get_db
