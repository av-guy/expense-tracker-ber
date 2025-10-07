# pylint: disable=redefined-outer-name
# pylint: disable=unused-argument
# pylint: disable=wrong-import-order
# pylint: disable=unused-import

from pathlib import Path
from datetime import datetime
from pytest import fixture, raises

import pandas as pd

from .utils import test_expense
from src.expense_tracker.models import Expense
from src.expense_tracker.services import PandasCSVService


@fixture
def csv_service() -> PandasCSVService:
    return PandasCSVService()


@fixture
def tmp_dir(tmp_path: Path) -> Path:
    return tmp_path


@fixture
def sample_expenses() -> list[Expense]:
    return [
        Expense(
            id=1,
            description="Groceries",
            amount=50.25,
            category="Food",
            notes="Weekly grocery trip",
            date=datetime(2025, 1, 1),
        ),
        Expense(
            id=2,
            description="Gas",
            amount=35.00,
            category="Transport",
            notes="Fuel refill",
            date=datetime(2025, 1, 2),
        ),
    ]


def test_export_expenses_creates_csv(
    csv_service: PandasCSVService,
    tmp_dir: Path,
    sample_expenses: list[Expense]
):
    csv_service.export_expenses(
        sample_expenses, tmp_dir,
        "expenses_test"
    )

    output = tmp_dir / "expenses_test.csv"
    assert output.exists()

    df = pd.read_csv(output)
    assert len(df) == 2
    assert set(df.columns) == {"ID", "Description",
                               "Category", "Amount", "Date", "Notes"}
    assert "Groceries" in df["Description"].values


def test_export_summary_creates_csv(csv_service: PandasCSVService, tmp_dir: Path):
    csv_service.export_summary("Food", 123.45, 3, tmp_dir, "summary_test")

    output = tmp_dir / "summary_test.csv"
    assert output.exists()

    df = pd.read_csv(output)
    assert len(df) == 1
    assert df.iloc[0]["Category"] == "Food"
    assert df.iloc[0]["Total"] == 123.45
    assert df.iloc[0]["Entries"] == 3


def test_export_monthly_summary_creates_csv(
    csv_service: PandasCSVService,
    tmp_dir: Path,
    sample_expenses: list[Expense]
):
    csv_service.export_monthly_summary(
        sample_expenses, total=85.25, year=2025, month=1,
        directory=tmp_dir, filename="monthly_test"
    )

    output = tmp_dir / "monthly_test.csv"
    assert output.exists()

    df = pd.read_csv(output)
    assert len(df) == 3
    assert "Total" in df["Description"].values


def test_import_expenses_reads_csv(
    csv_service: PandasCSVService,
    tmp_dir: Path
):
    data = pd.DataFrame([
        {"Description": "Lunch", "Amount": 12.50,
            "Category": "Food", "Notes": "Cafe"},
        {"Description": "Taxi", "Amount": 20.00,
            "Category": "Transport", "Notes": "Airport ride"},
    ])
    file = tmp_dir / "expenses_import.csv"
    data.to_csv(file, index=False)

    expenses = csv_service.import_expenses(file)
    assert isinstance(expenses, list)
    assert all(isinstance(e, Expense) for e in expenses)
    assert len(expenses) == 2
    assert expenses[0].description == "Lunch"
    assert expenses[1].amount == 20.00


def test_import_expenses_missing_file(
    csv_service: PandasCSVService,
    tmp_dir: Path
):
    missing_file = tmp_dir / "does_not_exist.csv"
    with raises(FileNotFoundError):
        csv_service.import_expenses(missing_file)


def test_import_expenses_missing_required_columns(
    csv_service: PandasCSVService,
    tmp_dir: Path
):
    invalid_df = pd.DataFrame([{"WrongColumn": "test"}])
    invalid_file = tmp_dir / "invalid.csv"
    invalid_df.to_csv(invalid_file, index=False)

    with raises(ValueError):
        csv_service.import_expenses(invalid_file)


def test_export_expenses_autoname_creates_file(
    csv_service: PandasCSVService,
    tmp_dir: Path,
    sample_expenses: list[Expense]
):
    csv_service.export_expenses(sample_expenses, tmp_dir)

    files = list(tmp_dir.glob("expenses_*.csv"))
    assert len(files) == 1
    output = files[0]
    assert output.exists()

    df = pd.read_csv(output)
    assert len(df) == 2
    assert set(df.columns) == {"ID", "Description",
                               "Category", "Amount", "Date", "Notes"}


def test_export_summary_autoname_creates_file(
    csv_service: PandasCSVService,
    tmp_dir: Path
):
    csv_service.export_summary("Food", 123.45, 3, tmp_dir)

    files = list(tmp_dir.glob("summary_*.csv"))
    assert len(files) == 1
    output = files[0]
    assert output.exists()

    df = pd.read_csv(output)
    assert len(df) == 1
    assert df.iloc[0]["Category"] == "Food"


def test_export_monthly_summary_autoname_creates_file(
    csv_service: PandasCSVService,
    tmp_dir: Path,
    sample_expenses: list[Expense]
):
    csv_service.export_monthly_summary(
        sample_expenses, total=85.25, year=2025, month=1, directory=tmp_dir)

    files = list(tmp_dir.glob("monthly_2025_01_*.csv"))
    assert len(files) == 1
    output = files[0]
    assert output.exists()

    df = pd.read_csv(output)
    assert "Total" in df["Description"].values
