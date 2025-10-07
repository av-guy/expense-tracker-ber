# pylint: disable=redefined-outer-name
# pylint: disable=unused-argument
# pylint: disable=wrong-import-order
# pylint: disable=unused-import

from pathlib import Path
from datetime import datetime
from typer.testing import CliRunner
import pandas as pd

from .utils import TestingSessionLocal, test_expense
from src.expense_tracker.models import Expense
from src.expense_tracker.cli import app


runner = CliRunner()


def test_summary_command_displays_totals(test_expense: Expense):
    result = runner.invoke(app, ["summary"])

    assert result.exit_code == 0
    assert "Expense Summary" in result.output
    assert "Total Expenses" in result.output
    assert "Number of Entries" in result.output


def test_summary_command_export_creates_csv(tmp_path: Path, test_expense: Expense):
    result = runner.invoke(
        app,
        ["summary", "--export", "--directory",
            str(tmp_path), "--filename", "summary"],
    )

    assert result.exit_code == 0
    assert "Summary exported successfully" in result.output

    csv_path = tmp_path / "summary.csv"
    assert csv_path.exists()

    df = pd.read_csv(csv_path)
    assert len(df) == 1
    assert "Total" in df.columns
    assert "Entries" in df.columns


def test_summary_command_filtered_by_category(test_expense: Expense):
    assert test_expense.category is not None

    result = runner.invoke(
        app, ["summary", "--category", test_expense.category])

    assert result.exit_code == 0
    assert f"{test_expense.category}" in result.output


def test_month_command_displays_table(test_expense: Expense):
    current_month = datetime.now().month
    result = runner.invoke(app, ["month", str(current_month)])

    assert result.exit_code == 0
    assert "Expenses for" in result.output
    assert test_expense.description in result.output
    assert test_expense.category is not None
    assert test_expense.category in result.output


def test_month_command_export_creates_csv(tmp_path: Path, test_expense: Expense):
    current_month = datetime.now().month
    result = runner.invoke(
        app,
        [
            "month",
            str(current_month),
            "--export",
            "--directory",
            str(tmp_path),
            "--filename",
            "monthly",
        ],
    )

    assert result.exit_code == 0
    assert "Monthly report exported successfully" in result.output

    csv_path = tmp_path / "monthly.csv"
    assert csv_path.exists()

    df = pd.read_csv(csv_path)
    assert "Description" in df.columns
    assert any("Total" in str(v) for v in df["Description"].values)


def test_month_command_no_expenses(tmp_path: Path):
    with TestingSessionLocal() as db:
        db.query(Expense).delete()
        db.commit()

    current_month = datetime.now().month
    result = runner.invoke(app, ["month", str(current_month)])

    assert result.exit_code == 0
    assert "No expenses found" in result.output
