"""
Recurring transaction rules and occurrence generation.
"""

from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal
from typing import List, Optional

from .models import RecurringRule, RecurrenceInterval, Transaction, TransactionType
from .storage import DataManager
from .validation import ValidationError


class RecurringTransactionManager:
    """
    Manages recurring rules and generates due transactions.

    Policy for missed dates:
    - When process_due() is called, all occurrences from last_generated
      (or start_date) up to and including today are generated, provided
      they fall before or on the end_date (if set).
    - Duplicate prevention: last_generated is updated after each generation,
      so reopening the app does not recreate the same occurrence.
    - Month-end: for monthly rules, if start day is 31 and target month has
      fewer days, the occurrence falls on the last day of that month.
    """

    def __init__(self, data_manager: DataManager) -> None:
        self.dm = data_manager
        self._rules: List[RecurringRule] = self.dm.load_recurring()

    def reload(self) -> None:
        self._rules = self.dm.load_recurring()

    def save(self) -> None:
        self.dm.save_recurring(self._rules)

    @property
    def rules(self) -> List[RecurringRule]:
        return list(self._rules)

    def add_rule(self, rule: RecurringRule) -> RecurringRule:
        self._rules.append(rule)
        self.save()
        return rule

    def get_by_id(self, rule_id: str) -> Optional[RecurringRule]:
        for r in self._rules:
            if r.id == rule_id:
                return r
        return None

    def deactivate(self, rule_id: str) -> None:
        rule = self.get_by_id(rule_id)
        if rule is None:
            raise ValidationError(f"Recurring rule '{rule_id}' not found.")
        rule.active = False
        self.save()

    def activate(self, rule_id: str) -> None:
        rule = self.get_by_id(rule_id)
        if rule is None:
            raise ValidationError(f"Recurring rule '{rule_id}' not found.")
        rule.active = True
        self.save()

    def delete_rule(self, rule_id: str) -> None:
        before = len(self._rules)
        self._rules = [r for r in self._rules if r.id != rule_id]
        if len(self._rules) == before:
            raise ValidationError(f"Recurring rule '{rule_id}' not found.")
        self.save()

    def _next_date(self, current: date, interval: RecurrenceInterval) -> date:
        if interval == RecurrenceInterval.WEEKLY:
            return current + timedelta(days=7)
        # Monthly
        year = current.year
        month = current.month + 1
        if month > 12:
            month = 1
            year += 1
        # Handle month-end (e.g., Jan 31 -> Feb 28/29)
        day = current.day
        while True:
            try:
                return date(year, month, day)
            except ValueError:
                day -= 1
                if day < 1:
                    raise  # should not happen

    def process_due(
        self, as_of: Optional[date] = None
    ) -> List[Transaction]:
        """
        Generate all due transactions up to as_of (default: today).
        Returns the list of newly created Transaction objects.
        Caller is responsible for adding them to the tracker.
        """
        if as_of is None:
            as_of = date.today()
        generated: List[Transaction] = []

        for rule in self._rules:
            if not rule.active:
                continue
            # Determine starting point
            if rule.last_generated:
                cursor = self._next_date(rule.last_generated, rule.interval)
            else:
                cursor = rule.start_date

            while cursor <= as_of:
                if rule.end_date and cursor > rule.end_date:
                    break
                # Create occurrence
                tx = Transaction(
                    amount=rule.amount,
                    category=rule.category,
                    date=cursor,
                    type=rule.type,
                    description=rule.description,
                    payment_method=rule.payment_method,
                    tags=list(rule.tags) + ["recurring"],
                    notes=rule.notes or f"Generated from recurring rule {rule.id}",
                )
                generated.append(tx)
                rule.last_generated = cursor
                cursor = self._next_date(cursor, rule.interval)

        if generated:
            self.save()
        return generated
