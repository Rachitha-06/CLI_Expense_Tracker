"""Tests for budget management."""

import unittest
import tempfile
from datetime import date
from decimal import Decimal

from expense_tracker.models import Transaction, TransactionType, Budget
from expense_tracker.storage import DataManager
from expense_tracker.budgets import BudgetManager


class TestBudgets(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dm = DataManager(self.tmp.name)
        self.bm = BudgetManager(self.dm)
        self.txs = [
            Transaction(
                amount=Decimal("200"),
                category="Food",
                date=date(2026, 10, 5),
                type=TransactionType.EXPENSE,
            ),
            Transaction(
                amount=Decimal("100"),
                category="Food",
                date=date(2026, 10, 12),
                type=TransactionType.EXPENSE,
            ),
            Transaction(
                amount=Decimal("50"),
                category="Travel",
                date=date(2026, 10, 8),
                type=TransactionType.EXPENSE,
            ),
        ]

    def tearDown(self):
        self.tmp.cleanup()

    def test_set_and_get(self):
        b = self.bm.set_budget(Decimal("3000"), 2026, 10)
        self.assertEqual(b.amount, Decimal("3000"))
        found = self.bm.get_budget(2026, 10)
        self.assertIsNotNone(found)
        self.assertEqual(found.amount, Decimal("3000"))

    def test_category_budget(self):
        self.bm.set_budget(Decimal("500"), 2026, 10, "Food")
        status = self.bm.get_status(self.txs, 2026, 10, "Food")
        self.assertEqual(status["spent"], Decimal("300"))
        self.assertEqual(status["remaining"], Decimal("200"))
        self.assertEqual(status["percent_used"], Decimal("60.00"))
        self.assertEqual(status["status"], "ok")

    def test_warning_threshold(self):
        self.bm.set_budget(Decimal("350"), 2026, 10, "Food")
        status = self.bm.get_status(self.txs, 2026, 10, "Food", warning_threshold=80)
        # 300/350 ≈ 85.71%
        self.assertTrue(status["warning"])
        self.assertEqual(status["status"], "warning")

    def test_overspending(self):
        self.bm.set_budget(Decimal("200"), 2026, 10, "Food")
        status = self.bm.get_status(self.txs, 2026, 10, "Food")
        self.assertEqual(status["overspent"], Decimal("100"))
        self.assertEqual(status["remaining"], Decimal("0.00"))
        self.assertEqual(status["status"], "over")

    def test_exact_budget(self):
        self.bm.set_budget(Decimal("300"), 2026, 10, "Food")
        status = self.bm.get_status(self.txs, 2026, 10, "Food")
        self.assertEqual(status["remaining"], Decimal("0.00"))
        self.assertEqual(status["overspent"], Decimal("0.00"))
        self.assertEqual(status["percent_used"], Decimal("100.00"))

    def test_no_expenses(self):
        self.bm.set_budget(Decimal("1000"), 2026, 10, "Healthcare")
        status = self.bm.get_status(self.txs, 2026, 10, "Healthcare")
        self.assertEqual(status["spent"], Decimal("0.00"))
        self.assertEqual(status["remaining"], Decimal("1000"))

    def test_no_budget(self):
        status = self.bm.get_status(self.txs, 2026, 10, "Food")
        self.assertEqual(status["status"], "no_budget")
        self.assertEqual(status["budget"], Decimal("0.00"))


if __name__ == "__main__":
    unittest.main()
