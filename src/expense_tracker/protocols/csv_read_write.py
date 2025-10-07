from typing import Protocol, Optional, Sequence
from pathlib import Path
from datetime import datetime

from ..models import Expense


class ExpenseCSVService(Protocol):
    def export_expenses(
        self,
        expenses: Sequence[Expense],
        directory: Path,
        filename: Optional[str] = None,
    ) -> None: ...

    def export_summary(
        self,
        category: Optional[str],
        total: float,
        count: int,
        directory: Path,
        filename: Optional[str] = None,
        exported_on: Optional[datetime] = None,
    ) -> None: ...

    def export_monthly_summary(
        self,
        expenses: Sequence[Expense],
        total: float,
        year: int,
        month: int,
        directory: Path,
        filename: Optional[str] = None,
    ) -> None: ...

    def import_expenses(self, file: Path) -> Sequence[Expense]: ...
