from typing import Annotated

from kink import di
from typer import Argument, Exit
from rich import print as rich_print

from ...protocols import ExpenseRepository
from .command_router import app


EXPENSE_ID = Annotated[
    int,
    Argument(
        help="The ID of the expense.",
        min=1
    )
]


@app.command("delete")
def delete_expense(expense_id: EXPENSE_ID):
    """Delete an expense."""
    repo: ExpenseRepository = di[ExpenseRepository]

    expense = repo.get(expense_id)
    if expense is None:
        rich_print(f"\n[red]Expense {expense_id} not found[/red]\n")
        raise Exit(code=2)

    repo.delete(expense)
    rich_print(f"\n[green]Expense {expense_id} succesfully deleted[/green]")
