"""Tests for storage layer."""

import unittest
import tempfile
import json
from datetime import date
from decimal import Decimal
from pathlib import Path

from expense_tracker.models import Transaction, TransactionType
from expense_tracker.storage import DataManager, StorageError


class TestStorage(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dm = DataManager(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_save_load_transactions(self):
        t = Transaction(
            amount=Decimal("42.50"),
            category="Food",
            date=date(2026, 10, 21),
            type=TransactionType.EXPENSE,
            description="Test",
        )
        self.dm.save_transactions([t])
        loaded = self.dm.load_transactions()
        self.assertEqual(len(loaded), 1)
        self.assertEqual(loaded[0].amount, Decimal("42.50"))
        self.assertEqual(loaded[0].id, t.id)

    def test_missing_file(self):
        loaded = self.dm.load_transactions()
        self.assertEqual(loaded, [])

    def test_malformed_json(self):
        path = Path(self.tmp.name) / "transactions.json"
        path.write_text("{not valid json", encoding="utf-8")
        with self.assertRaises(StorageError):
            self.dm.load_transactions()

    def test_invalid_record_skipped(self):
        path = Path(self.tmp.name) / "transactions.json"
        data = [
            {
                "id": "abc",
                "type": "expense",
                "amount": "10.00",
                "category": "Food",
                "date": "2026-10-21",
                "description": "",
                "payment_method": "Cash",
                "tags": [],
                "notes": "",
                "created_at": "2026-10-21T10:00:00",
                "updated_at": "2026-10-21T10:00:00",
            },
            {"bad": "record"},
        ]
        path.write_text(json.dumps(data), encoding="utf-8")
        loaded = self.dm.load_transactions()
        self.assertEqual(len(loaded), 1)

    def test_backup_restore(self):
        t = Transaction(
            amount=Decimal("10"),
            category="Food",
            date=date.today(),
            type=TransactionType.EXPENSE,
        )
        self.dm.save_transactions([t])
        backup_dir = Path(self.tmp.name) / "backup"
        self.dm.create_backup(backup_dir)
        # Clear current
        self.dm.save_transactions([])
        self.assertEqual(len(self.dm.load_transactions()), 0)
        # Restore
        self.dm.restore_backup(backup_dir)
        loaded = self.dm.load_transactions()
        self.assertEqual(len(loaded), 1)
        self.assertEqual(loaded[0].amount, Decimal("10"))

    def test_reject_invalid_backup(self):
        bad = Path(self.tmp.name) / "bad_backup"
        bad.mkdir()
        (bad / "transactions.json").write_text("not json", encoding="utf-8")
        with self.assertRaises(StorageError):
            self.dm.restore_backup(bad)


if __name__ == "__main__":
    unittest.main()
