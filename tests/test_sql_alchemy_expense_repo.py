# pylint: disable=redefined-outer-name
# pylint: disable=unused-argument
# pylint: disable=unused-import
# pylint: disable=wrong-import-order

from typing import Any
from pytest import mark, raises
from datetime import datetime
from kink import di

from .utils import test_expense, override_get_db

from src.expense_tracker.repositories import SQLAlchemyExpenseRepository
from src.expense_tracker.protocols import ExpenseRepository
from src.expense_tracker.models import Expense


def test_get_expense(test_expense: Expense):
    repository = di[ExpenseRepository]
    expense_item = repository.get(test_expense.id)

    assert expense_item is not None
    assert expense_item.id == test_expense.id
    assert expense_item.description == test_expense.description
    assert expense_item.amount == test_expense.amount
    assert expense_item.category == test_expense.category


@mark.parametrize("expense_id, exc_type", [
    ("not_an_int", ValueError),
    (0, ValueError),
    (-1, ValueError),
])
def test_expense_id_check(expense_id: str | int, exc_type: Any):
    repository = di[ExpenseRepository]

    with raises(exc_type):
        repository.get(expense_id)      # type: ignore


def test_add_expense():
    repository = di[ExpenseRepository]

    expense = Expense(
        description="Dinner",
        amount=25.50,
        category="Food",
        notes="Dinner with friends",
        date=datetime.now(),
    )

    expense_id = repository.add(expense)
    assert expense_id is not None
    assert expense_id == 1

    with override_get_db() as db:
        db_expense = db.get(Expense, expense_id)
        assert db_expense is not None
        assert db_expense.id == 1
        assert db_expense.description == "Dinner"
        assert db_expense.amount == 25.50
        assert db_expense.category == "Food"


def test_delete_expense(test_expense: Expense):
    repository = di[ExpenseRepository]

    with override_get_db() as db:
        expense = db.get(Expense, test_expense.id)
        assert expense is not None

    repository.delete(expense)

    with override_get_db() as db:
        expense = db.get(Expense, test_expense.id)
        assert expense is None


def test_update_expense(test_expense: Expense):
    repository = di[ExpenseRepository]

    with override_get_db() as db:
        expense = db.get(Expense, test_expense.id)
        assert expense is not None

        expense.description = "Updated Description"
        expense.amount = 50.75
        expense.category = "Entertainment"
        expense.notes = "Updated notes"

    repository.update(expense)

    with override_get_db() as db:
        updated = db.get(Expense, test_expense.id)
        assert updated is not None
        assert updated.description == "Updated Description"
        assert updated.amount == 50.75
        assert updated.category == "Entertainment"
        assert updated.notes == "Updated notes"


def test_list_expenses(test_expense: Expense):
    repository = di[ExpenseRepository]
    expense_list = repository.list()

    assert expense_list
    assert all(isinstance(e, Expense) for e in expense_list)


def test_type_check():
    repository = di[ExpenseRepository]

    with raises(TypeError):
        repository.add(123)     # type: ignore

    with raises(TypeError):
        repository.delete(456)  # type: ignore


def test_bulk_import(test_expense: Expense):
    repository = di[ExpenseRepository]

    new_expenses = [
        Expense(description="Groceries", amount=100.0,
                category="Food", date=datetime.now()),
        Expense(description="Gym Membership", amount=45.0,
                category="Health", date=datetime.now()),
    ]

    repository.bulk_import(new_expenses)

    with override_get_db() as db:
        results = db.query(Expense).all()
        assert len(results) >= 2
        descriptions = [r.description for r in results]
        assert "Groceries" in descriptions
        assert "Gym Membership" in descriptions


def test_category_summary(test_expense: Expense):
    repository = di[ExpenseRepository]

    total, count = repository.category_summary(category="Food")
    assert isinstance(total, float)
    assert isinstance(count, int)
    assert count >= 0


def test_monthly_summary(test_expense: Expense):
    repository = di[ExpenseRepository]

    month = datetime.now().month
    year = datetime.now().year

    results = repository.monthly_summary(month, year)
    assert isinstance(results, list)
    assert all(isinstance(e, Expense) for e in results)


def test_list_type_check():
    repository = di[ExpenseRepository]

    with raises(TypeError):
        repository.list(category=123)  # type: ignore


def test_category_summary_type_check():
    repository = di[ExpenseRepository]

    with raises(TypeError):
        repository.category_summary(category=123)  # type: ignore


@mark.parametrize(
    "month, year, exc_type",
    [
        ("not_an_int", 2025, ValueError),
        (5, "not_an_int", ValueError),
        (0, 2025, ValueError),
        (13, 2025, ValueError),
    ],
)
def test_monthly_summary_invalid_inputs(month, year, exc_type):
    repository = di[ExpenseRepository]

    with raises(exc_type):
        repository.monthly_summary(month, year)  # type: ignore
