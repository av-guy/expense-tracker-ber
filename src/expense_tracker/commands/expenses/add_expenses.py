# pylint: disable=not-callable

from pathlib import Path
from typing import Annotated
from datetime import datetime

from kink import di
from typer import Argument, Option, Exit
from rich import print as rich_print

from ...models import Expense
from ...protocols import ExpenseRepository, ExpenseCSVService

from .command_router import app


EXPENSE_DESCRIPTION = Annotated[
    str,
    Argument(
        help="A brief description of the expense."
    )
]

EXPENSE_AMOUNT = Annotated[
    float,
    Argument(
        help="The amount of the expense.",
        min=1
    )
]

EXPENSE_CATEGORY = Annotated[
    str,
    Option(
        "--category",
        "-c",
        help="Optional category for the expense."
    )
]

EXPENSE_NOTES = Annotated[
    str,
    Option(
        "--notes",
        "-n",
        help="Optional notes about the expense."
    )
]

BULK_FILE_PATH = Annotated[
    Path,
    Argument(
        help="Path to CSV file for bulk import."
    )
]


@app.command("add")
def add_expense(
    description: EXPENSE_DESCRIPTION,
    amount: EXPENSE_AMOUNT,
    category: EXPENSE_CATEGORY = "",
    notes: EXPENSE_NOTES = "",
):
    """Add a single expense."""
    repo: ExpenseRepository = di[ExpenseRepository]

    expense = Expense(
        description=description,
        amount=amount,
        category=category,
        notes=notes,
        date=datetime.now(),
    )

    created_id = repo.add(expense)
    rich_print(f"\n[green]Expense added with ID {created_id}[/green]\n")


@app.command("bulk")
def bulk_import(file: BULK_FILE_PATH):
    """Import multiple expenses from a CSV file."""
    repo: ExpenseRepository = di[ExpenseRepository]
    csv_service: ExpenseCSVService = di[ExpenseCSVService]

    try:
        expenses = csv_service.import_expenses(file)
    except (FileNotFoundError, ValueError, Exception) as exc:
        rich_print(f"\n[red]{exc}[/red]\n")
        raise Exit(code=2)

    added_count = repo.bulk_import(expenses)
    rich_print(
        f"\n[green]{added_count} expenses added from {file.name}[/green]\n")
