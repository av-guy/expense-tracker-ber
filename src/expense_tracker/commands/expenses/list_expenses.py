from pathlib import Path
from typing import Annotated

from kink import di
from typer import Option, Exit
from rich import print as rich_print
from rich.table import Table

from ...protocols import ExpenseRepository, ExpenseCSVService
from .command_router import app


CATEGORY_FILTER = Annotated[
    str,
    Option(
        "--category",
        "-c",
        help="Optional category filter for expenses."
    ),
]

EXPORT_DIR = Annotated[
    Path,
    Option(
        "--directory",
        "-d",
        help="Directory for CSV export."
    ),
]

EXPORT_FILENAME = Annotated[
    str,
    Option(
        "--filename",
        "-n",
        help="Optional filename for export."
    ),
]

EXPORT_FLAG = Annotated[
    bool,
    Option(
        "--export",
        "-e",
        help="Whether to export results to a CSV file."
    ),
]


@app.command("list")
def list_user_expenses(
    category: CATEGORY_FILTER = "",
    export: EXPORT_FLAG = False,
    directory: EXPORT_DIR = Path.cwd(),
    filename: EXPORT_FILENAME = "",
):
    """List all expenses, optionally filtered by category."""
    repo: ExpenseRepository = di[ExpenseRepository]
    csv_service: ExpenseCSVService = di[ExpenseCSVService]

    expenses = repo.list(category or None)
    if not expenses:
        rich_print("\n[yellow]No expenses found[/yellow]\n")
        return

    if export:
        csv_service.export_expenses(expenses, directory, filename or None)
        rich_print("\n[green]Expenses exported successfully[/green]\n")

    table = Table(title="Expenses", show_lines=True)
    table.add_column("ID", justify="right", style="cyan")
    table.add_column("Description", style="bold white")
    table.add_column("Category", style="magenta")
    table.add_column("Amount", justify="right", style="green")
    table.add_column("Date", style="dim")
    table.add_column("Notes", style="dim")

    for e in expenses:
        table.add_row(
            str(e.id),
            e.description,
            e.category or "-",
            f"${e.amount:.2f}",
            e.date.strftime("%Y-%m-%d"),
            e.notes or "-",
        )

    rich_print("")
    rich_print(table)
    rich_print("")
