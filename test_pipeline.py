import pandas as pd
import pytest

from pipeline import (
    clean_column_names,
    clean_discount,
    clean_region,
    drop_duplicate_rows,
    clean_unit_price,
    drop_rows_without_order_id,
    clean_quantity,
)


def test_column_names_are_lower_case_with_underscores():
    df = pd.DataFrame(columns=["Order ID", "Region", "Quantity ", "Unit Price"])

    result = clean_column_names(df)

    assert list(result.columns) == ["order_id", "region", "quantity", "unit_price"]


def test_cleaning_column_names_does_not_modify_input():
    df = pd.DataFrame(columns=["Order ID", "Quantity "])

    clean_column_names(df)

    assert list(df.columns) == ["Order ID", "Quantity "]


def test_rows_without_valid_order_id_are_dropped():
    df = pd.DataFrame(
        {
            "order_id": ["SO-10001", "Order ID", "SO-10002", "TOTAL", ""],
            "region": ["North", "Region", "South", "", "East"],
        }
    )

    result = drop_rows_without_order_id(df)

    assert list(result["order_id"]) == ["SO-10001", "SO-10002"]


def test_order_id_with_wrong_format_is_dropped():
    df = pd.DataFrame({"order_id": ["SO-10001", "SO-1001", "so-10002", "SO-100030", " SO-10004"]})

    result = drop_rows_without_order_id(df)

    assert list(result["order_id"]) == ["SO-10001"]


def test_dropped_order_ids_are_logged(caplog):
    df = pd.DataFrame({"order_id": ["SO-10001", "TOTAL"]})

    drop_rows_without_order_id(df)

    assert "Dropped 1 rows without a valid order id: ['TOTAL']" in caplog.text


def test_nothing_is_logged_when_no_row_is_dropped(caplog):
    df = pd.DataFrame({"order_id": ["SO-10001", "SO-10002"]})

    drop_rows_without_order_id(df)

    assert caplog.text == ""


def test_duplicate_rows_are_dropped():
    df = pd.DataFrame(
        {
            "order_id": ["SO-10001", "SO-10001", "SO-10002", "SO-10001"],
            "quantity": ["5", "5", "3", "5"],
        }
    )

    result = drop_duplicate_rows(df)

    assert list(result["order_id"]) == ["SO-10001", "SO-10002"]


def test_rows_with_same_order_id_but_different_values_are_kept():
    df = pd.DataFrame({"order_id": ["SO-10001", "SO-10001"], "quantity": ["5", "7"]})

    result = drop_duplicate_rows(df)

    assert list(result["quantity"]) == ["5", "7"]


@pytest.mark.parametrize("region", ["North", " North", "NORTH", "north  "])
def test_region_is_written_the_same_way(region):
    df = pd.DataFrame({"order_id": ["SO-10001"], "region": [region]})

    result = clean_region(df)

    assert list(result["region"]) == ["North"]


def test_row_with_empty_region_is_dropped():
    df = pd.DataFrame(
        {
            "order_id": ["SO-10001", "SO-10002", "SO-10003"],
            "region": ["North", "", "   "],
        }
    )

    result = clean_region(df)

    assert list(result["order_id"]) == ["SO-10001"]


def test_space_in_quantity_is_removed():
    df = pd.DataFrame({"order_id": ["SO-10001", "SO-10002"], "quantity": ["1 762", " 7 "]})

    result = clean_quantity(df)

    assert list(result["quantity"]) == [1762, 7]
    assert pd.api.types.is_integer_dtype(result["quantity"])


def test_negative_quantity_is_kept():
    df = pd.DataFrame({"order_id": ["SO-10001", "SO-10002"], "quantity": ["-3", "5"]})

    result = clean_quantity(df)

    assert list(result["quantity"]) == [-3, 5]


@pytest.mark.parametrize("quantity", ["", "abc", "2.5"])
def test_row_with_invalid_quantity_is_dropped(quantity):
    df = pd.DataFrame({"order_id": ["SO-10001", "SO-10002"], "quantity": ["5", quantity]})

    result = clean_quantity(df)

    assert list(result["order_id"]) == ["SO-10001"]


def test_unit_price_becomes_numbers():
    df = pd.DataFrame(
        {
            "order_id": ["SO-10001", "SO-10002", "SO-10003"],
            "product": ["Mouse", "Desk lamp", "Headset"],
            "unit_price": ["29.50", "39,90", " 119 "],
        }
    )

    result = clean_unit_price(df)

    assert list(result["unit_price"]) == [29.5, 39.9, 119.0]
    assert pd.api.types.is_float_dtype(result["unit_price"])


def test_empty_unit_price_is_taken_from_the_same_product():
    df = pd.DataFrame(
        {
            "order_id": ["SO-10001", "SO-10002", "SO-10003"],
            "product": ["Mouse", "Mouse", "Mouse"],
            "unit_price": ["29.50", "", "29,50"],
        }
    )

    result = clean_unit_price(df)

    assert list(result["unit_price"]) == [29.5, 29.5, 29.5]


def test_empty_unit_price_is_dropped_when_product_has_two_prices():
    df = pd.DataFrame(
        {
            "order_id": ["SO-10001", "SO-10002", "SO-10003"],
            "product": ["Mouse", "Mouse", "Mouse"],
            "unit_price": ["29.50", "31.00", ""],
        }
    )

    result = clean_unit_price(df)

    assert list(result["order_id"]) == ["SO-10001", "SO-10002"]


@pytest.mark.parametrize("unit_price", ["abc", "-5"])
def test_row_with_invalid_unit_price_is_dropped(unit_price):
    df = pd.DataFrame(
        {
            "order_id": ["SO-10001", "SO-10002"],
            "product": ["Mouse", "Mouse"],
            "unit_price": ["29.50", unit_price],
        }
    )

    result = clean_unit_price(df)

    assert list(result["order_id"]) == ["SO-10001"]


def test_empty_discount_becomes_zero():
    df = pd.DataFrame({"order_id": ["SO-10001", "SO-10002"], "discount": ["", "130.90"]})

    result = clean_discount(df)

    assert list(result["discount"]) == [0.0, 130.9]
    assert pd.api.types.is_float_dtype(result["discount"])


@pytest.mark.parametrize("discount", ["abc", "-5"])
def test_row_with_invalid_discount_is_dropped(discount):
    df = pd.DataFrame({"order_id": ["SO-10001", "SO-10002"], "discount": ["5.00", discount]})

    result = clean_discount(df)

    assert list(result["order_id"]) == ["SO-10001"]
