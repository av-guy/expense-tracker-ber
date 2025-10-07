# pylint: disable=redefined-outer-name
# pylint: disable=unused-argument
# pylint: disable=unused-import
# pylint: disable=wrong-import-order

from typing import Any
from pytest import mark, raises
from datetime import datetime, timedelta

from .utils import test_expense, override_get_db
from src.expense_tracker.models import Expense


def stringify_task(expense: Expense):
    return (
        f"Expense(id={expense.id!r}, description={expense.description!r},"
        f"category={expense.category!r}, amount={expense.amount!r}, date={expense.date!r})"
    )


def test_task_repr(test_expense):
    task_str = repr(test_expense)
    assert task_str == stringify_task(test_expense)
