# PocketLedger

**Command-Line Personal Expense Tracker**

PocketLedger is a modular, object-oriented Python application that helps you record, organize, analyze, and manage personal income and expenses from the terminal. It is designed as a complete portfolio project for Computer Science Engineering students.

---

## Features

- **Add expenses and income** with amount, category, date, description, payment method, tags, and notes
- **View, edit, and delete** transactions with unique IDs
- **Search and filter** by text, date range, category, type, amount, payment method, and tags
- **Financial summaries** – total income, expenses, net balance, averages, largest/smallest expenses, category breakdowns
- **Monthly, yearly, and custom date-range reports** with previous-period comparison
- **Budget management** – overall and category-specific monthly budgets with warning thresholds
- **Recurring transactions** – weekly and monthly rules with automatic occurrence generation and duplicate prevention
- **CSV export** of transactions and summaries (formula-injection safe)
- **Backup and restore** of all data files
- **Custom categories** for expense and income
- **Settings** – currency symbol, future-date policy, budget warning threshold
- **JSON persistence** with atomic writes and validation
- **Decimal arithmetic** for accurate money calculations
- **Full unit test suite** using `unittest`

---

## Technologies

| Component            | Technology                          |
|----------------------|-------------------------------------|
| Language             | Python 3.11+                        |
| Interface            | Interactive CLI                     |
| Storage              | JSON files                          |
| Money                | `decimal.Decimal`                   |
| Dates                | `datetime`                          |
| Testing              | `unittest` (standard library)       |
| Dependencies         | None (standard library only)        |

---

## Project Structure

```
PocketLedger/
├── README.md
├── LICENSE
├── .gitignore
├── requirements.txt
├── src/
│   └── expense_tracker/
│       ├── __init__.py
│       ├── __main__.py
│       ├── cli.py
│       ├── models.py
│       ├── tracker.py
│       ├── storage.py
│       ├── validation.py
│       ├── reports.py
│       ├── budgets.py
│       ├── recurring.py
│       ├── categories.py
│       ├── export.py
│       └── settings.py
├── tests/
│   ├── test_models.py
│   ├── test_tracker.py
│   ├── test_storage.py
│   ├── test_validation.py
│   ├── test_reports.py
│   ├── test_budgets.py
│   ├── test_recurring.py
│   └── test_export.py
├── data/                  # Runtime JSON data (created on first run)
├── examples/
├── exports/
└── docs/                  # Full project documentation
```

---

## Installation & Execution

### 1. Check Python version

```bash
python --version
# or
python3 --version
```

Requires **Python 3.11 or later**.

### 2. Extract the project

Unzip the archive and open a terminal in the project directory.

### 3. (Recommended) Create a virtual environment

**Windows (Command Prompt):**
```cmd
python -m venv .venv
.venv\Scripts\activate
```

**Windows (PowerShell):**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**Linux / macOS:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 4. Install (editable mode)

```bash
pip install -e .
```

Or simply run without installing by setting `PYTHONPATH`:

```bash
# Linux / macOS
export PYTHONPATH=src
python -m expense_tracker

# Windows CMD
set PYTHONPATH=src
python -m expense_tracker
```

### 5. Run the application

```bash
python -m expense_tracker
```

Optional data directory:

```bash
python -m expense_tracker --data-dir path/to/data
```

### 6. Run tests

```bash
# From project root with PYTHONPATH or after pip install -e .
python -m unittest discover -s tests -v
```

---

## Usage Examples

1. Start the app → Main menu appears.
2. Choose **1** to add an expense (amount, category, date, etc.).
3. Choose **2** to record income.
4. Choose **3** to view all transactions.
5. Choose **12** to set a monthly budget, then **13** to see status.
6. Choose **15** to export CSV files into the `exports/` folder.
7. Choose **16** to create a backup.

Dates must be entered as `YYYY-MM-DD` (example: `2026-10-21`).

---

## Data Storage

All data lives in the `data/` directory (configurable):

| File                         | Content                    |
|------------------------------|----------------------------|
| `transactions.json`          | Income and expense records |
| `categories.json`            | Expense & income categories|
| `budgets.json`               | Monthly budgets            |
| `recurring_transactions.json`| Recurring rules            |
| `settings.json`              | App settings               |

Monetary amounts are stored as **strings** (e.g. `"250.00"`) and converted to `Decimal` on load to avoid floating-point errors.

---

## Testing

```bash
python -m unittest discover -s tests -v
```

Tests use temporary directories and never touch real user data.

---

## Known Limitations

- Single-user, local-only; no multi-device sync.
- No bank import or online connectivity.
- Recurring generation occurs on application start / manual trigger; missed days are filled when the app is opened.
- CSV export does not support Excel-specific formatting beyond formula-injection protection.
- Not a substitute for official bank statements or professional financial advice.

---

## Future Enhancements

- SQLite backend option
- Simple charts (ASCII or export to image)
- Multi-currency support
- Tag-based analytics
- Import from bank CSV statements

---

## License

MIT License – see [LICENSE](LICENSE).

---

## Publishing to GitHub

1. Create a new repository on GitHub.
2. From the project root:

```bash
git init
git add .
git commit -m "Initial commit: PocketLedger CLI Expense Tracker"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/PocketLedger.git
git push -u origin main
```

Add a short description and topics such as `python`, `cli`, `expense-tracker`, `portfolio`, `student-project`.
