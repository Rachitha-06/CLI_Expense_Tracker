# User Guide – PocketLedger

## Starting the Application

```bash
python -m expense_tracker
```

## Main Menu Options

| #  | Action                        |
|----|-------------------------------|
| 1  | Add expense                   |
| 2  | Add income                    |
| 3  | View all transactions         |
| 4  | Edit transaction              |
| 5  | Delete transaction            |
| 6  | Search                        |
| 7  | Filter                        |
| 8  | Financial summary             |
| 9  | Monthly report                |
| 10 | Yearly report                 |
| 11 | Custom date-range report      |
| 12 | Manage budgets                |
| 13 | View budget status            |
| 14 | Manage recurring transactions |
| 15 | Export to CSV                 |
| 16 | Backup data                   |
| 17 | Restore data                  |
| 18 | Manage categories             |
| 19 | Settings                      |
| 20 | Help                          |
| 21 | Exit                          |

## Tips

- Dates: always `YYYY-MM-DD`
- Amounts: positive numbers, max 2 decimal places
- Leave fields blank when editing to keep current values
- Confirmations are required for delete and restore
- Recurring transactions are generated automatically on startup
