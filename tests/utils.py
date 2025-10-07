# pylint: disable=wrong-import-position
# pylint: disable=import-outside-toplevel
# pylint: disable=redefined-outer-name
# pylint: disable=reimported

from os import path
from pathlib import Path
from contextlib import contextmanager
from datetime import datetime

from pytest import fixture
from kink import di

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

SCRIPT_PATH = path.abspath(__file__)
SCRIPT_DIR = path.dirname(SCRIPT_PATH)

DB_PATH = Path(SCRIPT_DIR + "/db")
DB_PATH.mkdir(exist_ok=True)

SQLALCHEMY_DATABASE_URL = f"sqlite:///{SCRIPT_DIR}/db/test_db.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)

TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine)


@contextmanager
def override_get_db():
    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()


di["db_session_context"] = override_get_db
di["db_url"] = SQLALCHEMY_DATABASE_URL

# Dependency injection must happen before BASE and Task are imported.
# Both of these modules depend on the "db_url" and "db_session_context".
from src.expense_tracker.database import BASE
from src.expense_tracker.models import Expense

BASE.metadata.create_all(bind=engine)


@fixture
def test_expense():
    db = TestingSessionLocal()

    expense = Expense(
        description="Groceries",
        amount=42.75,
        category="Food",
        notes="Weekly grocery trip",
        date=datetime.now(),
    )

    db.add(expense)
    db.commit()

    yield expense

    with engine.connect() as connection:
        connection.execute(text("DELETE FROM expenses;"))
        connection.commit()
