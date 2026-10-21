# PocketLedger – Project Report

## 1. Title
PocketLedger: A Command-Line Personal Expense Tracker

## 2. Abstract
PocketLedger is a modular Python CLI application that enables users to record income and expenses, manage budgets, generate financial reports, handle recurring transactions, and export data to CSV. It demonstrates object-oriented design, Decimal arithmetic, JSON persistence, input validation, and automated testing, making it suitable as a Computer Science Engineering portfolio project.

## 3. Introduction
Managing personal finances is a common need for students. Existing mobile apps often hide implementation details. PocketLedger provides a transparent, fully inspectable codebase that teaches Python best practices while remaining practically useful.

## 4. Problem Statement
Students need a simple, offline tool to track where money goes, compare spending against budgets, and understand income versus expenses without relying on proprietary cloud services.

## 5. Objectives
- Record and categorize income and expenses
- Provide searchable, filterable transaction history
- Calculate accurate financial summaries using Decimal
- Support monthly budgets with warnings
- Generate period reports and CSV exports
- Persist data safely in JSON files
- Deliver a complete, tested, documented codebase

## 6. Scope
In scope: CLI interaction, JSON storage, budgets, recurring rules, reports, export, backup/restore, unit tests, documentation.  
Out of scope: GUI, web interface, databases, bank APIs, multi-user authentication.

## 7. Functional Requirements
See README and `docs/requirements.md` for the full list of 14 core features (CRUD, search, filter, reports, budgets, recurring, export, backup, categories, settings).

## 8. Non-Functional Requirements
- Python 3.11+
- No external runtime dependencies
- Atomic file writes
- Clear error messages
- Deterministic monetary calculations
- Isolated unit tests

## 9. System Architecture
Layered design:
- **CLI Layer** (`cli.py`) – menus and user interaction
- **Business Logic** (`tracker.py`, `budgets.py`, `reports.py`, `recurring.py`, `categories.py`)
- **Data Layer** (`storage.py`, `models.py`)
- **Utilities** (`validation.py`, `export.py`, `settings.py`)

## 10. Module Descriptions
| Module       | Responsibility                              |
|--------------|---------------------------------------------|
| models       | Transaction, Budget, RecurringRule dataclasses |
| storage      | JSON load/save, backup/restore              |
| tracker      | CRUD, search, filter                        |
| reports      | Summaries, monthly/yearly reports           |
| budgets      | Budget CRUD and status calculations         |
| recurring    | Rule management and occurrence generation   |
| categories   | Category lists and custom categories        |
| export       | CSV export with injection protection        |
| validation   | Amount, date, and input validators          |
| cli          | Interactive menu system                     |

## 11. Data Model
Transactions store: id, type, amount (Decimal string), category, date, description, payment_method, tags, notes, created_at, updated_at.  
Budgets: amount, year, month, optional category.  
Recurring rules: description, amount, interval (weekly/monthly), start/end dates, last_generated.

## 12. OOP Design
- Dataclasses for immutable-style value objects
- Single-responsibility managers (ExpenseTracker, BudgetManager, etc.)
- No deep inheritance hierarchies
- Type hints throughout

## 13. File Storage
Atomic write pattern: write to `.tmp` then `replace()`. Malformed records are skipped on load. Backup copies entire data directory.

## 14. Financial Calculations
- Net Balance = Total Income − Total Expenses
- Average Expense = Total Expenses / Expense Count (or N/A)
- Category aggregation via dictionary accumulation
- All amounts quantized to 2 decimal places

## 15. Budget Management
Remaining = max(Budget − Spent, 0)  
Overspent = max(Spent − Budget, 0)  
Warning when percent_used ≥ configurable threshold (default 80%)

## 16. Recurring Transactions
On startup or manual trigger, `process_due()` walks from last_generated (or start_date) to today, generating occurrences and updating last_generated to prevent duplicates. Month-end days clamp to the last valid day of the target month.

## 17. Testing Methodology
`unittest` suite covering models, tracker, reports, budgets, storage, recurring, export, and validation. Temporary directories isolate file tests.

## 18. Actual Test Results
See `docs/test_results.md` (populated after test execution).

## 19. Limitations
- Local single-user only
- No automatic bank import
- Recurring fill-in happens when the application runs

## 20. Future Enhancements
SQLite backend, ASCII charts, multi-currency, bank CSV import.

## 21. Conclusion
PocketLedger successfully delivers a complete, tested, and documented CLI expense tracker that demonstrates core Python skills required of a CSE graduate.

## 22. References
- Python Software Foundation – decimal, datetime, unittest documentation
- PEP 8, PEP 484 (Type Hints)
- ISO 8601 date format
