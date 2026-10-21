"""Tests for financial reports."""

import unittest
from datetime import date
from decimal import Decimal

from expense_tracker.models import Transaction, TransactionType
from expense_tracker.reports import ReportGenerator


class TestReports(unittest.TestCase):
    def setUp(self):
        self.txs = [
            Transaction(
                amount=Decimal("5000"),
                category="Salary",
                date=date(2026, 10, 1),
                type=TransactionType.INCOME,
            ),
            Transaction(
                amount=Decimal("200"),
                category="Food",
                date=date(2026, 10, 5),
                type=TransactionType.EXPENSE,
            ),
            Transaction(
                amount=Decimal("150"),
                category="Food",
                date=date(2026, 10, 10),
                type=TransactionType.EXPENSE,
            ),
            Transaction(
                amount=Decimal("500"),
                category="Travel",
                date=date(2026, 10, 15),
                type=TransactionType.EXPENSE,
            ),
            Transaction(
                amount=Decimal("100"),
                category="Food",
                date=date(2026, 9, 20),
                type=TransactionType.EXPENSE,
            ),
        ]
        self.gen = ReportGenerator(self.txs)

    def test_total_income(self):
        s = self.gen.summary()
        self.assertEqual(s["total_income"], Decimal("5000"))

    def test_total_expenses(self):
        s = self.gen.summary()
        self.assertEqual(s["total_expenses"], Decimal("950"))

    def test_net_balance(self):
        s = self.gen.summary()
        self.assertEqual(s["net_balance"], Decimal("4050"))

    def test_average_expense(self):
        s = self.gen.summary()
        # 950 / 4 = 237.50
        self.assertEqual(s["average_expense"], Decimal("237.50"))

    def test_largest_expense(self):
        s = self.gen.summary()
        self.assertEqual(s["largest_expense"], Decimal("500"))

    def test_expense_by_category(self):
        s = self.gen.summary()
        self.assertEqual(s["expense_by_category"]["Food"], Decimal("450"))
        self.assertEqual(s["expense_by_category"]["Travel"], Decimal("500"))

    def test_highest_category(self):
        s = self.gen.summary()
        cat, amt = s["highest_spending_category"]
        self.assertEqual(cat, "Travel")
        self.assertEqual(amt, Decimal("500"))

    def test_empty(self):
        gen = ReportGenerator([])
        s = gen.summary()
        self.assertEqual(s["total_income"], Decimal("0.00"))
        self.assertEqual(s["total_expenses"], Decimal("0.00"))
        self.assertIsNone(s["average_expense"])

    def test_income_only(self):
        gen = ReportGenerator([self.txs[0]])
        s = gen.summary()
        self.assertEqual(s["total_expenses"], Decimal("0.00"))
        self.assertIsNone(s["average_expense"])

    def test_monthly(self):
        report = self.gen.monthly_report(2026, 10)
        self.assertEqual(report["total_income"], Decimal("5000"))
        self.assertEqual(report["total_expenses"], Decimal("850"))
        self.assertEqual(report["year"], 2026)
        self.assertEqual(report["month"], 10)

    def test_yearly(self):
        report = self.gen.yearly_report(2026)
        self.assertEqual(report["total_expenses"], Decimal("950"))

    def test_precision(self):
        txs = [
            Transaction(
                amount=Decimal("0.10"),
                category="Other",
                date=date.today(),
                type=TransactionType.EXPENSE,
            ),
            Transaction(
                amount=Decimal("0.20"),
                category="Other",
                date=date.today(),
                type=TransactionType.EXPENSE,
            ),
        ]
        s = ReportGenerator(txs).summary()
        self.assertEqual(s["total_expenses"], Decimal("0.30"))


if __name__ == "__main__":
    unittest.main()
