# pylint: disable=wrong-import-order

from . import bootstrap
from .commands import expenses


app = expenses.app


if __name__ == "__main__":
    bootstrap.initialize()
    app()
