"""Tests for CSV export."""

import unittest
import tempfile
import csv
from datetime import date
from decimal import Decimal
from pathlib import Path

from expense_tracker.models import Transaction, TransactionType
from expense_tracker.export import export_transactions, export_summary_csv
from expense_tracker.reports import ReportGenerator


class TestExport(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.txs = [
            Transaction(
                amount=Decimal("99.99"),
                category="Food",
                date=date(2026, 10, 21),
                type=TransactionType.EXPENSE,
                description="Lunch",
                tags=["college"],
            ),
            Transaction(
                amount=Decimal("5000.00"),
                category="Salary",
                date=date(2026, 10, 1),
                type=TransactionType.INCOME,
                description="October salary",
            ),
        ]

    def tearDown(self):
        self.tmp.cleanup()

    def test_export_headers_and_precision(self):
        path = Path(self.tmp.name) / "out.csv"
        export_transactions(self.txs, path)
        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            headers = next(reader)
            self.assertIn("id", headers)
            self.assertIn("amount", headers)
            rows = list(reader)
            self.assertEqual(len(rows), 2)
            # amount is string preserving precision
            amounts = [r[headers.index("amount")] for r in rows]
            self.assertIn("99.99", amounts)
            self.assertIn("5000.00", amounts)

    def test_export_empty(self):
        path = Path(self.tmp.name) / "empty.csv"
        export_transactions([], path)
        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            headers = next(reader)
            rows = list(reader)
            self.assertEqual(len(rows), 0)

    def test_no_overwrite(self):
        path = Path(self.tmp.name) / "exists.csv"
        path.write_text("old", encoding="utf-8")
        with self.assertRaises(FileExistsError):
            export_transactions(self.txs, path, overwrite=False)

    def test_formula_injection(self):
        tx = Transaction(
            amount=Decimal("1"),
            category="=cmd",
            date=date.today(),
            type=TransactionType.EXPENSE,
            description="+1+1",
        )
        path = Path(self.tmp.name) / "safe.csv"
        export_transactions([tx], path)
        content = path.read_text(encoding="utf-8")
        self.assertIn("'=cmd", content)
        self.assertIn("'+1+1", content)

    def test_summary_export(self):
        gen = ReportGenerator(self.txs)
        s = gen.summary()
        path = Path(self.tmp.name) / "summary.csv"
        export_summary_csv(s, path)
        self.assertTrue(path.exists())


if __name__ == "__main__":
    unittest.main()
