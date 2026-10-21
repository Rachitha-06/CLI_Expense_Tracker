"""
Data models for PocketLedger.

Uses dataclasses and Decimal for precise monetary values.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Any, List, Optional
import uuid


class TransactionType(str, Enum):
    EXPENSE = "expense"
    INCOME = "income"


class RecurrenceInterval(str, Enum):
    WEEKLY = "weekly"
    MONTHLY = "monthly"


def generate_id() -> str:
    """Generate a unique transaction ID."""
    return str(uuid.uuid4())[:8]


@dataclass
class Transaction:
    """Represents a single income or expense transaction."""

    amount: Decimal
    category: str
    date: date
    type: TransactionType
    description: str = ""
    payment_method: str = "Cash"
    tags: List[str] = field(default_factory=list)
    notes: str = ""
    id: str = field(default_factory=generate_id)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self) -> None:
        if not isinstance(self.amount, Decimal):
            self.amount = Decimal(str(self.amount))
        if self.amount <= 0:
            raise ValueError("Amount must be positive. Use a separate refund or adjustment if needed.")
        if isinstance(self.date, str):
            self.date = date.fromisoformat(self.date)
        if isinstance(self.type, str):
            self.type = TransactionType(self.type.lower())
        if isinstance(self.created_at, str):
            self.created_at = datetime.fromisoformat(self.created_at)
        if isinstance(self.updated_at, str):
            self.updated_at = datetime.fromisoformat(self.updated_at)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a JSON-compatible dictionary."""
        return {
            "id": self.id,
            "type": self.type.value,
            "amount": str(self.amount),
            "category": self.category,
            "date": self.date.isoformat(),
            "description": self.description,
            "payment_method": self.payment_method,
            "tags": self.tags,
            "notes": self.notes,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Transaction:
        """Deserialize from a dictionary."""
        return cls(
            id=data.get("id", generate_id()),
            type=TransactionType(data["type"]),
            amount=Decimal(str(data["amount"])),
            category=data["category"],
            date=date.fromisoformat(data["date"]),
            description=data.get("description", ""),
            payment_method=data.get("payment_method", "Cash"),
            tags=data.get("tags", []),
            notes=data.get("notes", ""),
            created_at=datetime.fromisoformat(data["created_at"])
            if "created_at" in data
            else datetime.now(),
            updated_at=datetime.fromisoformat(data["updated_at"])
            if "updated_at" in data
            else datetime.now(),
        )

    def update(self, **kwargs: Any) -> None:
        """Update fields and set updated_at."""
        for key, value in kwargs.items():
            if hasattr(self, key) and value is not None:
                if key == "amount":
                    value = Decimal(str(value))
                    if value <= 0:
                        raise ValueError("Amount must be positive.")
                if key == "date" and isinstance(value, str):
                    value = date.fromisoformat(value)
                if key == "type" and isinstance(value, str):
                    value = TransactionType(value.lower())
                setattr(self, key, value)
        self.updated_at = datetime.now()


@dataclass
class Budget:
    """Monthly budget for overall spending or a specific category."""

    amount: Decimal
    year: int
    month: int
    category: Optional[str] = None  # None means overall budget
    id: str = field(default_factory=generate_id)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self) -> None:
        if not isinstance(self.amount, Decimal):
            self.amount = Decimal(str(self.amount))
        if self.amount < 0:
            raise ValueError("Budget amount cannot be negative.")
        if self.month < 1 or self.month > 12:
            raise ValueError("Month must be between 1 and 12.")

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "amount": str(self.amount),
            "year": self.year,
            "month": self.month,
            "category": self.category,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Budget:
        return cls(
            id=data.get("id", generate_id()),
            amount=Decimal(str(data["amount"])),
            year=int(data["year"]),
            month=int(data["month"]),
            category=data.get("category"),
            created_at=datetime.fromisoformat(data["created_at"])
            if "created_at" in data
            else datetime.now(),
            updated_at=datetime.fromisoformat(data["updated_at"])
            if "updated_at" in data
            else datetime.now(),
        )


@dataclass
class RecurringRule:
    """Rule for generating recurring transactions."""

    description: str
    amount: Decimal
    category: str
    type: TransactionType
    interval: RecurrenceInterval
    start_date: date
    end_date: Optional[date] = None
    payment_method: str = "Cash"
    tags: List[str] = field(default_factory=list)
    notes: str = ""
    active: bool = True
    last_generated: Optional[date] = None
    id: str = field(default_factory=generate_id)
    created_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self) -> None:
        if not isinstance(self.amount, Decimal):
            self.amount = Decimal(str(self.amount))
        if self.amount <= 0:
            raise ValueError("Amount must be positive.")
        if isinstance(self.start_date, str):
            self.start_date = date.fromisoformat(self.start_date)
        if self.end_date and isinstance(self.end_date, str):
            self.end_date = date.fromisoformat(self.end_date)
        if isinstance(self.type, str):
            self.type = TransactionType(self.type.lower())
        if isinstance(self.interval, str):
            self.interval = RecurrenceInterval(self.interval.lower())
        if self.last_generated and isinstance(self.last_generated, str):
            self.last_generated = date.fromisoformat(self.last_generated)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "description": self.description,
            "amount": str(self.amount),
            "category": self.category,
            "type": self.type.value,
            "interval": self.interval.value,
            "start_date": self.start_date.isoformat(),
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "payment_method": self.payment_method,
            "tags": self.tags,
            "notes": self.notes,
            "active": self.active,
            "last_generated": self.last_generated.isoformat()
            if self.last_generated
            else None,
            "created_at": self.created_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> RecurringRule:
        return cls(
            id=data.get("id", generate_id()),
            description=data["description"],
            amount=Decimal(str(data["amount"])),
            category=data["category"],
            type=TransactionType(data["type"]),
            interval=RecurrenceInterval(data["interval"]),
            start_date=date.fromisoformat(data["start_date"]),
            end_date=date.fromisoformat(data["end_date"])
            if data.get("end_date")
            else None,
            payment_method=data.get("payment_method", "Cash"),
            tags=data.get("tags", []),
            notes=data.get("notes", ""),
            active=data.get("active", True),
            last_generated=date.fromisoformat(data["last_generated"])
            if data.get("last_generated")
            else None,
            created_at=datetime.fromisoformat(data["created_at"])
            if "created_at" in data
            else datetime.now(),
        )


# Default categories
DEFAULT_EXPENSE_CATEGORIES = [
    "Food",
    "Transportation",
    "Education",
    "Housing",
    "Utilities",
    "Shopping",
    "Healthcare",
    "Entertainment",
    "Travel",
    "Subscriptions",
    "Personal Care",
    "Other",
]

DEFAULT_INCOME_CATEGORIES = [
    "Salary",
    "Internship",
    "Scholarship",
    "Freelance",
    "Allowance",
    "Other Income",
]

DEFAULT_PAYMENT_METHODS = [
    "Cash",
    "UPI",
    "Credit Card",
    "Debit Card",
    "Bank Transfer",
    "Other",
]
