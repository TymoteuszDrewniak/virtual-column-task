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

This one command runs all the tests: the 6 provided with the task and 123 of mine
(93 for Part 1 and 30 for Part 2).

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

## Part 2: sales pipeline

### Problems found in `sales.csv`

The file has 1507 rows of data. After dropping the rows that are not orders,
1505 are left, and after deduplication the final number of rows is 1500.
I didn't drop any of the real orders, because every other problem could be fixed.

| # | Problem | Rows affected | How it is handled |
|---|---|---|---|
| 1 | Column labels have spaces and capital letters, also `Quantity ` has space at the end | 7 labels | change to small letters and `_`, for example `unit_price` |
| 2 | Header row duplicated in the middle of the file | 1 | dropped |
| 3 | `TOTAL` row at the end of the file | 1 | dropped |
| 4 | Entirely duplicated rows | 5 | dropped, only first copy remains |
| 5 | Region written in different ways: spaces, small and capital letters | 15 | remove spaces and write with only first letter as a capital letter |
| 6 | Space as a thousands separator, for example `1 762` | 4 | space removed |
| 7 | Negative quantity | 6 | remains, treated as a return |
| 8 | Decimal comma in a price, for example `39,90` | 7 | replace with a `.` |
| 9 | Missing unit price | 4 | filled with a price of the same product if this product always has the same price across whole file |
| 10 | Empty discount | 963 (959 after removing duplicates) | set to 0 |

I also checked the product names and the order dates before cleaning the data.
I found no problems in them, so the pipeline does not clean these columns.

### Decisions

**Which rows are orders.** Instead of two separate rules for duplicated header row and
`TOTAL` row I have only one: I drop every row whose order id is not `SO-` followed
by 5 digits. I have checked and all 1505 remaining rows match this pattern.

**Duplicates.** I drop only rows that are identical in every column. Five such pairs
have the same order_id and values, so I classified them as a duplicate of
the same order and kept only the first one.

**Negative quantities.** Six of the rows have quantity between -2 and -5. There was no information
about this case so I assumed they are returns. Because of this when I calculate
revenue of this order it is also negative which affects the total of all orders.

**Missing prices.** After cleaning the data, every product has exactly one price so
I take price from other rows with the same product. Prices are not hardcoded in code,
pipeline calculates them from data. If a product had more than one price or none
at all, the row would be dropped, because it is not possible to
determine which price is correct.

**Large quantities.** Typical quantity in the data is between 1 and 40. Four orders have
between 1371 and 1762 units. I left them, because even if they are odd compared to
other orders they seem fine. They had spaces in the number but it was only a format issue
not a data issue. These four orders make up 12.6% of all revenue. The `TOTAL` row
also supports this. Its quantity is 37150, and I get the same number when I sum the
quantity column of the raw data only if `1 762` is read as 1762.

**Value that are not possible to fix.** A row where the quantity, price or discount is not a
number is dropped with warning in the logs and pipeline moves on. This also applies to
the negative price and negative discount and row without a region.
I don't have any of these cases in this data.

**Output file.** The task doesn't specify the format of the file. I chose `region` and
`revenue` columns with a row for each region in alphabetical order. Revenue is rounded
to the second decimal place at the end of calculations.

### Effect of the decisions on the result

Decision about negative quantities changes result in three regions:

| Region | Returns kept | Returns dropped | Difference |
|---|---|---|---|
| Central | 515824.67 | 516123.17 | -298.50 |
| East | 442219.91 | 442219.91 | 0.00 |
| North | 665897.52 | 665977.32 | -79.80 |
| South | 504036.04 | 504036.04 | 0.00 |
| West | 442268.89 | 442803.59 | -534.70 |
| Total | 2570247.03 | 2571160.03 | -913.00 |

### What the pipeline does not check

- I don't know which regions are valid, so a misspelled or new region would
  appear as its own row in the output file.

### Result

```
region,revenue
Central,515824.67
East,442219.91
North,665897.52
South,504036.04
West,442268.89
```

I double-checked the results without using the code from
this repository. All 5 regions had exactly the same sums.
