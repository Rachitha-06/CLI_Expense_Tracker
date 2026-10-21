"""
Persistent storage layer using JSON files.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional

from .models import (
    Budget,
    RecurringRule,
    Transaction,
    DEFAULT_EXPENSE_CATEGORIES,
    DEFAULT_INCOME_CATEGORIES,
)


class StorageError(Exception):
    """Raised on storage-related failures."""
    pass


class DataManager:
    """Handles loading and saving of all application data."""

    def __init__(self, data_dir: Path | str = "data") -> None:
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.transactions_file = self.data_dir / "transactions.json"
        self.categories_file = self.data_dir / "categories.json"
        self.budgets_file = self.data_dir / "budgets.json"
        self.recurring_file = self.data_dir / "recurring_transactions.json"
        self.settings_file = self.data_dir / "settings.json"

    def _safe_write(self, path: Path, data: Any) -> None:
        """Write JSON atomically using a temporary file."""
        tmp = path.with_suffix(".tmp")
        try:
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            tmp.replace(path)
        except OSError as e:
            if tmp.exists():
                tmp.unlink(missing_ok=True)
            raise StorageError(f"Failed to write {path.name}: {e}") from e

    def _load_json(self, path: Path, default: Any) -> Any:
        """Load JSON or return default if missing/malformed."""
        if not path.exists():
            return default
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            raise StorageError(f"Failed to load {path.name}: {e}") from e

    # --- Transactions ---

    def load_transactions(self) -> List[Transaction]:
        raw = self._load_json(self.transactions_file, [])
        transactions = []
        for item in raw:
            try:
                transactions.append(Transaction.from_dict(item))
            except (KeyError, ValueError, TypeError) as e:
                # Skip invalid records but continue
                continue
        return transactions

    def save_transactions(self, transactions: List[Transaction]) -> None:
        data = [t.to_dict() for t in transactions]
        self._safe_write(self.transactions_file, data)

    # --- Categories ---

    def load_categories(self) -> Dict[str, List[str]]:
        default = {
            "expense": list(DEFAULT_EXPENSE_CATEGORIES),
            "income": list(DEFAULT_INCOME_CATEGORIES),
        }
        raw = self._load_json(self.categories_file, default)
        if not isinstance(raw, dict):
            return default
        return {
            "expense": raw.get("expense", default["expense"]),
            "income": raw.get("income", default["income"]),
        }

    def save_categories(self, categories: Dict[str, List[str]]) -> None:
        self._safe_write(self.categories_file, categories)

    # --- Budgets ---

    def load_budgets(self) -> List[Budget]:
        raw = self._load_json(self.budgets_file, [])
        budgets = []
        for item in raw:
            try:
                budgets.append(Budget.from_dict(item))
            except (KeyError, ValueError, TypeError):
                continue
        return budgets

    def save_budgets(self, budgets: List[Budget]) -> None:
        data = [b.to_dict() for b in budgets]
        self._safe_write(self.budgets_file, data)

    # --- Recurring ---

    def load_recurring(self) -> List[RecurringRule]:
        raw = self._load_json(self.recurring_file, [])
        rules = []
        for item in raw:
            try:
                rules.append(RecurringRule.from_dict(item))
            except (KeyError, ValueError, TypeError):
                continue
        return rules

    def save_recurring(self, rules: List[RecurringRule]) -> None:
        data = [r.to_dict() for r in rules]
        self._safe_write(self.recurring_file, data)

    # --- Settings ---

    def load_settings(self) -> Dict[str, Any]:
        default = {
            "budget_warning_threshold": 80,
            "allow_future_dates": True,
            "currency_symbol": "₹",
            "date_format": "%Y-%m-%d",
        }
        raw = self._load_json(self.settings_file, default)
        if not isinstance(raw, dict):
            return default
        default.update(raw)
        return default

    def save_settings(self, settings: Dict[str, Any]) -> None:
        self._safe_write(self.settings_file, settings)

    # --- Backup / Restore ---

    def create_backup(self, backup_path: Path | str) -> Path:
        """Create a ZIP-like directory backup of all data files."""
        backup_path = Path(backup_path)
        backup_path.mkdir(parents=True, exist_ok=True)
        for src in [
            self.transactions_file,
            self.categories_file,
            self.budgets_file,
            self.recurring_file,
            self.settings_file,
        ]:
            if src.exists():
                shutil.copy2(src, backup_path / src.name)
        return backup_path

    def restore_backup(self, backup_path: Path | str) -> None:
        """Restore from a backup directory after validating structure."""
        backup_path = Path(backup_path)
        if not backup_path.is_dir():
            raise StorageError(f"Backup path is not a directory: {backup_path}")

        # Validate at least transactions or categories exist and are valid JSON
        tx_file = backup_path / "transactions.json"
        if tx_file.exists():
            try:
                with open(tx_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if not isinstance(data, list):
                    raise StorageError("Invalid transactions.json structure in backup.")
            except json.JSONDecodeError as e:
                raise StorageError(f"Malformed transactions.json in backup: {e}") from e

        # Copy files
        for name in [
            "transactions.json",
            "categories.json",
            "budgets.json",
            "recurring_transactions.json",
            "settings.json",
        ]:
            src = backup_path / name
            if src.exists():
                shutil.copy2(src, self.data_dir / name)
