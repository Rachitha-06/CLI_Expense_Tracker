# Limitations and Future Scope

## Limitations

- Single-user, local filesystem only – no multi-device sync.
- No integration with bank accounts or payment gateways.
- Recurring occurrences are generated when the application starts or when the user explicitly triggers processing; the app does not run as a background daemon.
- CSV export is plain text; advanced Excel formatting is not supported.
- The calculated balance reflects only recorded transactions, not a verified bank balance.
- Not a substitute for professional financial advice or official records.

## Future Scope

1. Optional SQLite backend for larger datasets and relational queries.
2. ASCII or simple graphical charts for category spending.
3. Multi-currency support with exchange-rate snapshots.
4. Import of bank CSV statements with column mapping.
5. Tag-based analytics and spending trends over time.
6. Optional password protection / simple encryption of the data directory.
7. Plugin architecture for custom report formats.
