"""
Interactive command-line interface for PocketLedger.
"""

from __future__ import annotations

import sys
from datetime import date
from decimal import Decimal
from pathlib import Path
from typing import List, Optional

from .models import (
    Transaction,
    TransactionType,
    RecurringRule,
    RecurrenceInterval,
    DEFAULT_PAYMENT_METHODS,
)
from .storage import DataManager, StorageError
from .tracker import ExpenseTracker
from .categories import CategoryManager
from .budgets import BudgetManager
from .reports import ReportGenerator
from .recurring import RecurringTransactionManager
from .settings import SettingsManager
from .export import export_transactions, export_summary_csv
from .validation import (
    ValidationError,
    parse_amount,
    parse_date,
    parse_optional_date,
    parse_year_month,
    parse_year,
    validate_id,
    confirm,
)


def format_money(amount: Decimal, symbol: str = "₹") -> str:
    return f"{symbol}{amount:,.2f}"


def print_header(title: str) -> None:
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def print_transactions(
    transactions: List[Transaction],
    symbol: str = "₹",
    limit: int = 50,
) -> None:
    if not transactions:
        print("  No transactions found.")
        return
    shown = transactions[:limit]
    print(
        f"{'ID':<10} {'Date':<12} {'Type':<8} {'Category':<16} "
        f"{'Amount':>12} {'Description':<20} {'Method':<12}"
    )
    print("-" * 100)
    for t in shown:
        desc = (t.description[:18] + "..") if len(t.description) > 20 else t.description
        cat = (t.category[:14] + "..") if len(t.category) > 16 else t.category
        print(
            f"{t.id:<10} {t.date.isoformat():<12} {t.type.value:<8} {cat:<16} "
            f"{format_money(t.amount, symbol):>12} {desc:<20} {t.payment_method:<12}"
        )
    if len(transactions) > limit:
        print(f"\n  ... and {len(transactions) - limit} more. Use filters to narrow results.")


class CLIInterface:
    """Menu-driven CLI for PocketLedger."""

    def __init__(self, data_dir: Path | str = "data") -> None:
        self.dm = DataManager(data_dir)
        self.tracker = ExpenseTracker(self.dm)
        self.categories = CategoryManager(self.dm)
        self.budgets = BudgetManager(self.dm)
        self.recurring = RecurringTransactionManager(self.dm)
        self.settings = SettingsManager(self.dm)
        self.symbol = self.settings.currency_symbol

        # Auto-process recurring on startup
        self._process_recurring()

    def _process_recurring(self) -> None:
        try:
            new_txs = self.recurring.process_due()
            for tx in new_txs:
                self.tracker.add_transaction(tx)
            if new_txs:
                print(f"  [Recurring] Generated {len(new_txs)} transaction(s).")
        except Exception:
            pass  # non-fatal

    def run(self) -> None:
        print_header("PocketLedger - Personal Expense Tracker")
        print("  Track income, expenses, budgets and more.")
        while True:
            try:
                self._main_menu()
            except KeyboardInterrupt:
                print("\n\n  Goodbye!")
                sys.exit(0)
            except ValidationError as e:
                print(f"\n  Error: {e}")
            except StorageError as e:
                print(f"\n  Storage error: {e}")
            except Exception as e:
                print(f"\n  Unexpected error: {e}")

    def _main_menu(self) -> None:
        print_header("Main Menu")
        options = [
            ("1", "Add expense"),
            ("2", "Add income"),
            ("3", "View all transactions"),
            ("4", "Edit transaction"),
            ("5", "Delete transaction"),
            ("6", "Search transactions"),
            ("7", "Filter transactions"),
            ("8", "Financial summary"),
            ("9", "Monthly report"),
            ("10", "Yearly report"),
            ("11", "Custom date-range report"),
            ("12", "Manage budgets"),
            ("13", "View budget status"),
            ("14", "Manage recurring transactions"),
            ("15", "Export transactions / reports"),
            ("16", "Backup data"),
            ("17", "Restore data"),
            ("18", "Manage categories"),
            ("19", "Settings"),
            ("20", "Help"),
            ("21", "Exit"),
        ]
        for code, label in options:
            print(f"  {code:>2}. {label}")
        choice = input("\n  Enter choice: ").strip()
        handlers = {
            "1": self._add_expense,
            "2": self._add_income,
            "3": self._view_all,
            "4": self._edit,
            "5": self._delete,
            "6": self._search,
            "7": self._filter,
            "8": self._summary,
            "9": self._monthly,
            "10": self._yearly,
            "11": self._custom_range,
            "12": self._manage_budgets,
            "13": self._budget_status,
            "14": self._manage_recurring,
            "15": self._export,
            "16": self._backup,
            "17": self._restore,
            "18": self._manage_categories,
            "19": self._settings_menu,
            "20": self._help,
            "21": self._exit,
        }
        handler = handlers.get(choice)
        if handler:
            handler()
        else:
            print("  Invalid choice. Please enter a number from the menu.")

    # ----- Transaction CRUD -----

    def _prompt_transaction(self, tx_type: TransactionType) -> Optional[Transaction]:
        print_header(f"Add {tx_type.value.title()}")
        try:
            amount = parse_amount(input("  Amount: "))
            cats = (
                self.categories.get_expense_categories()
                if tx_type == TransactionType.EXPENSE
                else self.categories.get_income_categories()
            )
            print("  Categories:", ", ".join(cats))
            category = input("  Category: ").strip()
            if not category:
                raise ValidationError("Category is required.")
            # Allow custom on the fly
            if category not in cats:
                print(f"  '{category}' is a new category. It will be added.")
                kind = "expense" if tx_type == TransactionType.EXPENSE else "income"
                try:
                    self.categories.add_category(category, kind)
                except ValidationError:
                    pass  # already exists case-insensitive

            date_str = input(f"  Date (YYYY-MM-DD) [today={date.today().isoformat()}]: ").strip()
            tx_date = parse_date(date_str) if date_str else date.today()
            if not self.settings.allow_future_dates and tx_date > date.today():
                raise ValidationError("Future dates are disabled in settings.")

            description = input("  Description (optional): ").strip()
            print("  Payment methods:", ", ".join(DEFAULT_PAYMENT_METHODS))
            payment = input("  Payment method [Cash]: ").strip() or "Cash"
            tags_str = input("  Tags (comma-separated, optional): ").strip()
            tags = [t.strip() for t in tags_str.split(",") if t.strip()] if tags_str else []
            notes = input("  Notes (optional): ").strip()

            tx = Transaction(
                amount=amount,
                category=category,
                date=tx_date,
                type=tx_type,
                description=description,
                payment_method=payment,
                tags=tags,
                notes=notes,
            )
            return tx
        except ValidationError as e:
            print(f"  Error: {e}")
            return None

    def _add_expense(self) -> None:
        tx = self._prompt_transaction(TransactionType.EXPENSE)
        if tx:
            self.tracker.add_transaction(tx)
            print(f"\n  Expense added successfully. ID: {tx.id}")

    def _add_income(self) -> None:
        tx = self._prompt_transaction(TransactionType.INCOME)
        if tx:
            self.tracker.add_transaction(tx)
            print(f"\n  Income recorded successfully. ID: {tx.id}")

    def _view_all(self) -> None:
        print_header("All Transactions")
        sort_by = input("  Sort by (date/amount) [date]: ").strip().lower() or "date"
        txs = self.tracker.sort_transactions(by=sort_by, reverse=True)
        print_transactions(txs, self.symbol)

    def _edit(self) -> None:
        print_header("Edit Transaction")
        tx_id = validate_id(input("  Transaction ID: "))
        tx = self.tracker.get_by_id(tx_id)
        if not tx:
            print(f"  Transaction '{tx_id}' not found.")
            return
        print(f"  Current: {tx.date} | {tx.type.value} | {tx.category} | {format_money(tx.amount, self.symbol)} | {tx.description}")
        print("  Leave blank to keep current value.")
        try:
            amt_str = input(f"  Amount [{tx.amount}]: ").strip()
            amount = parse_amount(amt_str) if amt_str else None
            date_str = input(f"  Date [{tx.date.isoformat()}]: ").strip()
            new_date = parse_date(date_str) if date_str else None
            cat = input(f"  Category [{tx.category}]: ").strip() or None
            desc = input(f"  Description [{tx.description}]: ").strip()
            desc = desc if desc else None
            pay = input(f"  Payment method [{tx.payment_method}]: ").strip() or None
            tags_str = input(f"  Tags (comma-sep) [{', '.join(tx.tags)}]: ").strip()
            tags = [t.strip() for t in tags_str.split(",") if t.strip()] if tags_str else None
            notes = input(f"  Notes [{tx.notes}]: ").strip()
            notes = notes if notes else None

            kwargs = {}
            if amount is not None:
                kwargs["amount"] = amount
            if new_date is not None:
                kwargs["date"] = new_date
            if cat:
                kwargs["category"] = cat
            if desc is not None:
                kwargs["description"] = desc
            if pay:
                kwargs["payment_method"] = pay
            if tags is not None:
                kwargs["tags"] = tags
            if notes is not None:
                kwargs["notes"] = notes

            if kwargs:
                self.tracker.edit_transaction(tx_id, **kwargs)
                print("  Transaction updated successfully.")
            else:
                print("  No changes made.")
        except ValidationError as e:
            print(f"  Error: {e}")

    def _delete(self) -> None:
        print_header("Delete Transaction")
        tx_id = validate_id(input("  Transaction ID: "))
        tx = self.tracker.get_by_id(tx_id)
        if not tx:
            print(f"  Transaction '{tx_id}' not found.")
            return
        print(f"  {tx.date} | {tx.type.value} | {tx.category} | {format_money(tx.amount, self.symbol)} | {tx.description}")
        if confirm("  Confirm deletion? (y/n): "):
            self.tracker.delete_transaction(tx_id)
            print("  Transaction deleted.")
        else:
            print("  Deletion cancelled.")

    def _search(self) -> None:
        print_header("Search Transactions")
        query = input("  Search text (description, category, tags, notes, id): ").strip()
        results = self.tracker.search(query=query)
        print_transactions(results, self.symbol)

    def _filter(self) -> None:
        print_header("Filter Transactions")
        print("  Leave blank to skip a filter.")
        try:
            start_s = input("  Start date (YYYY-MM-DD): ").strip()
            end_s = input("  End date (YYYY-MM-DD): ").strip()
            cat = input("  Category: ").strip() or None
            type_s = input("  Type (expense/income): ").strip().lower() or None
            min_s = input("  Min amount: ").strip()
            max_s = input("  Max amount: ").strip()
            pay = input("  Payment method: ").strip() or None
            tag = input("  Tag: ").strip() or None

            start = parse_date(start_s) if start_s else None
            end = parse_date(end_s) if end_s else None
            tx_type = TransactionType(type_s) if type_s else None
            min_amt = parse_amount(min_s) if min_s else None
            max_amt = parse_amount(max_s) if max_s else None

            results = self.tracker.filter(
                start_date=start,
                end_date=end,
                category=cat,
                tx_type=tx_type,
                min_amount=min_amt,
                max_amount=max_amt,
                payment_method=pay,
                tag=tag,
            )
            print_transactions(results, self.symbol)
        except ValidationError as e:
            print(f"  Error: {e}")
        except ValueError as e:
            print(f"  Error: {e}")

    # ----- Reports -----

    def _print_summary(self, s: dict) -> None:
        print(f"  Total Income:      {format_money(s['total_income'], self.symbol)}")
        print(f"  Total Expenses:    {format_money(s['total_expenses'], self.symbol)}")
        print(f"  Net Balance:       {format_money(s['net_balance'], self.symbol)}")
        print(f"  Transactions:      {s['transaction_count']}")
        if s["average_expense"] is not None:
            print(f"  Average Expense:   {format_money(s['average_expense'], self.symbol)}")
        else:
            print("  Average Expense:   N/A (no expenses)")
        if s["largest_expense"] is not None:
            print(f"  Largest Expense:   {format_money(s['largest_expense'], self.symbol)}")
        if s["highest_spending_category"]:
            cat, amt = s["highest_spending_category"]
            print(f"  Top Category:      {cat} ({format_money(amt, self.symbol)})")
        if s.get("expense_by_category"):
            print("\n  Expense by Category:")
            for cat, amt in sorted(s["expense_by_category"].items(), key=lambda x: -x[1]):
                print(f"    {cat:<20} {format_money(amt, self.symbol)}")
        if s.get("income_by_category"):
            print("\n  Income by Category:")
            for cat, amt in sorted(s["income_by_category"].items(), key=lambda x: -x[1]):
                print(f"    {cat:<20} {format_money(amt, self.symbol)}")

    def _summary(self) -> None:
        print_header("Financial Summary (All Time)")
        gen = ReportGenerator(self.tracker.transactions)
        s = gen.summary()
        self._print_summary(s)
        print("\n  Note: Balance is calculated from recorded transactions only.")

    def _monthly(self) -> None:
        print_header("Monthly Report")
        try:
            ym = input(f"  Year-Month (YYYY-MM) [{date.today().strftime('%Y-%m')}]: ").strip()
            if not ym:
                year, month = date.today().year, date.today().month
            else:
                year, month = parse_year_month(ym)
            gen = ReportGenerator(self.tracker.transactions)
            report = gen.monthly_report(year, month)
            print(f"\n  Period: {report['period']}")
            self._print_summary(report)
            prev = report.get("previous", {})
            print(f"\n  Previous period ({prev.get('year')}-{prev.get('month', 0):02d}):")
            print(f"    Income:   {format_money(prev.get('total_income', 0), self.symbol)}")
            print(f"    Expenses: {format_money(prev.get('total_expenses', 0), self.symbol)}")
            print(f"    Net:      {format_money(prev.get('net_balance', 0), self.symbol)}")
        except ValidationError as e:
            print(f"  Error: {e}")

    def _yearly(self) -> None:
        print_header("Yearly Report")
        try:
            y = input(f"  Year [{date.today().year}]: ").strip()
            year = parse_year(y) if y else date.today().year
            gen = ReportGenerator(self.tracker.transactions)
            report = gen.yearly_report(year)
            print(f"\n  Period: {report['period']}")
            self._print_summary(report)
            prev = report.get("previous", {})
            print(f"\n  Previous year ({prev.get('year')}):")
            print(f"    Income:   {format_money(prev.get('total_income', 0), self.symbol)}")
            print(f"    Expenses: {format_money(prev.get('total_expenses', 0), self.symbol)}")
            print(f"    Net:      {format_money(prev.get('net_balance', 0), self.symbol)}")
        except ValidationError as e:
            print(f"  Error: {e}")

    def _custom_range(self) -> None:
        print_header("Custom Date-Range Report")
        try:
            start = parse_date(input("  Start date (YYYY-MM-DD): "))
            end = parse_date(input("  End date (YYYY-MM-DD): "))
            gen = ReportGenerator(self.tracker.transactions)
            report = gen.custom_range_report(start, end)
            print(f"\n  Period: {report['period']}")
            self._print_summary(report)
        except (ValidationError, ValueError) as e:
            print(f"  Error: {e}")

    # ----- Budgets -----

    def _manage_budgets(self) -> None:
        print_header("Manage Budgets")
        print("  1. Set overall monthly budget")
        print("  2. Set category monthly budget")
        print("  3. Delete a budget")
        print("  4. List budgets")
        print("  0. Back")
        choice = input("  Choice: ").strip()
        try:
            if choice == "1":
                amount = parse_amount(input("  Budget amount: "))
                ym = input(f"  Year-Month (YYYY-MM) [{date.today().strftime('%Y-%m')}]: ").strip()
                year, month = parse_year_month(ym) if ym else (date.today().year, date.today().month)
                self.budgets.set_budget(amount, year, month, None)
                print("  Overall budget set.")
            elif choice == "2":
                amount = parse_amount(input("  Budget amount: "))
                cat = input("  Category: ").strip()
                if not cat:
                    raise ValidationError("Category required.")
                ym = input(f"  Year-Month (YYYY-MM) [{date.today().strftime('%Y-%m')}]: ").strip()
                year, month = parse_year_month(ym) if ym else (date.today().year, date.today().month)
                self.budgets.set_budget(amount, year, month, cat)
                print(f"  Budget for '{cat}' set.")
            elif choice == "3":
                ym = input("  Year-Month (YYYY-MM): ").strip()
                year, month = parse_year_month(ym)
                cat = input("  Category (leave blank for overall): ").strip() or None
                self.budgets.delete_budget(year, month, cat)
                print("  Budget deleted.")
            elif choice == "4":
                for b in self.budgets.budgets:
                    cat = b.category or "Overall"
                    print(f"  {b.year}-{b.month:02d} | {cat:<20} {format_money(b.amount, self.symbol)}")
            else:
                return
        except ValidationError as e:
            print(f"  Error: {e}")

    def _budget_status(self) -> None:
        print_header("Budget Status")
        try:
            ym = input(f"  Year-Month (YYYY-MM) [{date.today().strftime('%Y-%m')}]: ").strip()
            year, month = parse_year_month(ym) if ym else (date.today().year, date.today().month)
            statuses = self.budgets.list_statuses(
                self.tracker.transactions, year, month, self.settings.warning_threshold
            )
            for s in statuses:
                print(f"\n  {s['category']} ({s['year']}-{s['month']:02d})")
                print(f"    Budget:    {format_money(s['budget'], self.symbol)}")
                print(f"    Spent:     {format_money(s['spent'], self.symbol)}")
                print(f"    Remaining: {format_money(s['remaining'], self.symbol)}")
                if s["overspent"] > 0:
                    print(f"    Overspent: {format_money(s['overspent'], self.symbol)}")
                print(f"    Used:      {s['percent_used']}%  [{s['status']}]")
                if s["warning"]:
                    print("    *** WARNING: Approaching or exceeding budget ***")
        except ValidationError as e:
            print(f"  Error: {e}")

    # ----- Recurring -----

    def _manage_recurring(self) -> None:
        print_header("Recurring Transactions")
        print("  1. Add recurring rule")
        print("  2. List rules")
        print("  3. Deactivate rule")
        print("  4. Activate rule")
        print("  5. Delete rule")
        print("  6. Process due now")
        print("  0. Back")
        choice = input("  Choice: ").strip()
        try:
            if choice == "1":
                desc = input("  Description: ").strip()
                if not desc:
                    raise ValidationError("Description required.")
                amount = parse_amount(input("  Amount: "))
                type_s = input("  Type (expense/income) [expense]: ").strip().lower() or "expense"
                tx_type = TransactionType(type_s)
                cats = (
                    self.categories.get_expense_categories()
                    if tx_type == TransactionType.EXPENSE
                    else self.categories.get_income_categories()
                )
                print("  Categories:", ", ".join(cats))
                cat = input("  Category: ").strip()
                if not cat:
                    raise ValidationError("Category required.")
                interval_s = input("  Interval (weekly/monthly) [monthly]: ").strip().lower() or "monthly"
                interval = RecurrenceInterval(interval_s)
                start = parse_date(
                    input(f"  Start date (YYYY-MM-DD) [{date.today().isoformat()}]: ").strip()
                    or date.today().isoformat()
                )
                end_s = input("  End date (YYYY-MM-DD, optional): ").strip()
                end = parse_optional_date(end_s) if end_s else None
                pay = input("  Payment method [Cash]: ").strip() or "Cash"
                rule = RecurringRule(
                    description=desc,
                    amount=amount,
                    category=cat,
                    type=tx_type,
                    interval=interval,
                    start_date=start,
                    end_date=end,
                    payment_method=pay,
                )
                self.recurring.add_rule(rule)
                print(f"  Rule created. ID: {rule.id}")
            elif choice == "2":
                for r in self.recurring.rules:
                    status = "active" if r.active else "inactive"
                    end = r.end_date.isoformat() if r.end_date else "none"
                    last = r.last_generated.isoformat() if r.last_generated else "never"
                    print(
                        f"  {r.id} | {r.description[:25]:<25} | {r.interval.value} | "
                        f"{format_money(r.amount, self.symbol)} | {status} | last={last} | end={end}"
                    )
            elif choice == "3":
                rid = validate_id(input("  Rule ID: "))
                self.recurring.deactivate(rid)
                print("  Rule deactivated.")
            elif choice == "4":
                rid = validate_id(input("  Rule ID: "))
                self.recurring.activate(rid)
                print("  Rule activated.")
            elif choice == "5":
                rid = validate_id(input("  Rule ID: "))
                if confirm("  Confirm delete? (y/n): "):
                    self.recurring.delete_rule(rid)
                    print("  Rule deleted.")
            elif choice == "6":
                new_txs = self.recurring.process_due()
                for tx in new_txs:
                    self.tracker.add_transaction(tx)
                print(f"  Generated {len(new_txs)} transaction(s).")
            else:
                return
        except (ValidationError, ValueError) as e:
            print(f"  Error: {e}")

    # ----- Export / Backup -----

    def _export(self) -> None:
        print_header("Export")
        print("  1. Export all transactions to CSV")
        print("  2. Export filtered transactions")
        print("  3. Export financial summary")
        print("  0. Back")
        choice = input("  Choice: ").strip()
        try:
            if choice == "1":
                name = input("  Filename [exports/transactions.csv]: ").strip() or "exports/transactions.csv"
                path = export_transactions(self.tracker.transactions, name)
                print(f"  Exported to {path}")
            elif choice == "2":
                print("  Enter filter criteria (leave blank to skip):")
                start_s = input("  Start date: ").strip()
                end_s = input("  End date: ").strip()
                cat = input("  Category: ").strip() or None
                start = parse_date(start_s) if start_s else None
                end = parse_date(end_s) if end_s else None
                results = self.tracker.filter(start_date=start, end_date=end, category=cat)
                name = input("  Filename [exports/filtered.csv]: ").strip() or "exports/filtered.csv"
                path = export_transactions(results, name)
                print(f"  Exported {len(results)} rows to {path}")
            elif choice == "3":
                gen = ReportGenerator(self.tracker.transactions)
                s = gen.summary()
                name = input("  Filename [exports/summary.csv]: ").strip() or "exports/summary.csv"
                path = export_summary_csv(s, name)
                print(f"  Exported to {path}")
            else:
                return
        except FileExistsError as e:
            print(f"  {e}")
            if confirm("  Overwrite? (y/n): "):
                # retry with overwrite
                pass  # simplified
        except Exception as e:
            print(f"  Error: {e}")

    def _backup(self) -> None:
        print_header("Backup Data")
        dest = input("  Backup directory [backups/backup_latest]: ").strip() or "backups/backup_latest"
        try:
            path = self.dm.create_backup(dest)
            print(f"  Backup created at {path}")
        except StorageError as e:
            print(f"  Error: {e}")

    def _restore(self) -> None:
        print_header("Restore Data")
        print("  WARNING: This will replace current data with the backup.")
        src = input("  Backup directory path: ").strip()
        if not src:
            print("  Cancelled.")
            return
        if not confirm("  Confirm restore? (y/n): "):
            print("  Cancelled.")
            return
        try:
            self.dm.restore_backup(src)
            self.tracker.reload()
            self.budgets.reload()
            self.recurring.reload()
            self.categories = CategoryManager(self.dm)
            print("  Data restored successfully.")
        except StorageError as e:
            print(f"  Restore failed (current data preserved): {e}")

    # ----- Categories / Settings / Help -----

    def _manage_categories(self) -> None:
        print_header("Manage Categories")
        print("  1. List categories")
        print("  2. Add category")
        print("  3. Rename category")
        print("  4. Remove category")
        print("  0. Back")
        choice = input("  Choice: ").strip()
        try:
            if choice == "1":
                print("  Expense:", ", ".join(self.categories.get_expense_categories()))
                print("  Income: ", ", ".join(self.categories.get_income_categories()))
            elif choice == "2":
                kind = input("  Kind (expense/income) [expense]: ").strip().lower() or "expense"
                name = input("  Name: ").strip()
                self.categories.add_category(name, kind)
                print("  Category added.")
            elif choice == "3":
                kind = input("  Kind (expense/income) [expense]: ").strip().lower() or "expense"
                old = input("  Current name: ").strip()
                new = input("  New name: ").strip()
                self.categories.rename_category(old, new, kind)
                print("  Category renamed.")
            elif choice == "4":
                kind = input("  Kind (expense/income) [expense]: ").strip().lower() or "expense"
                name = input("  Name: ").strip()
                self.categories.remove_category(name, kind)
                print("  Category removed (existing transactions unchanged).")
            else:
                return
        except ValidationError as e:
            print(f"  Error: {e}")

    def _settings_menu(self) -> None:
        print_header("Settings")
        s = self.settings.all()
        for k, v in s.items():
            print(f"  {k}: {v}")
        print("\n  1. Change budget warning threshold")
        print("  2. Toggle allow future dates")
        print("  3. Change currency symbol")
        print("  0. Back")
        choice = input("  Choice: ").strip()
        if choice == "1":
            val = input("  Threshold percent (e.g. 80): ").strip()
            try:
                t = int(val)
                if 1 <= t <= 100:
                    self.settings.set("budget_warning_threshold", t)
                    print("  Updated.")
                else:
                    print("  Must be 1-100.")
            except ValueError:
                print("  Invalid number.")
        elif choice == "2":
            current = self.settings.allow_future_dates
            self.settings.set("allow_future_dates", not current)
            print(f"  Allow future dates: {not current}")
        elif choice == "3":
            sym = input("  Symbol: ").strip()
            if sym:
                self.settings.set("currency_symbol", sym)
                self.symbol = sym
                print("  Updated.")

    def _help(self) -> None:
        print_header("Help")
        print("""
  PocketLedger helps you track personal income and expenses from the terminal.

  Quick start:
    1. Add expenses (option 1) and income (option 2).
    2. View everything with option 3.
    3. Set budgets (12) and check status (13).
    4. Generate reports (8-11).
    5. Export to CSV (15) or backup (16).

  Dates must be entered as YYYY-MM-DD (e.g. 2026-10-21).
  Amounts use up to 2 decimal places and must be positive.
  Data is stored as JSON files in the 'data/' directory.
  This application is NOT a substitute for bank records or professional advice.
        """)

    def _exit(self) -> None:
        print("\n  Thank you for using PocketLedger. Goodbye!")
        sys.exit(0)
