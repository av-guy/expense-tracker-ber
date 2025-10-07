# pylint: disable=redefined-outer-name
# pylint: disable=unused-argument
# pylint: disable=wrong-import-order

from pathlib import Path
from typer.testing import CliRunner
import pandas as pd

from .utils import TestingSessionLocal, test_expense
from src.expense_tracker.models import Expense
from src.expense_tracker.cli import app


runner = CliRunner()


def test_add_expense_command(test_expense: Expense):
    result = runner.invoke(
        app,
        ["add", "Groceries", "25.50", "--category",
            "Food", "--notes", "Weekly trip"],
    )

    assert result.exit_code == 0
    assert "Expense added with ID" in result.stdout

    with TestingSessionLocal() as db:
        expenses = db.query(Expense).all()
        assert len(expenses) == 2
        expense = expenses[1]
        assert expense.description == "Groceries"
        assert expense.amount == 25.50
        assert expense.category == "Food"
        assert expense.notes == "Weekly trip"


def test_bulk_import_success(tmp_path: Path):
    csv_path = tmp_path / "expenses.csv"
    pd.DataFrame(
        [
            {"Description": "Coffee", "Amount": 3.50, "Category": "Food"},
            {"Description": "Lunch", "Amount": 12.00, "Category": "Food"},
        ]
    ).to_csv(csv_path, index=False)

    result = runner.invoke(app, ["bulk", str(csv_path)])

    assert result.exit_code == 0
    assert "expenses added" in result.stdout

    with TestingSessionLocal() as db:
        expenses = db.query(Expense).all()
        assert len(expenses) == 2
        descriptions = [e.description for e in expenses]
        assert "Coffee" in descriptions
        assert "Lunch" in descriptions


def test_bulk_import_missing_file(tmp_path: Path):
    missing_file = tmp_path / "does_not_exist.csv"
    result = runner.invoke(app, ["bulk", str(missing_file)])

    assert result.exit_code == 2
    assert "Could not locate file" in result.output


def test_bulk_import_bad_columns(tmp_path: Path):
    bad_cols_file = tmp_path / "empty.csv"
    pd.DataFrame(columns=["Descrin", "Amounst"]
                 ).to_csv(bad_cols_file, index=False)

    result = runner.invoke(app, ["bulk", str(bad_cols_file)])

    assert result.exit_code == 2
    assert "File must contain required columns" in result.output


def test_bulk_import_empty_csv(tmp_path: Path):
    empty_file = tmp_path / "empty.csv"
    pd.DataFrame(columns=["Description", "Amount"]
                 ).to_csv(empty_file, index=False)

    result = runner.invoke(app, ["bulk", str(empty_file)])

    assert result.exit_code == 0
    assert "0 expenses" in result.output
