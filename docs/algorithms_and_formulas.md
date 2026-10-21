# Algorithms and Formulas – PocketLedger

## 1. Financial Aggregation

```
TotalIncome   = Σ amount  where type = income
TotalExpenses = Σ amount  where type = expense
NetBalance    = TotalIncome − TotalExpenses
```

Pseudocode:
```
income = Decimal("0.00")
expenses = Decimal("0.00")
for t in transactions:
    if t.type == INCOME:
        income += t.amount
    else:
        expenses += t.amount
net = income - expenses
```

Complexity: O(n) where n = number of transactions.

## 2. Average Expense

```
AverageExpense = TotalExpenses / NumberOfExpenseTransactions
```

If expense count is zero → return None (display “N/A”).

## 3. Category-wise Aggregation

```
expense_by_category[cat] += amount   for each expense
income_by_category[cat]  += amount   for each income
```

Highest-spending category = argmax(expense_by_category).

## 4. Date-Range Filtering

Inclusive boundaries:
```
start ≤ t.date ≤ end
```

Invalid if start > end → raise ValidationError.

## 5. Search

Case-insensitive substring match against description, category, notes, tags, payment_method, and id.

## 6. Sorting

- By date: `sorted(txs, key=lambda t: t.date, reverse=True)`
- By amount: `sorted(txs, key=lambda t: t.amount, reverse=True)`

## 7. Monthly / Yearly Reporting

Monthly: filter transactions where `year == Y and month == M`.  
Yearly: filter `year == Y`.  
Previous period is computed for comparison.

## 8. Budget Calculations

```
Spent      = Σ expense amounts in (year, month) [and category if set]
Remaining  = max(Budget − Spent, 0)
Overspent  = max(Spent − Budget, 0)
PercentUsed = (Spent / Budget) × 100   (if Budget > 0)
Status     = "over" | "warning" | "ok" | "no_budget"
```

Warning when PercentUsed ≥ threshold (default 80).

## 9. Recurrence Generation

```
cursor = last_generated + interval   OR   start_date
while cursor ≤ today and (end_date is None or cursor ≤ end_date):
    create Transaction on cursor
    last_generated = cursor
    cursor = next_date(cursor, interval)
```

Monthly next_date advances month and clamps day to last valid day of month.

## 10. Decimal Arithmetic

All monetary values use `decimal.Decimal`.  
Amounts are quantized to `Decimal("0.01")` on input.  
JSON stores amounts as strings to avoid binary floating-point.

## 11. Atomic File Write

```
write data to path.tmp
path.tmp.replace(path)   # atomic on same filesystem
```
