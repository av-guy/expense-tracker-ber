# pylint: disable=not-callable

from typing import Sequence, Optional, Callable
from contextlib import AbstractContextManager

from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from kink import inject

from ..models import Expense
from ..protocols import ExpenseRepository


@inject(alias=ExpenseRepository)
class SQLAlchemyExpenseRepository:
    def __init__(self, db_session_context: Callable[[
    ], AbstractContextManager[Session]]) -> None:
        self._db_context = db_session_context

    def _expense_id_check(self, expense_id: int) -> None:
        if not isinstance(expense_id, int):
            raise ValueError("Task ID must be an integer.")

        if expense_id < 1:
            raise ValueError("Task ID must be greater than 0.")

    def _expense_type_check(self, expense: Expense) -> None:
        if not isinstance(expense, Expense):
            raise TypeError("`expense` must be of type Expense.")

    def get(self, expense_id: int) -> Expense | None:
        self._expense_id_check(expense_id)

        with self._db_context() as db:
            return db.get(Expense, expense_id)

    def add(self, expense: Expense) -> int | None:
        self._expense_type_check(expense)

        with self._db_context() as db:
            db.add(expense)
            db.commit()
            return expense.id

    def bulk_import(self, expenses: Sequence[Expense]) -> int:
        added_count = 0

        with self._db_context() as db:
            for expense in expenses:
                self._expense_type_check(expense)
                db.add(expense)
                added_count += 1

            db.commit()

        return added_count

    def category_summary(
        self,
        category: Optional[str] = None
    ) -> tuple[float, int]:
        if category is not None and not isinstance(category, str):
            raise TypeError('`category` must be a `str` or None')

        with self._db_context() as db:
            query = db.query(func.sum(Expense.amount), func.count())

            if category:
                category = category.lower().capitalize()
                query = query.filter(Expense.category == category)

            total, count = 0.0, 0

            if (values := query.first()) is not None:
                total, count = values
                total = total or 0.0

            return total, count

    def delete(self, task: Expense) -> None:
        self._expense_type_check(task)

        with self._db_context() as db:
            db.delete(task)
            db.commit()

    def update(self, expense: Expense) -> None:
        self._expense_type_check(expense)

        with self._db_context() as db:
            old_expense = db.get(Expense, expense.id)

            if old_expense is not None:
                old_expense.category = expense.category
                old_expense.description = expense.description
                old_expense.amount = expense.amount
                old_expense.date = expense.date
                old_expense.notes = expense.notes

            db.commit()

    def list(self, category: Optional[str] = None) -> Sequence[Expense]:
        if category is not None and not isinstance(category, str):
            raise TypeError('`category` must be a `str` or None')

        with self._db_context() as db:
            query = db.query(Expense)

            if category is not None:
                category = category.lower().capitalize()
                query = query.filter(Expense.category == category)

            return query.all()

    def monthly_summary(self, month: int, year: int) -> Sequence[Expense]:
        if not isinstance(month, int):
            raise ValueError("`month` must be type `int`.")

        if not isinstance(year, int):
            raise ValueError("`year` must be type `int`.")

        if not 1 <= month <= 12:
            raise ValueError("`month` must be between 1 and 12")

        with self._db_context() as db:
            expenses = (
                db.query(Expense)
                .filter(extract("year", Expense.date) == year)
                .filter(extract("month", Expense.date) == month)
                .all()
            )

            return expenses
