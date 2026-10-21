"""
Category management.
"""

from __future__ import annotations

from typing import Dict, List

from .models import DEFAULT_EXPENSE_CATEGORIES, DEFAULT_INCOME_CATEGORIES
from .storage import DataManager
from .validation import ValidationError, validate_category_name


class CategoryManager:
    """Manages expense and income categories."""

    def __init__(self, data_manager: DataManager) -> None:
        self.dm = data_manager
        self._categories = self.dm.load_categories()

    def get_expense_categories(self) -> List[str]:
        return list(self._categories.get("expense", DEFAULT_EXPENSE_CATEGORIES))

    def get_income_categories(self) -> List[str]:
        return list(self._categories.get("income", DEFAULT_INCOME_CATEGORIES))

    def get_all(self) -> Dict[str, List[str]]:
        return {
            "expense": self.get_expense_categories(),
            "income": self.get_income_categories(),
        }

    def add_category(self, name: str, kind: str = "expense") -> None:
        name = validate_category_name(name)
        kind = kind.lower()
        if kind not in ("expense", "income"):
            raise ValidationError("Kind must be 'expense' or 'income'.")
        cats = self._categories.setdefault(kind, [])
        # Case-insensitive duplicate check
        if any(c.lower() == name.lower() for c in cats):
            raise ValidationError(f"Category '{name}' already exists.")
        cats.append(name)
        self._save()

    def rename_category(self, old_name: str, new_name: str, kind: str = "expense") -> None:
        old_name = old_name.strip()
        new_name = validate_category_name(new_name)
        kind = kind.lower()
        cats = self._categories.get(kind, [])
        found = False
        for i, c in enumerate(cats):
            if c.lower() == old_name.lower():
                if any(x.lower() == new_name.lower() for x in cats if x != c):
                    raise ValidationError(f"Category '{new_name}' already exists.")
                cats[i] = new_name
                found = True
                break
        if not found:
            raise ValidationError(f"Category '{old_name}' not found.")
        self._save()

    def remove_category(self, name: str, kind: str = "expense") -> None:
        """Deactivate / remove a category (does not alter existing transactions)."""
        name = name.strip()
        kind = kind.lower()
        cats = self._categories.get(kind, [])
        for i, c in enumerate(cats):
            if c.lower() == name.lower():
                cats.pop(i)
                self._save()
                return
        raise ValidationError(f"Category '{name}' not found.")

    def _save(self) -> None:
        self.dm.save_categories(self._categories)
