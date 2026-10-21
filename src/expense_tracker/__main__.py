"""
Entry point for `python -m expense_tracker`.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from .cli import CLIInterface


def main() -> None:
    parser = argparse.ArgumentParser(
        description="PocketLedger - Command-Line Expense Tracker"
    )
    parser.add_argument(
        "--data-dir",
        type=str,
        default="data",
        help="Directory for JSON data files (default: data)",
    )
    args = parser.parse_args()
    data_dir = Path(args.data_dir)
    cli = CLIInterface(data_dir=data_dir)
    cli.run()


if __name__ == "__main__":
    main()
