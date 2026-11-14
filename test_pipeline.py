import pandas as pd

from pipeline import clean_column_names, drop_duplicate_rows, drop_rows_without_order_id


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
