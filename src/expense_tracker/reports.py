"""
Financial summaries and period reports.
"""

from __future__ import annotations

from collections import defaultdict
from datetime import date
from decimal import Decimal
from typing import Dict, List, Optional, Tuple

from .models import Transaction, TransactionType


class ReportGenerator:
    """Generates financial summaries and period reports."""

    def __init__(self, transactions: List[Transaction]) -> None:
        self.transactions = transactions

    def summary(
        self,
        start: Optional[date] = None,
        end: Optional[date] = None,
    ) -> Dict:
        """
        Overall financial summary for optional date range.
        Formulas:
          Total Income   = sum of income amounts
          Total Expenses = sum of expense amounts
          Net Balance    = Total Income - Total Expenses
          Average Expense = Total Expenses / count of expense transactions
        """
        txs = self._filter_range(start, end)
        income = Decimal("0.00")
        expenses = Decimal("0.00")
        expense_amounts: List[Decimal] = []
        income_by_cat: Dict[str, Decimal] = defaultdict(lambda: Decimal("0.00"))
        expense_by_cat: Dict[str, Decimal] = defaultdict(lambda: Decimal("0.00"))

        for t in txs:
            if t.type == TransactionType.INCOME:
                income += t.amount
                income_by_cat[t.category] += t.amount
            else:
                expenses += t.amount
                expense_amounts.append(t.amount)
                expense_by_cat[t.category] += t.amount

        net = income - expenses
        count = len(txs)
        exp_count = len(expense_amounts)
        avg_exp = (
            (expenses / exp_count).quantize(Decimal("0.01"))
            if exp_count > 0
            else None
        )
        largest = max(expense_amounts) if expense_amounts else None
        smallest = min(expense_amounts) if expense_amounts else None
        highest_cat = None
        if expense_by_cat:
            highest_cat = max(expense_by_cat.items(), key=lambda x: x[1])

        return {
            "total_income": income,
            "total_expenses": expenses,
            "net_balance": net,
            "transaction_count": count,
            "expense_count": exp_count,
            "average_expense": avg_exp,
            "largest_expense": largest,
            "smallest_expense": smallest,
            "highest_spending_category": highest_cat,
            "income_by_category": dict(income_by_cat),
            "expense_by_category": dict(expense_by_cat),
            "start": start,
            "end": end,
        }

    def monthly_report(self, year: int, month: int) -> Dict:
        """Report for a specific year-month."""
        start = date(year, month, 1)
        if month == 12:
            end = date(year + 1, 1, 1)
        else:
            end = date(year, month + 1, 1)
        # Use exclusive end by filtering < end
        txs = [t for t in self.transactions if start <= t.date < end]
        gen = ReportGenerator(txs)
        report = gen.summary()
        report["year"] = year
        report["month"] = month
        report["period"] = f"{year}-{month:02d}"

        # Previous period comparison
        if month == 1:
            prev_year, prev_month = year - 1, 12
        else:
            prev_year, prev_month = year, month - 1
        prev = self.monthly_report_simple(prev_year, prev_month)
        report["previous"] = {
            "year": prev_year,
            "month": prev_month,
            "total_income": prev["total_income"],
            "total_expenses": prev["total_expenses"],
            "net_balance": prev["net_balance"],
        }
        return report

    def monthly_report_simple(self, year: int, month: int) -> Dict:
        """Lightweight monthly without previous comparison (avoid recursion)."""
        start = date(year, month, 1)
        if month == 12:
            end = date(year + 1, 1, 1)
        else:
            end = date(year, month + 1, 1)
        txs = [t for t in self.transactions if start <= t.date < end]
        return ReportGenerator(txs).summary()

    def yearly_report(self, year: int) -> Dict:
        """Report for a full year."""
        start = date(year, 1, 1)
        end = date(year + 1, 1, 1)
        txs = [t for t in self.transactions if start <= t.date < end]
        gen = ReportGenerator(txs)
        report = gen.summary()
        report["year"] = year
        report["period"] = str(year)

        prev = ReportGenerator(
            [t for t in self.transactions if date(year - 1, 1, 1) <= t.date < date(year, 1, 1)]
        ).summary()
        report["previous"] = {
            "year": year - 1,
            "total_income": prev["total_income"],
            "total_expenses": prev["total_expenses"],
            "net_balance": prev["net_balance"],
        }
        return report

    def custom_range_report(self, start: date, end: date) -> Dict:
        if start > end:
            raise ValueError("Start date cannot be after end date.")
        report = self.summary(start, end)
        report["period"] = f"{start.isoformat()} to {end.isoformat()}"
        return report

    def _filter_range(
        self, start: Optional[date], end: Optional[date]
    ) -> List[Transaction]:
        txs = self.transactions
        if start:
            txs = [t for t in txs if t.date >= start]
        if end:
            txs = [t for t in txs if t.date <= end]
        return txs
