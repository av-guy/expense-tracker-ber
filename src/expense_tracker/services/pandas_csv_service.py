from pathlib import Path
from datetime import datetime
from typing import Optional, Sequence
from kink import inject

import pandas as pd
from ..models import Expense
from ..protocols import ExpenseCSVService


@inject(alias=ExpenseCSVService)
class PandasCSVService:
    def export_expenses(
        self,
        expenses: list[Expense],
        directory: Path,
        filename: Optional[str] = None,
    ) -> None:
        directory.mkdir(parents=True, exist_ok=True)

        if not filename:
            timestamp = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
            filename = f"expenses_{timestamp}"

        filename = f"{filename}.csv"
        export_path = directory / filename

        data = [
            {
                "ID": e.id,
                "Description": e.description,
                "Category": e.category or "",
                "Amount": e.amount,
                "Date": e.date.strftime("%Y-%m-%d"),
                "Notes": e.notes or "",
            }
            for e in expenses
        ]

        pd.DataFrame(data).to_csv(export_path, index=False)

    def export_summary(
        self,
        category: Optional[str],
        total: float,
        count: int,
        directory: Path,
        filename: Optional[str] = None,
        exported_on: Optional[datetime] = None,
    ) -> None:
        directory.mkdir(parents=True, exist_ok=True)

        if not filename:
            timestamp = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
            filename = f"summary_{timestamp}"

        filename = f"{filename}.csv"
        export_path = directory / filename

        data = [
            {
                "Category": category or "All",
                "Total": total,
                "Entries": count,
                "Exported On": (exported_on or datetime.now()).strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
            }
        ]

        pd.DataFrame(data).to_csv(export_path, index=False)

    def export_monthly_summary(
        self,
        expenses: list[Expense],
        total: float,
        year: int,
        month: int,
        directory: Path,
        filename: Optional[str] = None,
    ) -> None:
        directory.mkdir(parents=True, exist_ok=True)

        if not filename:
            timestamp = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
            filename = f"monthly_{year}_{month:02d}_{timestamp}"

        filename = f"{filename}.csv"
        export_path = directory / filename

        df = pd.DataFrame(
            [
                {
                    "ID": e.id,
                    "Description": e.description,
                    "Category": e.category or "",
                    "Amount": e.amount,
                    "Date": e.date.strftime("%Y-%m-%d"),
                }
                for e in expenses
            ]
        )

        df.loc[len(df)] = {"ID": "", "Description": "Total", "Amount": total}
        df.to_csv(export_path, index=False)

    def import_expenses(self, file: Path) -> Sequence[Expense]:
        expenses = []

        if not file.exists():
            raise FileNotFoundError(f"Could not locate file at {file}.")

        df = pd.read_csv(file)

        required_columns = {"description", "amount"}
        lower_columns = {col.lower(): col for col in df.columns}

        if not required_columns.issubset(lower_columns.keys()):
            raise ValueError(
                f"File must contain required columns: {",".join(required_columns)}")

        for _, row in df.iterrows():
            expense = Expense(
                description=row.get(lower_columns.get("description")),
                amount=float(row.get(lower_columns.get("amount")) or 0.0),
                category=row.get(lower_columns.get("category"))
                if "category" in lower_columns
                else None,
                notes=row.get(lower_columns.get("notes"))
                if "notes" in lower_columns
                else None,
                date=datetime.now(),
            )
            expenses.append(expense)

        return expenses
