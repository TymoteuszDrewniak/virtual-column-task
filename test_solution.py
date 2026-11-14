import pandas
import pytest

from solution import add_virtual_column


def make_df() -> pandas.DataFrame:
    """Return a small DataFrame with three numeric columns."""
    return pandas.DataFrame({"a": [2, 5], "b": [3, 7], "c": [4, 1]})


@pytest.mark.parametrize(
    "role, expected",
    [
        ("a + b", [5, 12]),
        ("a - b", [-1, -2]),
        ("a * b", [6, 35]),
        ("a + b + c", [9, 13]),
        ("a - b - c", [-5, -3]),
        ("a * b * c", [24, 35]),
        ("a + b * c", [14, 12]),
        ("a - b * c", [-10, -2]),
        ("a * b + c", [10, 36]),
        ("a * a", [4, 25]),
        ("a", [2, 5]),
    ],
)
def test_role_is_computed(role, expected):
    result = add_virtual_column(make_df(), role, "total")
    assert result["total"].tolist() == expected


def test_result_keeps_original_columns_and_adds_new_one():
    result = add_virtual_column(make_df(), "a + b", "total")
    assert list(result.columns) == ["a", "b", "c", "total"]
