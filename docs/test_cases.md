# Test Cases

## A. Transaction
| ID | Description                    | Expected                |
|----|--------------------------------|-------------------------|
| T1 | Create expense                 | Stored with unique ID   |
| T2 | Create income                  | Type = income           |
| T3 | Negative amount                | ValueError              |
| T4 | Zero amount                    | ValueError              |
| T5 | Unique IDs                     | 50 distinct IDs         |
| T6 | Edit by ID                     | Fields updated          |
| T7 | Edit nonexistent               | ValidationError         |
| T8 | Delete                         | Removed from list       |

## B. Financial Calculations
| ID | Description              | Expected                     |
|----|--------------------------|------------------------------|
| F1 | Total income             | Sum of income amounts        |
| F2 | Total expenses           | Sum of expense amounts       |
| F3 | Net balance              | Income − Expenses            |
| F4 | Average expense          | Expenses / count             |
| F5 | Empty dataset            | Zeros, avg = None            |
| F6 | Decimal precision        | 0.10 + 0.20 = 0.30           |

## C. Filtering
| ID | Description           | Expected              |
|----|-----------------------|-----------------------|
| R1 | Date range inclusive  | Boundary dates kept   |
| R2 | Invalid range         | ValidationError       |
| R3 | Amount filter         | Correct subset        |
| R4 | Type filter           | Only matching type    |

## D. Budgets
| ID | Description        | Expected                |
|----|--------------------|-------------------------|
| B1 | Set budget         | Persisted               |
| B2 | Remaining          | Budget − Spent          |
| B3 | Overspend          | overspent > 0           |
| B4 | Exact match        | remaining = 0           |
| B5 | Warning threshold  | status = warning        |

## E. File Handling
| ID | Description         | Expected              |
|----|---------------------|-----------------------|
| S1 | Save / load         | Round-trip OK         |
| S2 | Missing file        | Empty list            |
| S3 | Malformed JSON      | StorageError          |
| S4 | Backup / restore    | Data restored         |

## F. Recurring
| ID | Description      | Expected                     |
|----|------------------|------------------------------|
| C1 | Weekly           | Correct interval dates       |
| C2 | Monthly          | Month advanced               |
| C3 | Month-end        | Clamped to last day          |
| C4 | No duplicates    | Second process yields 0      |
| C5 | End date         | Stops after end              |

## G. Export
| ID | Description          | Expected                    |
|----|----------------------|-----------------------------|
| E1 | Headers present      | id, amount, …               |
| E2 | Precision preserved  | "99.99" string              |
| E3 | Formula injection    | Leading ' prefix            |
| E4 | No silent overwrite  | FileExistsError             |
