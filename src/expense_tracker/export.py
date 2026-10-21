"""
CSV export functionality with basic formula-injection protection.
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import List, Optional

from .models import Transaction


def _sanitize(value: str) -> str:
    """Prevent spreadsheet formula injection by prefixing risky cells."""
    if value and value[0] in ("=", "+", "-", "@"):
        return "'" + value
    return value


def export_transactions(
    transactions: List[Transaction],
    filepath: Path | str,
    overwrite: bool = False,
) -> Path:
    """
    Export transactions to CSV.
    Raises FileExistsError if file exists and overwrite is False.
    """
    path = Path(filepath)
    if path.exists() and not overwrite:
        raise FileExistsError(
            f"File already exists: {path}. Choose a different name or enable overwrite."
        )
    path.parent.mkdir(parents=True, exist_ok=True)

    headers = [
        "id",
        "date",
        "type",
        "category",
        "amount",
        "description",
        "payment_method",
        "tags",
        "notes",
        "created_at",
        "updated_at",
    ]

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        for t in transactions:
            writer.writerow(
                [
                    t.id,
                    t.date.isoformat(),
                    t.type.value,
                    _sanitize(t.category),
                    str(t.amount),  # preserve decimal precision
                    _sanitize(t.description),
                    _sanitize(t.payment_method),
                    ";".join(t.tags),
                    _sanitize(t.notes),
                    t.created_at.isoformat(),
                    t.updated_at.isoformat(),
                ]
            )
    return path


def export_summary_csv(
    summary: dict,
    filepath: Path | str,
    overwrite: bool = False,
) -> Path:
    """Export a simple category summary to CSV."""
    path = Path(filepath)
    if path.exists() and not overwrite:
        raise FileExistsError(f"File already exists: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Metric", "Value"])
        writer.writerow(["Total Income", str(summary.get("total_income", "0"))])
        writer.writerow(["Total Expenses", str(summary.get("total_expenses", "0"))])
        writer.writerow(["Net Balance", str(summary.get("net_balance", "0"))])
        writer.writerow(["Transaction Count", summary.get("transaction_count", 0)])
        writer.writerow([])
        writer.writerow(["Category", "Type", "Amount"])
        for cat, amt in summary.get("income_by_category", {}).items():
            writer.writerow([_sanitize(cat), "income", str(amt)])
        for cat, amt in summary.get("expense_by_category", {}).items():
            writer.writerow([_sanitize(cat), "expense", str(amt)])
    return path
