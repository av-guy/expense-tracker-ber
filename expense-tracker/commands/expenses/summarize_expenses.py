# pylint: disable=not-callable

from pathlib import Path
from typing import Annotated, Callable
from contextlib import AbstractContextManager
from datetime import datetime

import pandas as pd

from kink import di
from typer import Option
from rich import print as rich_print
from rich.table import Table
from sqlalchemy.orm import Session
from sqlalchemy import func
from sqlalchemy import extract

from ...models import Expense
from .command_router import app


MONTH_NUMBER = Annotated[
    int,
    Option(
        "--month",
        "-m",
        help="Month number (1–12) for the report."
    )
]

CATEGORY_FILTER = Annotated[
    str,
    Option(
        "--category",
        "-c",
        help="Optional category filter for the summary."
    )
]

EXPORT_FLAG = Annotated[
    bool,
    Option(
        "--export",
        "-e",
        help="Whether to export the summary to a CSV file."
    )
]

EXPORT_DIR = Annotated[
    Path,
    Option(
        "--directory",
        "-d",
        help="Target directory for exported file. Defaults to the current working directory.",
    )
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
    )
]


@app.command("summary")
def summarize_user_expenses(
    category: CATEGORY_FILTER = "",
    export: EXPORT_FLAG = False,
    directory: EXPORT_DIR = Path.cwd(),
    filename: EXPORT_FILENAME = "",
):
    """View total expenses and count, optionally filtered by category."""
    db_session: Callable[[], AbstractContextManager[Session]
                         ] = di["db_session_context"]

    with db_session() as db:
        if not isinstance(db, Session):
            rich_print("")
            rich_print("[red]Invalid database session[/red]")
            rich_print("")
            return

        query = db.query(func.sum(Expense.amount), func.count())

        if category:
            query = query.filter(Expense.category == category)

        total, count = 0.0, 0

        if (values := query.first()) is not None:
            total, count = values
            total = total or 0.0

        if export:
            export_dir = directory

            try:
                export_dir.mkdir(parents=True, exist_ok=True)
            except FileNotFoundError as exc:
                rich_print("")
                rich_print(f"[red]{exc}[/red]")
                rich_print("")
                return

            if filename:
                export_path = export_dir / f"{filename}.csv"
            else:
                timestamp = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
                export_path = export_dir / f"summary_{timestamp}.csv"

            df = pd.DataFrame(
                [
                    {
                        "Category": category or "All",
                        "Total": total,
                        "Entries": count,
                        "Exported On": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    }
                ]
            )

            df.to_csv(export_path, index=False)

            rich_print("")
            rich_print(
                f"[green]Summary exported to {export_path.resolve()}[/green]"
            )
            rich_print("")
            return

        rich_print("")
        rich_print("\n[bold cyan]Expense Summary[/bold cyan]")
        rich_print(f"Category: [magenta]{category or 'All'}[/magenta]")
        rich_print(f"Total Expenses: [green]${total:.2f}[/green]")
        rich_print(f"Number of Entries: [magenta]{count}[/magenta]\n")
        rich_print("")


@app.command("month")
def monthly_summary(
    month: MONTH_NUMBER,
    export: EXPORT_FLAG = False,
    directory: EXPORT_DIR = Path.cwd(),
    filename: EXPORT_FILENAME = "",
):
    """View summary of expenses for a specific month of the current year."""
    year = datetime.now().year
    db_session: Callable[[], AbstractContextManager[Session]
                         ] = di["db_session_context"]

    with db_session() as db:
        if not isinstance(db, Session):
            rich_print("")
            rich_print("[red]Invalid database session[/red]")
            rich_print("")
            return

        expenses = (
            db.query(Expense)
            .filter(extract("year", Expense.date) == year)
            .filter(extract("month", Expense.date) == month)
            .all()
        )

        if not expenses:
            rich_print(
                f"[yellow]No expenses found for {year}-{month:02d}[/yellow]")
            return

        total = sum(e.amount for e in expenses)

        if export:
            export_dir = directory
            export_dir.mkdir(parents=True, exist_ok=True)

            if filename:
                export_path = export_dir / f"{filename}.csv"
            else:
                timestamp = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
                export_path = export_dir / \
                    f"expenses_{year}_{month:02d}_{timestamp}.csv"

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
            df.loc[len(df)] = {
                "ID": "", "Description": "Total", "Amount": total}
            df.to_csv(export_path, index=False)

            rich_print("")
            rich_print(
                f"[green]Monthly report exported to {export_path.resolve()}[/green]")
            rich_print("")
            return

        table = Table(
            title=f"Expenses for {year}-{month:02d}", show_lines=True)
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
            f"\n[bold cyan]Total for {year}-{month:02d}: [green]${total:.2f}[/green][/bold cyan]"
        )
        rich_print("")
