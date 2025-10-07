from typing import Annotated

from kink import di
from typer import Argument, Option, Exit
from rich import print as rich_print

from ...protocols import ExpenseRepository
from .command_router import app


EXPENSE_ID = Annotated[
    int,
    Argument(
        help="The ID of the expense.",
        min=1
    ),
]

DESCRIPTION_OPTION = Annotated[
    str,
    Option(
        "--description",
        "-d",
        help="New description for the expense."
    ),
]

AMOUNT_OPTION = Annotated[
    float,
    Option(
        "--amount",
        "-a",
        help="New amount for the expense."
    ),
]

CATEGORY_OPTION = Annotated[
    str,
    Option(
        "--category",
        "-c",
        help="New category for the expense."
    ),
]

NOTES_OPTION = Annotated[
    str,
    Option(
        "--notes",
        "-n",
        help="New notes for the expense."
    ),
]


@app.command("update")
def update_expense(
    expense_id: EXPENSE_ID,
    description: DESCRIPTION_OPTION = "",
    amount: AMOUNT_OPTION = 0.0,
    category: CATEGORY_OPTION = "",
    notes: NOTES_OPTION = "",
):
    """Update an existing expense."""
    repo: ExpenseRepository = di[ExpenseRepository]

    expense = repo.get(expense_id)
    if expense is None:
        rich_print(f"\n[red]Expense {expense_id} not found[/red]\n")
        raise Exit(code=2)

    if description:
        expense.description = description
    if amount > 0:
        expense.amount = amount
    if category:
        expense.category = category
    if notes:
        expense.notes = notes

    repo.update(expense)
    rich_print(f"\n[green]Expense {expense_id} successfully updated[/green]\n")
