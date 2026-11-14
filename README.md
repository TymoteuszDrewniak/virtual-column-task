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
