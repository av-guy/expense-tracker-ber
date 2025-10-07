# pylint: disable=import-outside-toplevel

from .bootstrap import initialize


def create_app():
    initialize()
    from .commands import expenses
    return expenses.app


app = create_app()
