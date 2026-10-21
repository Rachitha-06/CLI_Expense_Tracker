"""Tests for ExpenseTracker."""

import unittest
import tempfile
from datetime import date
from decimal import Decimal
from pathlib import Path

from expense_tracker.models import Transaction, TransactionType
from expense_tracker.storage import DataManager
from expense_tracker.tracker import ExpenseTracker
from expense_tracker.validation import ValidationError


class TestTracker(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dm = DataManager(self.tmp.name)
        self.tracker = ExpenseTracker(self.dm)

    def tearDown(self):
        self.tmp.cleanup()

    def _make(self, amount="100", category="Food", d=None, ttype=TransactionType.EXPENSE, description="test"):
        return Transaction(
            amount=Decimal(amount),
            category=category,
            date=d or date(2026, 10, 15),
            type=ttype,
            description=description,
        )

    def test_add_and_get(self):
        t = self._make()
        self.tracker.add_transaction(t)
        found = self.tracker.get_by_id(t.id)
        self.assertIsNotNone(found)
        self.assertEqual(found.amount, Decimal("100"))

    def test_edit(self):
        t = self._make()
        self.tracker.add_transaction(t)
        self.tracker.edit_transaction(t.id, amount=Decimal("200"), description="changed")
        updated = self.tracker.get_by_id(t.id)
        self.assertEqual(updated.amount, Decimal("200"))
        self.assertEqual(updated.description, "changed")

    def test_edit_nonexistent(self):
        with self.assertRaises(ValidationError):
            self.tracker.edit_transaction("nope", amount=Decimal("1"))

    def test_delete(self):
        t = self._make()
        self.tracker.add_transaction(t)
        self.tracker.delete_transaction(t.id)
        self.assertIsNone(self.tracker.get_by_id(t.id))

    def test_delete_nonexistent(self):
        with self.assertRaises(ValidationError):
            self.tracker.delete_transaction("missing")

    def test_search(self):
        self.tracker.add_transaction(self._make(description="Lunch at cafe"))
        self.tracker.add_transaction(self._make(category="Travel", amount="500"))
        results = self.tracker.search(query="lunch")
        self.assertEqual(len(results), 1)
        results = self.tracker.search(query="travel")
        self.assertEqual(len(results), 1)

    def test_filter_date(self):
        self.tracker.add_transaction(self._make(d=date(2026, 10, 1)))
        self.tracker.add_transaction(self._make(d=date(2026, 10, 20)))
        self.tracker.add_transaction(self._make(d=date(2026, 11, 1)))
        results = self.tracker.filter(
            start_date=date(2026, 10, 1), end_date=date(2026, 10, 31)
        )
        self.assertEqual(len(results), 2)

    def test_filter_boundaries(self):
        self.tracker.add_transaction(self._make(d=date(2026, 10, 1)))
        self.tracker.add_transaction(self._make(d=date(2026, 10, 31)))
        results = self.tracker.filter(
            start_date=date(2026, 10, 1), end_date=date(2026, 10, 31)
        )
        self.assertEqual(len(results), 2)

    def test_filter_amount(self):
        self.tracker.add_transaction(self._make(amount="50"))
        self.tracker.add_transaction(self._make(amount="150"))
        results = self.tracker.filter(min_amount=Decimal("100"))
        self.assertEqual(len(results), 1)

    def test_filter_type(self):
        self.tracker.add_transaction(self._make(ttype=TransactionType.EXPENSE))
        self.tracker.add_transaction(
            self._make(ttype=TransactionType.INCOME, category="Salary")
        )
        results = self.tracker.filter(tx_type=TransactionType.INCOME)
        self.assertEqual(len(results), 1)

    def test_invalid_date_range(self):
        with self.assertRaises(ValidationError):
            self.tracker.filter(
                start_date=date(2026, 11, 1), end_date=date(2026, 10, 1)
            )

    def test_persist(self):
        t = self._make()
        self.tracker.add_transaction(t)
        # New tracker instance should load it
        t2 = ExpenseTracker(self.dm)
        self.assertEqual(len(t2.transactions), 1)


if __name__ == "__main__":
    unittest.main()
