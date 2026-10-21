"""
Budget management and status calculations.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Dict, List, Optional, Tuple

from .models import Budget, Transaction, TransactionType
from .storage import DataManager
from .validation import ValidationError


class BudgetManager:
    """Handles creation, editing, and status of budgets."""

    def __init__(self, data_manager: DataManager) -> None:
        self.dm = data_manager
        self._budgets: List[Budget] = self.dm.load_budgets()

    def reload(self) -> None:
        self._budgets = self.dm.load_budgets()

    def save(self) -> None:
        self.dm.save_budgets(self._budgets)

    @property
    def budgets(self) -> List[Budget]:
        return list(self._budgets)

    def set_budget(
        self,
        amount: Decimal,
        year: int,
        month: int,
        category: Optional[str] = None,
    ) -> Budget:
        if amount < 0:
            raise ValidationError("Budget amount cannot be negative.")
        # Update existing if same year/month/category
        for b in self._budgets:
            if b.year == year and b.month == month and b.category == category:
                b.amount = amount
                b.updated_at = date.today()  # type: ignore
                self.save()
                return b
        budget = Budget(amount=amount, year=year, month=month, category=category)
        self._budgets.append(budget)
        self.save()
        return budget

    def get_budget(
        self, year: int, month: int, category: Optional[str] = None
    ) -> Optional[Budget]:
        for b in self._budgets:
            if b.year == year and b.month == month and b.category == category:
                return b
        return None

    def delete_budget(
        self, year: int, month: int, category: Optional[str] = None
    ) -> None:
        before = len(self._budgets)
        self._budgets = [
            b
            for b in self._budgets
            if not (b.year == year and b.month == month and b.category == category)
        ]
        if len(self._budgets) == before:
            raise ValidationError("Budget not found.")
        self.save()

    def calculate_spent(
        self,
        transactions: List[Transaction],
        year: int,
        month: int,
        category: Optional[str] = None,
    ) -> Decimal:
        """Sum of expense amounts for the given period (and optional category)."""
        total = Decimal("0.00")
        for t in transactions:
            if t.type != TransactionType.EXPENSE:
                continue
            if t.date.year != year or t.date.month != month:
                continue
            if category is not None and t.category.lower() != category.lower():
                continue
            total += t.amount
        return total

    def get_status(
        self,
        transactions: List[Transaction],
        year: int,
        month: int,
        category: Optional[str] = None,
        warning_threshold: int = 80,
    ) -> Dict:
        """
        Return budget status dictionary.
        Keys: budget, spent, remaining, overspent, percent_used, status, warning
        """
        budget_obj = self.get_budget(year, month, category)
        budget_amount = budget_obj.amount if budget_obj else Decimal("0.00")
        spent = self.calculate_spent(transactions, year, month, category)

        if budget_amount == 0:
            remaining = Decimal("0.00")
            overspent = Decimal("0.00")
            percent = Decimal("0.00")
            status = "no_budget"
            warning = False
        else:
            remaining = max(budget_amount - spent, Decimal("0.00"))
            overspent = max(spent - budget_amount, Decimal("0.00"))
            percent = (spent / budget_amount * 100).quantize(Decimal("0.01"))
            if spent > budget_amount:
                status = "over"
            elif percent >= warning_threshold:
                status = "warning"
            else:
                status = "ok"
            warning = status in ("warning", "over")

        return {
            "budget": budget_amount,
            "spent": spent,
            "remaining": remaining,
            "overspent": overspent,
            "percent_used": percent,
            "status": status,
            "warning": warning,
            "category": category or "Overall",
            "year": year,
            "month": month,
        }

    def list_statuses(
        self,
        transactions: List[Transaction],
        year: int,
        month: int,
        warning_threshold: int = 80,
    ) -> List[Dict]:
        """Return status for overall + all category budgets for the period."""
        results = []
        # Overall
        overall = self.get_status(
            transactions, year, month, None, warning_threshold
        )
        results.append(overall)
        # Category budgets
        seen = set()
        for b in self._budgets:
            if b.year == year and b.month == month and b.category:
                if b.category not in seen:
                    results.append(
                        self.get_status(
                            transactions, year, month, b.category, warning_threshold
                        )
                    )
                    seen.add(b.category)
        return results
