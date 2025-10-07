from typing import Protocol, Optional, Sequence
from ..models import Expense


class ExpenseRepository(Protocol):
    def get(self, expense_id: int) -> Expense | None:
        ...

    def add(self, expense: Expense) -> int:
        ...

    def bulk_import(self, expenses: Sequence[Expense]) -> None:
        ...

    def delete(self, expense: Expense) -> None:
        ...

    def update(
        self,
        expense: Expense
    ) -> Optional[Expense]:
        ...

    def list(
            self, category: Optional[str] = None) -> Sequence[Expense]:
        ...

    def category_summary(
            self, category: Optional[str] = None) -> tuple[float, int]:
        ...

    def monthly_summary(self, month: int, year: int) -> Sequence[Expense]:
        ...
