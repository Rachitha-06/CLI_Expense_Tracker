"""
Core expense tracker business logic.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import List, Optional

from .models import Transaction, TransactionType
from .storage import DataManager
from .validation import ValidationError


class ExpenseTracker:
    """Coordinates transaction management, search, and filtering."""

    def __init__(self, data_manager: DataManager) -> None:
        self.dm = data_manager
        self._transactions: List[Transaction] = self.dm.load_transactions()

    def reload(self) -> None:
        self._transactions = self.dm.load_transactions()

    def save(self) -> None:
        self.dm.save_transactions(self._transactions)

    @property
    def transactions(self) -> List[Transaction]:
        return list(self._transactions)

    def add_transaction(self, transaction: Transaction) -> Transaction:
        self._transactions.append(transaction)
        self.save()
        return transaction

    def get_by_id(self, tx_id: str) -> Optional[Transaction]:
        for t in self._transactions:
            if t.id == tx_id:
                return t
        return None

    def edit_transaction(self, tx_id: str, **kwargs) -> Transaction:
        tx = self.get_by_id(tx_id)
        if tx is None:
            raise ValidationError(f"Transaction with ID '{tx_id}' not found.")
        tx.update(**kwargs)
        self.save()
        return tx

    def delete_transaction(self, tx_id: str) -> None:
        tx = self.get_by_id(tx_id)
        if tx is None:
            raise ValidationError(f"Transaction with ID '{tx_id}' not found.")
        self._transactions = [t for t in self._transactions if t.id != tx_id]
        self.save()

    def search(
        self,
        query: str = "",
        by_id: Optional[str] = None,
        category: Optional[str] = None,
        payment_method: Optional[str] = None,
        tag: Optional[str] = None,
    ) -> List[Transaction]:
        """Case-insensitive partial text search."""
        results = self._transactions
        if by_id:
            results = [t for t in results if t.id == by_id]
            return results
        q = query.lower().strip()
        if q:
            results = [
                t
                for t in results
                if q in t.description.lower()
                or q in t.category.lower()
                or q in t.notes.lower()
                or any(q in tag.lower() for tag in t.tags)
                or q in t.payment_method.lower()
                or q in t.id.lower()
            ]
        if category:
            results = [t for t in results if t.category.lower() == category.lower()]
        if payment_method:
            results = [
                t
                for t in results
                if t.payment_method.lower() == payment_method.lower()
            ]
        if tag:
            results = [
                t
                for t in results
                if any(tag.lower() == tg.lower() for tg in t.tags)
            ]
        return results

    def filter(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        category: Optional[str] = None,
        tx_type: Optional[TransactionType] = None,
        min_amount: Optional[Decimal] = None,
        max_amount: Optional[Decimal] = None,
        payment_method: Optional[str] = None,
        tag: Optional[str] = None,
    ) -> List[Transaction]:
        """Filter transactions with inclusive date boundaries."""
        if start_date and end_date and start_date > end_date:
            raise ValidationError("Start date cannot be after end date.")
        if min_amount is not None and max_amount is not None and min_amount > max_amount:
            raise ValidationError("Minimum amount cannot exceed maximum amount.")

        results = self._transactions
        if start_date:
            results = [t for t in results if t.date >= start_date]
        if end_date:
            results = [t for t in results if t.date <= end_date]
        if category:
            results = [t for t in results if t.category.lower() == category.lower()]
        if tx_type:
            results = [t for t in results if t.type == tx_type]
        if min_amount is not None:
            results = [t for t in results if t.amount >= min_amount]
        if max_amount is not None:
            results = [t for t in results if t.amount <= max_amount]
        if payment_method:
            results = [
                t
                for t in results
                if t.payment_method.lower() == payment_method.lower()
            ]
        if tag:
            results = [
                t
                for t in results
                if any(tag.lower() == tg.lower() for tg in t.tags)
            ]
        return results

    def sort_transactions(
        self,
        transactions: Optional[List[Transaction]] = None,
        by: str = "date",
        reverse: bool = True,
    ) -> List[Transaction]:
        txs = transactions if transactions is not None else self._transactions
        if by == "amount":
            return sorted(txs, key=lambda t: t.amount, reverse=reverse)
        if by == "date":
            return sorted(txs, key=lambda t: t.date, reverse=reverse)
        return list(txs)
