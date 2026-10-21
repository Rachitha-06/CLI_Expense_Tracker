# Viva Answers

1. PocketLedger is a CLI personal expense tracker that records income/expenses, manages budgets, generates reports, and exports data.
2. CLI keeps the project focused on core Python skills, works offline, and has zero GUI dependencies.
3. Float has binary precision errors (0.1 + 0.2 ≠ 0.3). Decimal provides exact decimal arithmetic required for money.
4. `uuid.uuid4()` truncated to 8 characters via `generate_id()`.
5. A dataclass holding amount, category, date, type, description, payment_method, tags, notes, id, timestamps.
6. `TransactionType` enum distinguishes them; calculations treat them separately (income adds, expense subtracts).
7. JSON files under a configurable `data/` directory.
8. Write to a temporary file, then atomically `replace()` the original so a crash cannot leave a half-written file.
9. An empty list is returned and the file is created on the next save.
10. `StorageError` is raised; the application does not silently load partial data.
11. Case-insensitive substring match across description, category, notes, tags, payment method, and ID.
12. Filters use `>= start` and `<= end` (inclusive).
13. Net Balance = Total Income − Total Expenses.
14. The function returns `None` and the UI displays “N/A”.
15. A `defaultdict(Decimal)` accumulates amounts keyed by category.
16. Transactions where `date.year == Y and date.month == M`.
17. A percentage (default 80) at which the system flags a budget as approaching its limit.
18. `max(Budget − Spent, 0)`.
19. When `Spent > Budget`, `overspent = Spent − Budget` and status becomes `"over"`.
20. On `process_due()`, all occurrences from the day after `last_generated` (or start_date) up to today are created, provided they are before the optional end_date.
21. The day is decremented until a valid date in the target month is found (e.g., 31 Jan → 28/29 Feb).
22. After generating an occurrence, `last_generated` is updated; the next run starts after that date.
23. Any cell starting with `=`, `+`, `-`, or `@` is prefixed with a single quote.
24. Restore validates JSON structure first; on failure the original data remains untouched.
25. Categories can be managed independently and reused; transactions only store the name string.
26. Manager/Facade pattern – each class owns one responsibility.
27. They document expected types, help IDEs, and catch type errors early.
28. It isolates all file I/O, validation of stored structures, and backup/restore logic.
29. `CLIInterface` only calls public methods of managers; managers never print.
30. `ValidationError` for user input, `StorageError` for file problems; unexpected exceptions are caught at the top level.
31. Strip commas, convert to Decimal, reject ≤ 0, quantize to 2 decimal places.
32. Zero-value and negative entries would distort totals; refunds should be modelled explicitly if needed.
33. ISO 8601: `YYYY-MM-DD`.
34. User types a new name; if it does not exist (case-insensitive) it is appended to the appropriate list and saved.
35. No – category removal only updates the category list; existing transactions keep their stored category name.
36. Free-form labels for additional filtering and search.
37. Add it to `DEFAULT_PAYMENT_METHODS` or simply accept any string the user types.
38. Python’s built-in `unittest`.
39. They guarantee tests never modify real user data and are cleaned up automatically.
40. 64 tests, all passing.
41. O(n) linear scan over the transaction list.
42. JSON numbers are IEEE floats; strings preserve exact decimal representation.
43. A `StorageError` is raised and the current data directory is left unchanged.
44. `pyproject.toml` with setuptools; installable via `pip install -e .`.
45. Python 3.11 or later.
46. No runtime third-party dependencies.
47. `python -m expense_tracker` (with `PYTHONPATH=src` or after editable install).
48. `python -m unittest discover -s tests -v`.
49. Single-user local only; no bank import; recurring fill-in only when the app runs.
50. SQLite backend, ASCII charts, bank CSV import.
51. Less boilerplate than classic classes, automatic `__init__`, `__repr__`, and easy conversion to dicts.
52. A RecurringRule is a schedule; a Transaction is an actual recorded occurrence generated from a rule.
53. The report for the previous month/year is computed with the same summary function and attached under a `"previous"` key.
54. ₹ (Indian Rupee), configurable in settings.
55. Extend `Budget` with an optional `week` field or create a parallel weekly budget manager; the calculation logic is analogous.
