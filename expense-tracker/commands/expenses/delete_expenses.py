

from typing import Annotated, Callable
from contextlib import AbstractContextManager

from kink import di
from typer import Argument
from rich import print as rich_print
from sqlalchemy.orm import Session

from ...models import Expense
from .command_router import app

EXPENSE_ID = Annotated[
    int,
    Argument(help="The ID of the expense.")
]


@app.command("delete")
def delete_expense(expense_id: EXPENSE_ID):
    """Delete an expense."""
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

        db.delete(expense)
        db.commit()

        rich_print("")
        rich_print(f"[green]Expense {expense_id} deleted[/green]")
        rich_print("")
