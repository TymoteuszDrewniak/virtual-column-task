# Virtual column task

This repository contains my solution to the recruitment task. The first part is the function
`add_virtual_column` which adds a new column to a DataFrame.
It is in the `solution.py` file. The second part is a pipeline in
`pipeline.py` which cleans the data from `sales.csv` and calculates the revenue
of each region using the `add_virtual_column` function.

## Files

| File | Description |
|---|---|
| `solution.py` | function `add_virtual_column` |
| `pipeline.py` | cleans `sales.csv` and calculates revenue for each region |
| `revenue_by_region.csv` | result of `pipeline.py` |
| `sales.csv` | input data, unchanged |
| `test_virtual_column.py` | the tests provided with the task, unchanged |
| `test_solution.py` | my tests for Part 1 |
| `test_pipeline.py` | my tests for Part 2 |

## Setup

The project was written and tested with Python 3.13. The dependencies and their versions
are listed in `requirements.txt`.

```bash
python3.13 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## How to run

### Pipeline

```bash
python pipeline.py
```

The script reads `sales.csv` and saves `revenue_by_region.csv` in the same folder.
While pipeline runs, each step logs how many rows were changed or dropped.
Dropped rows are logged together with their order_id.

### Tests

```bash
pytest
```

This one command runs all the tests: the 6 provided with the task and 122 of mine
(92 for Part 1 and 30 for Part 2).

## Part 1: `add_virtual_column`

The function receives a DataFrame, a role and the label of the new column,
and returns a copy of the given DataFrame with the new column. The role is
an expression written as a string, for example `quantity * price - discount`.

The role is divided into column labels, numbers and operators and then checked.
The result is calculated from the same elements without `eval`,
so it can only do the operations that the task allows.

### What the function accepts

- column labels from DataFrame,
- integers and decimals, for example `2` or `2.5`,
- operators `+`, `-` and `*`,
- a minus sign before a column or number, for example `-a + b` or `a * -2`,
- any spaces between elements of the role.

Multiplication is done before addition and subtraction.
A role can contain just one column, for example `a`.

### What makes it return an empty DataFrame

- role is not a string or contains a character that is not allowed,
- role uses column which is not in the DataFrame,
- role has incorrect structure, for example `a +`, `a b` or `a + * b`,
- role doesn't use any column, for example `2 + 3`,
- label of a new column or any column in the DataFrame contains something
  other than letters or `_`,
- label of a new column already exists in the DataFrame,
- DataFrame has two columns with the same label,
- column used in the role contains something other than number,
  for example text, dates or boolean values.

The input DataFrame is never changed. The function returns a copy with the new column.

### Assumptions

**Number in the role.** The task talks about columns, but I also accept numbers,
because expressions like `price * 2` are common. However the role has to use
at least one column.

**Minus as a sign.** One minus before a column or number is allowed.
Expression `a - -b` is allowed and will give the same result as `a + b`.

**Prohibited operations.** Division, exponentiation and parentheses are prohibited,
because the task mentions only addition, subtraction and multiplication.

**Number formats.** Accepted formats are only like `2` and `2.5`. Formats `.5`, `2.`,
`1e3` and `1,5` are not allowed.

**Column names.** Only Latin letters and `_` are allowed. Labels are case-sensitive.
A label with only `_` is okay.

**Column types.** Role can use only columns with numbers. Columns of type `bool`
are not treated as numbers, because they are not typically used in arithmetic
expressions and can be confusing.

**Missing values.** If a value is missing in a numeric column, the result for
that row is also missing.
DataFrame without rows gets new, empty column.
