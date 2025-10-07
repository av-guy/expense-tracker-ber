# pylint: disable=redefined-outer-name
# pylint: disable=unused-argument
# pylint: disable=wrong-import-order
# pylint: disable=unused-import

from typer.testing import CliRunner

from .utils import TestingSessionLocal, test_expense
from src.expense_tracker.models import Expense
from src.expense_tracker.cli import app


runner = CliRunner()


def test_update_existing_expense(test_expense: Expense):
    expense_id = test_expense.id
    result = runner.invoke(
        app,
        [
            "update",
            str(expense_id),
            "--description",
            "Updated description",
            "--amount",
            "99.99",
            "--category",
            "Updated category",
            "--notes",
            "Updated notes",
        ],
    )

    assert result.exit_code == 0
    assert f"Expense {expense_id} successfully updated" in result.output

    with TestingSessionLocal() as db:
        updated = db.get(Expense, expense_id)
        assert updated is not None
        assert updated.description == "Updated description"
        assert updated.amount == 99.99
        assert updated.category == "Updated category"
        assert updated.notes == "Updated notes"


def test_update_nonexistent_expense():
    result = runner.invoke(
        app, ["update", "9999", "--description", "Ghost expense"])

    assert result.exit_code == 2
    assert "Expense 9999 not found" in result.output


def test_update_invalid_id_below_one():
    result = runner.invoke(app, ["update", "0", "--description", "Invalid ID"])
    assert result.exit_code == 2

    result = runner.invoke(
        app, ["update", "-1", "--description", "Invalid ID"])
    assert result.exit_code == 2
