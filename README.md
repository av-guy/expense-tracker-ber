[![codecov](https://codecov.io/gh/av-guy/expense-tracker-ber/branch/main/graph/badge.svg)](https://codecov.io/gh/av-guy/expense-tracker-ber)

# Expense Manager CLI

A simple Typer-based command-line app for managing your expenses.

## Setup

Clone the repo and enter the directory:

```bash
git clone https://github.com/av-guy/expense-tracker-ber.git
cd expense-tracker-ber
```

Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
```

Install dependencies:

```bash
pip install .           # Core dependencies
pip install .[dev]      # Dev/test tools
```

## Run the App

Use the help command to explore available commands:

```bash
python -m src.expense_tracker --help
```

## Run Tests

```bash
pytest
```

## Build and Install

Install the build tool:

```bash
python -m pip install --upgrade build
```

Build the package:

```bash
python -m build
```

Install from the generated archive:

```bash
pip install dist/expense_tracker-0.0.1.tar.gz
```

After installation, run the CLI:

```bash
expense-tracker --help
```

_If you follow these instructions, this application will only be available from within your virtual environment_
