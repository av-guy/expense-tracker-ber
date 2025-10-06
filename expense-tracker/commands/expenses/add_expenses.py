# pylint: disable=not-callable

from pathlib import Path
from typing import Annotated, Callable
from contextlib import AbstractContextManager
from datetime import datetime

import pandas as pd

from kink import di
from typer import Argument, Option
from rich import print as rich_print
from sqlalchemy.orm import Session

from ...models import Expense
from .command_router import app


EXPENSE_DESCRIPTION = Annotated[
    str,
    Argument(help="A brief description of the expense.")
]

EXPENSE_AMOUNT = Annotated[
    float,
    Argument(help="The amount of the expense.")
]

EXPENSE_CATEGORY = Annotated[
    str,
    Option("--category", "-c", help="Optional category for the expense.")
]

EXPENSE_NOTES = Annotated[
    str,
    Option("--notes", "-n", help="Optional notes about the expense.")
]

BULK_FILE_PATH = Annotated[
    Path,
    Argument(
        help="Path to CSV file for bulk import."
    )
]


def _import_expenses_from_csv(db: Session, file: Path) -> int:
    """Import expenses from a CSV file and return the count of rows added."""
    if not file.exists():
        rich_print("")
        rich_print(f"[red]File not found: {file}[/red]")
        rich_print("")
        return 0

    try:
        df = pd.read_csv(file)
    except Exception as e:
        rich_print("")
        rich_print(f"[red]Error reading CSV: {e}[/red]")
        rich_print("")
        return 0

    required_columns = {"description", "amount"}
    lower_columns = {col.lower(): col for col in df.columns}

    if not required_columns.issubset(lower_columns.keys()):
        rich_print(
            "[red]CSV must include at least 'description' and 'amount' columns[/red]")
        return 0

    added_count = 0
    for _, row in df.iterrows():
        try:
            expense = Expense(
                description=row.get(lower_columns.get("description")),
                amount=float(row.get(lower_columns.get("amount")) or 0.0),
                category=row.get(lower_columns.get("category")
                                 ) if "category" in lower_columns else None,
                notes=row.get(lower_columns.get("notes")
                              ) if "notes" in lower_columns else None,
                date=datetime.now(),
            )
            db.add(expense)
            added_count += 1
        except Exception as e:
            rich_print(f"[yellow]Skipping invalid row: {e}[/yellow]")

    db.commit()
    return added_count


@app.command("add")
def add_expense(
    description: EXPENSE_DESCRIPTION,
    amount: EXPENSE_AMOUNT,
    category: EXPENSE_CATEGORY = "",
    notes: EXPENSE_NOTES = "",
):
    """Add a single expense."""
    db_session: Callable[[], AbstractContextManager[Session]
                         ] = di["db_session_context"]

    with db_session() as db:
        if not isinstance(db, Session):
            rich_print("\n[red]Invalid database session[/red]\n")
            return

        expense = Expense(
            description=description,
            amount=amount,
            category=category,
            notes=notes,
            date=datetime.now(),
        )

        db.add(expense)
        db.commit()
        rich_print(f"\n[green]Expense added with ID {expense.id}[/green]\n")


@app.command("bulk")
def bulk_import(file: BULK_FILE_PATH):
    """Import multiple expenses from a CSV file."""
    db_session: Callable[[], AbstractContextManager[Session]
                         ] = di["db_session_context"]

    with db_session() as db:
        if not isinstance(db, Session):
            rich_print("\n[red]Invalid database session[/red]\n")
            return

        added_count = _import_expenses_from_csv(db, file)

        if added_count:
            rich_print(
                f"\n[green]{added_count} expenses added from {file.name}[/green]\n")
