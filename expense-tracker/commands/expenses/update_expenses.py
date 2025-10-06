from typing import Annotated, Callable
from contextlib import AbstractContextManager

from kink import di
from typer import Argument, Option
from rich import print as rich_print
from sqlalchemy.orm import Session

from ...models import Expense
from .command_router import app

EXPENSE_ID = Annotated[
    int,
    Argument(help="The ID of the expense.")
]

DESCRIPTION_OPTION = Annotated[
    str,
    Option("--description", "-d", help="New description for the expense.")
]

AMOUNT_OPTION = Annotated[
    float,
    Option("--amount", "-a", help="New amount for the expense.")
]

CATEGORY_OPTION = Annotated[
    str,
    Option("--category", "-c", help="New category for the expense.")
]

NOTES_OPTION = Annotated[
    str,
    Option("--notes", "-n", help="New notes for the expense.")
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
    db_session: Callable[[], AbstractContextManager[Session]
                         ] = di["db_session_context"]

    with db_session() as db:
        if not isinstance(db, Session):
            rich_print("")
            rich_print("[red]Invalid database session[/red]")
            rich_print("")
            return

        expense = db.get(Expense, expense_id)
        if not expense:
            rich_print("")
            rich_print(f"[red]Expense {expense_id} not found[/red]")
            rich_print("")
            return

        if description:
            expense.description = description
        if amount > 0:
            expense.amount = amount
        if category:
            expense.category = category
        if notes:
            expense.notes = notes

        db.commit()

        rich_print("")
        rich_print(f"[green]Expense {expense_id} updated[/green]")
        rich_print("")
