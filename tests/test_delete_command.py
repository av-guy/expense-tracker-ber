# pylint: disable=redefined-outer-name
# pylint: disable=unused-argument
# pylint: disable=wrong-import-order
# pylint: disable=unused-import

from typer.testing import CliRunner

from .utils import TestingSessionLocal, test_expense
from src.expense_tracker.models import Expense
from src.expense_tracker.cli import app


runner = CliRunner()


def test_delete_existing_expense(test_expense: Expense):
    expense_id = test_expense.id
    result = runner.invoke(app, ["delete", str(expense_id)])

    assert result.exit_code == 0
    assert f"Expense {expense_id} succesfully deleted" in result.output

    with TestingSessionLocal() as db:
        deleted = db.get(Expense, expense_id)
        assert deleted is None


def test_delete_nonexistent_expense():
    result = runner.invoke(app, ["delete", "9999"])

    assert result.exit_code == 2
    assert "Expense 9999 not found" in result.output


def test_delete_invalid_id_below_one():
    result = runner.invoke(app, ["delete", "0"])
    assert result.exit_code == 2

    result = runner.invoke(app, ["delete", "-1"])
    assert result.exit_code == 2
