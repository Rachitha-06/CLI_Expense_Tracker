# Viva Questions (50+)

1. What is the purpose of PocketLedger?
2. Why did you choose a command-line interface?
3. Why use `decimal.Decimal` instead of float?
4. How are unique transaction IDs generated?
5. Explain the Transaction dataclass.
6. What is the difference between income and expense in the model?
7. How is data persisted?
8. Explain atomic file writing.
9. What happens if transactions.json is missing?
10. What happens if the JSON is malformed?
11. How does search work?
12. How does date-range filtering handle boundary dates?
13. Write the formula for Net Balance.
14. How is average expense calculated when there are no expenses?
15. Explain category-wise aggregation.
16. How are monthly reports grouped?
17. What is a budget warning threshold?
18. How is remaining budget calculated?
19. How is overspending detected?
20. Explain the recurring transaction policy for missed dates.
21. How are month-end dates handled in monthly recurrence?
22. How does the system prevent duplicate recurring transactions?
23. What CSV injection protection is implemented?
24. How does backup/restore ensure data safety?
25. Why are categories stored separately from transactions?
26. What design pattern is used for managers?
27. Why use type hints?
28. What is the role of `DataManager`?
29. How is the CLI separated from business logic?
30. Explain exception hierarchy used.
31. How do you validate amounts?
32. Why reject zero and negative amounts?
33. What date format is required?
34. How are custom categories added?
35. Can deleting a category corrupt transactions?
36. What is the purpose of tags?
37. How would you add a new payment method?
38. What testing framework was used?
39. Why use temporary directories in tests?
40. How many tests currently pass?
41. What is the time complexity of the summary calculation?
42. Why store amounts as strings in JSON?
43. What happens on failed restore?
44. How is the project packaged?
45. What Python version is required?
46. Are there third-party dependencies?
47. How do you run the application?
48. How do you run the tests?
49. What are the known limitations?
50. Suggest three future enhancements.
51. Why use dataclasses?
52. Explain the difference between a RecurringRule and a Transaction.
53. How is the previous period comparison computed in reports?
54. What is the default currency symbol?
55. How would you extend the system to support weekly budgets?
