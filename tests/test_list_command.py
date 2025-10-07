# pylint: disable=redefined-outer-name
# pylint: disable=unused-argument
# pylint: disable=wrong-import-order
# pylint: disable=unused-import

from pathlib import Path
from typer.testing import CliRunner
import pandas as pd

from .utils import TestingSessionLocal, test_expense
from src.expense_tracker.models import Expense
from src.expense_tracker.cli import app


runner = CliRunner()


def test_list_expenses_displays_table(test_expense: Expense):
    result = runner.invoke(app, ["list"])

    assert result.exit_code == 0
    assert "Expenses" in result.output
    assert test_expense.description in result.output
    assert test_expense.category is not None
    assert test_expense.category in result.output


def test_list_expenses_filtered_by_category(test_expense: Expense):
    assert test_expense.category is not None

    result = runner.invoke(app, ["list", "--category", test_expense.category])

    assert result.exit_code == 0
    assert test_expense.category in result.output
    assert test_expense.description in result.output


def test_list_expenses_export_to_csv(tmp_path: Path, test_expense: Expense):
    result = runner.invoke(
        app,
        ["list", "--export", "--directory", str(tmp_path), "--filename", "expenses"],
    )

    assert result.exit_code == 0
    assert "Expenses exported successfully" in result.output
    csv_path = tmp_path / "expenses.csv"
    assert csv_path.exists()

    df = pd.read_csv(csv_path)
    assert len(df) >= 1
    assert "Description" in df.columns
    assert test_expense.description in df["Description"].values


def test_list_expenses_no_results(tmp_path: Path):
    with TestingSessionLocal() as db:
        db.query(Expense).delete()
        db.commit()

    result = runner.invoke(app, ["list"])
    assert result.exit_code == 0
    assert "No expenses found" in result.output
