# Data Model

## Transaction
| Field          | Type            | Notes                          |
|----------------|-----------------|--------------------------------|
| id             | str (8-char)    | UUID fragment                  |
| type           | expense/income  | Enum                           |
| amount         | Decimal (str)   | Positive, 2 dp                 |
| category       | str             | Required                       |
| date           | date (ISO)      | YYYY-MM-DD                     |
| description    | str             | Optional                       |
| payment_method | str             | Default Cash                   |
| tags           | list[str]       | Optional                       |
| notes          | str             | Optional                       |
| created_at     | datetime        | ISO                            |
| updated_at     | datetime        | ISO                            |

## Budget
| Field    | Type          | Notes                    |
|----------|---------------|--------------------------|
| id       | str           |                          |
| amount   | Decimal       | ≥ 0                      |
| year     | int           |                          |
| month    | int           | 1–12                     |
| category | str or null   | null = overall           |

## RecurringRule
| Field          | Type     | Notes                     |
|----------------|----------|---------------------------|
| interval       | weekly/monthly |                     |
| start_date     | date     |                           |
| end_date       | date/null|                           |
| last_generated | date/null| Prevents duplicates       |
| active         | bool     |                           |
