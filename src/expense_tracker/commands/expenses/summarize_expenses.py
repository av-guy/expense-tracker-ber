from pathlib import Path
from typing import Annotated
from datetime import datetime

from kink import di
from typer import Option, Argument
from rich import print as rich_print
from rich.table import Table

from ...protocols import ExpenseRepository, ExpenseCSVService
from .command_router import app


MONTH_NUMBER = Annotated[
    int,
    Argument(
        help="Month number (1–12) for the report.",
        min=1,
        max=12
    ),
]

CATEGORY_FILTER = Annotated[
    str,
    Option(
        "--category",
        "-c",
        help="Optional category filter for the summary."
    ),
]

EXPORT_FLAG = Annotated[
    bool,
    Option(
        "--export",
        "-e",
        help="Whether to export the summary to a CSV file."
    ),
]

EXPORT_DIR = Annotated[
    Path,
    Option(
        "--directory",
        "-d",
        help="Target directory for exported file. Defaults to the current working directory.",
    ),
]

EXPORT_FILENAME = Annotated[
    str,
    Option(
        "--filename",
        "-f",
        help=(
            "Filename for export. "
            "The '.csv' extension will be added automatically. "
            "If omitted, a timestamped name will be used."
        ),
    ),
]


@app.command("summary")
def summarize_user_expenses(
    category: CATEGORY_FILTER = "",
    export: EXPORT_FLAG = False,
    directory: EXPORT_DIR = Path.cwd(),
    filename: EXPORT_FILENAME = "",
):
    """View total expenses and count, optionally filtered by category."""
    repo: ExpenseRepository = di[ExpenseRepository]
    csv_service: ExpenseCSVService = di[ExpenseCSVService]

    total, count = repo.category_summary(category or None)

    if export:
        csv_service.export_summary(
            category or None,
            total,
            count,
            directory,
            filename or None,
            exported_on=datetime.now(),
        )
        rich_print("\n[green]Summary exported successfully[/green]\n")

    rich_print("\n[bold cyan]Expense Summary[/bold cyan]")
    rich_print(f"Category: [magenta]{category or 'All'}[/magenta]")
    rich_print(f"Total Expenses: [green]${total:.2f}[/green]")
    rich_print(f"Number of Entries: [magenta]{count}[/magenta]\n")


@app.command("month")
def monthly_summary(
    month: MONTH_NUMBER,
    export: EXPORT_FLAG = False,
    directory: EXPORT_DIR = Path.cwd(),
    filename: EXPORT_FILENAME = "",
):
    """View summary of expenses for a specific month of the current year."""
    repo: ExpenseRepository = di[ExpenseRepository]
    csv_service: ExpenseCSVService = di[ExpenseCSVService]

    year = datetime.now().year
    expenses = repo.monthly_summary(month, year)

    if not expenses:
        rich_print(
            f"[yellow]No expenses found for {year}-{month:02d}[/yellow]")
        return

    total = sum(e.amount for e in expenses)

    if export:
        csv_service.export_monthly_summary(
            expenses, total, year, month, directory, filename or None
        )
        rich_print(
            "\n[green]Monthly report exported successfully[/green]\n")

    table = Table(title=f"Expenses for {year}-{month:02d}", show_lines=True)
    table.add_column("ID", style="cyan", justify="right")
    table.add_column("Description", style="bold white")
    table.add_column("Amount", justify="right", style="green")
    table.add_column("Category", style="magenta")
    table.add_column("Date", style="dim")

    for e in expenses:
        table.add_row(
            str(e.id),
            e.description,
            f"${e.amount:.2f}",
            e.category or "-",
            e.date.strftime("%Y-%m-%d"),
        )

    rich_print("")
    rich_print(table)
    rich_print(
        f"\n[bold cyan]Total for {year}-{month:02d}: [green]${total:.2f}[/green][/bold cyan]\n"
    )
