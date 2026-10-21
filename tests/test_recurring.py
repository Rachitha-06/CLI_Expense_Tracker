"""Tests for recurring transactions."""

import unittest
import tempfile
from datetime import date, timedelta
from decimal import Decimal

from expense_tracker.models import (
    RecurringRule,
    RecurrenceInterval,
    TransactionType,
)
from expense_tracker.storage import DataManager
from expense_tracker.recurring import RecurringTransactionManager


class TestRecurring(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dm = DataManager(self.tmp.name)
        self.rm = RecurringTransactionManager(self.dm)

    def tearDown(self):
        self.tmp.cleanup()

    def test_weekly(self):
        start = date(2026, 10, 1)
        rule = RecurringRule(
            description="Weekly allowance",
            amount=Decimal("100"),
            category="Allowance",
            type=TransactionType.INCOME,
            interval=RecurrenceInterval.WEEKLY,
            start_date=start,
        )
        self.rm.add_rule(rule)
        # Process up to 2 weeks later
        as_of = start + timedelta(days=14)
        txs = self.rm.process_due(as_of)
        # start, +7, +14 => 3 occurrences
        self.assertEqual(len(txs), 3)
        self.assertEqual(txs[0].date, start)
        self.assertEqual(txs[1].date, start + timedelta(days=7))
        self.assertEqual(txs[2].date, start + timedelta(days=14))

    def test_monthly(self):
        start = date(2026, 1, 15)
        rule = RecurringRule(
            description="Rent",
            amount=Decimal("15000"),
            category="Housing",
            type=TransactionType.EXPENSE,
            interval=RecurrenceInterval.MONTHLY,
            start_date=start,
        )
        self.rm.add_rule(rule)
        as_of = date(2026, 3, 20)
        txs = self.rm.process_due(as_of)
        self.assertEqual(len(txs), 3)  # Jan, Feb, Mar
        self.assertEqual(txs[0].date, date(2026, 1, 15))
        self.assertEqual(txs[1].date, date(2026, 2, 15))
        self.assertEqual(txs[2].date, date(2026, 3, 15))

    def test_month_end(self):
        start = date(2026, 1, 31)
        rule = RecurringRule(
            description="Month-end bill",
            amount=Decimal("50"),
            category="Utilities",
            type=TransactionType.EXPENSE,
            interval=RecurrenceInterval.MONTHLY,
            start_date=start,
        )
        self.rm.add_rule(rule)
        as_of = date(2026, 3, 5)
        txs = self.rm.process_due(as_of)
        # Jan 31, Feb 28 (2026 not leap), Mar 31 not yet
        self.assertEqual(len(txs), 2)
        self.assertEqual(txs[0].date, date(2026, 1, 31))
        self.assertEqual(txs[1].date, date(2026, 2, 28))

    def test_end_date(self):
        start = date(2026, 1, 1)
        end = date(2026, 2, 1)
        rule = RecurringRule(
            description="Short",
            amount=Decimal("10"),
            category="Other",
            type=TransactionType.EXPENSE,
            interval=RecurrenceInterval.MONTHLY,
            start_date=start,
            end_date=end,
        )
        self.rm.add_rule(rule)
        txs = self.rm.process_due(date(2026, 5, 1))
        self.assertEqual(len(txs), 2)  # Jan 1 and Feb 1

    def test_no_duplicates(self):
        start = date(2026, 10, 1)
        rule = RecurringRule(
            description="Sub",
            amount=Decimal("99"),
            category="Subscriptions",
            type=TransactionType.EXPENSE,
            interval=RecurrenceInterval.MONTHLY,
            start_date=start,
        )
        self.rm.add_rule(rule)
        txs1 = self.rm.process_due(date(2026, 10, 15))
        self.assertEqual(len(txs1), 1)
        # Process again same day
        txs2 = self.rm.process_due(date(2026, 10, 15))
        self.assertEqual(len(txs2), 0)

    def test_inactive(self):
        rule = RecurringRule(
            description="Old",
            amount=Decimal("10"),
            category="Other",
            type=TransactionType.EXPENSE,
            interval=RecurrenceInterval.WEEKLY,
            start_date=date(2026, 1, 1),
            active=False,
        )
        self.rm.add_rule(rule)
        txs = self.rm.process_due(date(2026, 2, 1))
        self.assertEqual(len(txs), 0)


if __name__ == "__main__":
    unittest.main()
