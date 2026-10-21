"""Tests for data models."""

import unittest
from datetime import date, datetime
from decimal import Decimal

from expense_tracker.models import (
    Transaction,
    TransactionType,
    Budget,
    RecurringRule,
    RecurrenceInterval,
    generate_id,
)


class TestTransaction(unittest.TestCase):
    def test_create_expense(self):
        t = Transaction(
            amount=Decimal("250.00"),
            category="Food",
            date=date(2026, 10, 21),
            type=TransactionType.EXPENSE,
            description="Lunch",
        )
        self.assertEqual(t.amount, Decimal("250.00"))
        self.assertEqual(t.type, TransactionType.EXPENSE)
        self.assertTrue(t.id)

    def test_create_income(self):
        t = Transaction(
            amount=Decimal("5000"),
            category="Salary",
            date=date(2026, 10, 1),
            type=TransactionType.INCOME,
        )
        self.assertEqual(t.type, TransactionType.INCOME)

    def test_reject_negative(self):
        with self.assertRaises(ValueError):
            Transaction(
                amount=Decimal("-10"),
                category="Food",
                date=date.today(),
                type=TransactionType.EXPENSE,
            )

    def test_reject_zero(self):
        with self.assertRaises(ValueError):
            Transaction(
                amount=Decimal("0"),
                category="Food",
                date=date.today(),
                type=TransactionType.EXPENSE,
            )

    def test_unique_ids(self):
        ids = {generate_id() for _ in range(50)}
        self.assertEqual(len(ids), 50)

    def test_to_from_dict(self):
        t = Transaction(
            amount=Decimal("99.99"),
            category="Shopping",
            date=date(2026, 5, 5),
            type=TransactionType.EXPENSE,
            description="Book",
            tags=["study"],
        )
        d = t.to_dict()
        self.assertEqual(d["amount"], "99.99")
        t2 = Transaction.from_dict(d)
        self.assertEqual(t2.amount, t.amount)
        self.assertEqual(t2.category, t.category)
        self.assertEqual(t2.tags, t.tags)

    def test_update(self):
        t = Transaction(
            amount=Decimal("10"),
            category="Food",
            date=date.today(),
            type=TransactionType.EXPENSE,
        )
        t.update(amount=Decimal("20"), description="Updated")
        self.assertEqual(t.amount, Decimal("20"))
        self.assertEqual(t.description, "Updated")


class TestBudget(unittest.TestCase):
    def test_create(self):
        b = Budget(amount=Decimal("3000"), year=2026, month=10)
        self.assertEqual(b.amount, Decimal("3000"))
        self.assertIsNone(b.category)

    def test_reject_negative(self):
        with self.assertRaises(ValueError):
            Budget(amount=Decimal("-1"), year=2026, month=1)


class TestRecurringRule(unittest.TestCase):
    def test_create(self):
        r = RecurringRule(
            description="Netflix",
            amount=Decimal("649"),
            category="Subscriptions",
            type=TransactionType.EXPENSE,
            interval=RecurrenceInterval.MONTHLY,
            start_date=date(2026, 1, 15),
        )
        self.assertTrue(r.active)
        self.assertIsNone(r.last_generated)


if __name__ == "__main__":
    unittest.main()
