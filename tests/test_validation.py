"""Tests for validation helpers."""

import unittest
from datetime import date
from decimal import Decimal

from expense_tracker.validation import (
    parse_amount,
    parse_date,
    parse_year_month,
    parse_year,
    validate_category_name,
    ValidationError,
)


class TestValidation(unittest.TestCase):
    def test_parse_amount_valid(self):
        self.assertEqual(parse_amount("250.00"), Decimal("250.00"))
        self.assertEqual(parse_amount("1,000.50"), Decimal("1000.50"))

    def test_parse_amount_invalid(self):
        with self.assertRaises(ValidationError):
            parse_amount("abc")
        with self.assertRaises(ValidationError):
            parse_amount("-10")
        with self.assertRaises(ValidationError):
            parse_amount("0")
        with self.assertRaises(ValidationError):
            parse_amount("1.999")

    def test_parse_date(self):
        self.assertEqual(parse_date("2026-10-21"), date(2026, 10, 21))
        with self.assertRaises(ValidationError):
            parse_date("21-10-2026")
        with self.assertRaises(ValidationError):
            parse_date("not-a-date")

    def test_parse_year_month(self):
        self.assertEqual(parse_year_month("2026-10"), (2026, 10))
        with self.assertRaises(ValidationError):
            parse_year_month("2026-13")

    def test_parse_year(self):
        self.assertEqual(parse_year("2026"), 2026)
        with self.assertRaises(ValidationError):
            parse_year("1999")

    def test_category_name(self):
        self.assertEqual(validate_category_name("  Food  "), "Food")
        with self.assertRaises(ValidationError):
            validate_category_name("")
        with self.assertRaises(ValidationError):
            validate_category_name("x" * 51)


if __name__ == "__main__":
    unittest.main()
