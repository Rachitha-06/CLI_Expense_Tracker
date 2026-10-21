"""
Input validation helpers for PocketLedger.
"""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from typing import Optional, Tuple


class ValidationError(Exception):
    """Raised when user input fails validation."""
    pass


def parse_amount(value: str) -> Decimal:
    """Parse and validate a monetary amount. Must be positive."""
    value = value.strip().replace(",", "")
    if not value:
        raise ValidationError("Amount cannot be empty.")
    try:
        amount = Decimal(value)
    except InvalidOperation:
        raise ValidationError(f"Invalid amount: '{value}'. Enter a valid number.")
    if amount <= 0:
        raise ValidationError("Amount must be greater than zero.")
    # Limit to 2 decimal places for currency
    if amount.as_tuple().exponent < -2:
        raise ValidationError("Amount may have at most 2 decimal places.")
    return amount.quantize(Decimal("0.01"))


def parse_date(value: str, allow_future: bool = True) -> date:
    """Parse a date in YYYY-MM-DD format."""
    value = value.strip()
    if not value:
        raise ValidationError("Date cannot be empty.")
    try:
        d = date.fromisoformat(value)
    except ValueError:
        raise ValidationError(
            f"Invalid date '{value}'. Use YYYY-MM-DD format (e.g., 2026-10-21)."
        )
    if not allow_future and d > date.today():
        raise ValidationError("Future dates are not allowed.")
    return d


def parse_optional_date(value: str) -> Optional[date]:
    """Parse an optional date; empty string returns None."""
    value = value.strip()
    if not value:
        return None
    return parse_date(value)


def parse_year_month(value: str) -> Tuple[int, int]:
    """Parse YYYY-MM into (year, month)."""
    value = value.strip()
    try:
        parts = value.split("-")
        if len(parts) != 2:
            raise ValueError
        year = int(parts[0])
        month = int(parts[1])
        if month < 1 or month > 12:
            raise ValueError
        if year < 2000 or year > 2100:
            raise ValueError
        return year, month
    except ValueError:
        raise ValidationError(
            f"Invalid year-month '{value}'. Use YYYY-MM (e.g., 2026-10)."
        )


def parse_year(value: str) -> int:
    """Parse a year."""
    value = value.strip()
    try:
        year = int(value)
        if year < 2000 or year > 2100:
            raise ValueError
        return year
    except ValueError:
        raise ValidationError(f"Invalid year '{value}'. Enter a year between 2000 and 2100.")


def validate_category_name(name: str) -> str:
    """Validate and normalize a category name."""
    name = name.strip()
    if not name:
        raise ValidationError("Category name cannot be empty.")
    if len(name) > 50:
        raise ValidationError("Category name is too long (max 50 characters).")
    return name


def validate_id(value: str) -> str:
    """Validate a transaction ID string."""
    value = value.strip()
    if not value:
        raise ValidationError("ID cannot be empty.")
    return value


def confirm(prompt: str = "Are you sure? (y/n): ") -> bool:
    """Ask for yes/no confirmation."""
    while True:
        answer = input(prompt).strip().lower()
        if answer in ("y", "yes"):
            return True
        if answer in ("n", "no"):
            return False
        print("Please enter 'y' or 'n'.")
