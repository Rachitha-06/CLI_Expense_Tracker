"""
Application settings management.
"""

from __future__ import annotations

from typing import Any, Dict

from .storage import DataManager


class SettingsManager:
    """Load and update application settings."""

    def __init__(self, data_manager: DataManager) -> None:
        self.dm = data_manager
        self._settings = self.dm.load_settings()

    def get(self, key: str, default: Any = None) -> Any:
        return self._settings.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self._settings[key] = value
        self.dm.save_settings(self._settings)

    def all(self) -> Dict[str, Any]:
        return dict(self._settings)

    @property
    def warning_threshold(self) -> int:
        return int(self._settings.get("budget_warning_threshold", 80))

    @property
    def allow_future_dates(self) -> bool:
        return bool(self._settings.get("allow_future_dates", True))

    @property
    def currency_symbol(self) -> str:
        return str(self._settings.get("currency_symbol", "₹"))
