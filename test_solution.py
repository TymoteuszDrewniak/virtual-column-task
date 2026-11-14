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


@pytest.mark.parametrize(
    "role, expected",
    [
        ("a * 2", [4, 10]),
        ("a * 2.5", [5.0, 12.5]),
        ("2 * a + b", [7, 17]),
        ("a - 10", [-8, -5]),
        ("10 - a * b", [4, -25]),
    ],
)
def test_role_with_numbers(role, expected):
    result = add_virtual_column(make_df(), role, "total")
    assert result["total"].tolist() == expected


def test_whole_number_keeps_integer_column_type():
    result = add_virtual_column(make_df(), "a * 2", "total")
    assert result["total"].dtype == "int64"


@pytest.mark.parametrize(
    "role, expected",
    [
        ("-a", [-2, -5]),
        ("-a + b", [1, 2]),
        ("-a - b", [-5, -12]),
        ("a * -2", [-4, -10]),
        ("a * -b", [-6, -35]),
        ("-a * -b", [6, 35]),
        ("a - -b", [5, 12]),
        ("a--b", [5, 12]),
    ],
)
def test_role_with_minus_sign(role, expected):
    result = add_virtual_column(make_df(), role, "total")
    assert result["total"].tolist() == expected


@pytest.mark.parametrize(
    "role",
    [
        # nothing to compute
        "",
        "   ",
        # missing operand
        "a +",
        "a *",
        "+ a",
        "* a",
        "a + + b",
        "a * * b",
        "a + * b",
        # missing operator
        "a b",
        # characters and operators that are not supported
        "a / b",
        "a ** b",
        "(a + b) * c",
        "a & b",
        # unknown column
        "a + x",
        "A + b",
        # numbers in a form that is not supported
        "a * .5",
        "a * 2.",
        "a * 1e3",
        "a * 1,5",
        "a2 + b",
        "2a + b",
        # no column at all
        "2 + 3",
        "2",
        # more than one sign, or a plus sign
        "--a",
        "a---b",
        "+a",
        "a + +b",
        "-",
    ],
)
def test_invalid_role_returns_empty_dataframe(role):
    result = add_virtual_column(make_df(), role, "total")
    assert result.shape == (0, 0)
