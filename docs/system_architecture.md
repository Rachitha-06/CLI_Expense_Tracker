# System Architecture

```
┌─────────────────────────────────────────────┐
│                 CLIInterface                │
│              (cli.py menus)                 │
└──────────────────┬──────────────────────────┘
                   │
     ┌─────────────┼─────────────┐
     ▼             ▼             ▼
 ExpenseTracker  BudgetManager  ReportGenerator
 RecurringMgr    CategoryMgr    SettingsMgr
     │             │             │
     └─────────────┼─────────────┘
                   ▼
              DataManager
           (storage.py JSON)
                   │
                   ▼
         data/*.json files
```

**Separation of concerns**
- UI never talks to files directly
- Business logic never prints
- Storage never calculates balances
