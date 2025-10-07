# pylint: disable=redefined-outer-name
# pylint: disable=unused-argument
# pylint: disable=wrong-import-order
# pylint: disable=unused-import

from typer.testing import CliRunner

from .utils import test_expense
from src.expense_tracker.__main__ import app


runner = CliRunner()


def test_app_help_command():
    result = runner.invoke(
        app, ["--help"],
    )

    assert result.exit_code == 0
