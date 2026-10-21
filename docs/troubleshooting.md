# Troubleshooting

| Problem | Solution |
|---------|----------|
| `ModuleNotFoundError: expense_tracker` | Set `PYTHONPATH=src` or run `pip install -e .` |
| `python` not found | Use `python3` or install Python 3.11+ |
| Invalid date error | Enter dates as `YYYY-MM-DD` |
| Amount rejected | Must be positive with at most 2 decimal places |
| Transaction ID not found | Use option 3 to list IDs |
| FileExistsError on export | Choose a new filename or confirm overwrite |
| Restore fails | Check that the backup folder contains valid JSON files |
| Tests fail with import errors | Ensure you are in the project root and PYTHONPATH includes `src` |
| Permission denied writing data | Check write permissions on the data directory |
