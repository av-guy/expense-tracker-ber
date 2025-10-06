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

from ...models import Expense
from .command_router import app

CATEGORY_FILTER = Annotated[
    str,
    Option(
        "--category",
        "-c",
        help="Optional category filter for expenses."
    )
]

EXPORT_DIR = Annotated[
    Path,
    Option(
        "--directory",
        "-d",
        help="Optional file path for CSV export. Must end with '.csv' if provided.",
    ),
]

EXPORT_FILENAME = Annotated[
    str,
    Option(
        "--filename",
        "-n",
        help="Optional filename for export ('.csv' will be added automatically).",
    ),
]

EXPORT_FLAG = Annotated[
    bool,
    Option(
        "--export",
        "-e",
        help="Whether to export results to a CSV file."
    )
]


@app.command("list")
def list_user_expenses(
    category: CATEGORY_FILTER = "",
    export: EXPORT_FLAG = False,
    directory: EXPORT_DIR = Path.cwd(),
    filename: EXPORT_FILENAME = "",
):
    """List all expenses, optionally filtered by category."""
    db_session: Callable[[], AbstractContextManager[Session]
                         ] = di["db_session_context"]

    with db_session() as db:
        if not isinstance(db, Session):
            rich_print("\n[red]Invalid database session[/red]\n")
            return

        query = db.query(Expense)

        if category:
            query = query.filter(Expense.category == category)

        expenses = query.order_by(Expense.date.desc()).all()

        if not expenses:
            rich_print("\n[yellow]No expenses found[/yellow]\n")
            return

        if export:
            export_dir = directory

            try:
                export_dir.mkdir(parents=True, exist_ok=True)
            except FileNotFoundError as exc:
                rich_print(f"\n[red]{exc}[/red]\n")
                return

            if filename:
                export_path = export_dir / f"{filename}.csv"
            else:
                timestamp = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
                export_path = export_dir / f"expenses_{timestamp}.csv"

            df = pd.DataFrame(
                [
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
            )

            df.to_csv(export_path, index=False)
            rich_print(f"\n[green]Exported to {export_path.resolve()}[/green]\n")
            return

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
