import logging

import pandas as pd

INPUT_PATH = "sales.csv"
OUTPUT_PATH = "revenue_by_region.csv"
ORDER_ID_PATTERN = r"SO-[0-9]{5}"
QUANTITY_PATTERN = r"-?[0-9]+"

logger = logging.getLogger(__name__)


def load_sales(path: str) -> pd.DataFrame:
    """Read the sales file with every value kept as text.

    Nothing is converted on load, so each cleaning step decides how to read its column.
    """
    df = pd.read_csv(path, dtype=str, keep_default_na=False)
    logger.info("Loaded %d rows from %s", len(df), path)
    return df


def clean_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """Return a copy with column names in lower case and underscores instead of spaces."""
    cleaned_df = df.copy()
    cleaned_df.columns = cleaned_df.columns.str.strip().str.lower().str.replace(" ", "_")
    logger.info("Columns: %s", list(cleaned_df.columns))
    return cleaned_df


def drop_rows_without_order_id(df: pd.DataFrame) -> pd.DataFrame:
    """Return only the rows whose order id looks like SO-12345.

    This removes rows that are not orders, such as a repeated header or a totals row.
    """
    is_order = df["order_id"].str.fullmatch(ORDER_ID_PATTERN)
    dropped_rows = df[~is_order]
    if not dropped_rows.empty:
        logger.warning(
            "Dropped %d rows without a valid order id: %s",
            len(dropped_rows),
            list(dropped_rows["order_id"]),
        )
    return df[is_order].copy()


def drop_duplicate_rows(df: pd.DataFrame) -> pd.DataFrame:
    """Remove rows that appear more than once.

    Two rows are the same only if all their values are the same.
    The first one stays and the others are removed.
    """
    is_duplicated = df.duplicated(keep="first")
    duplicated_rows = df[is_duplicated]
    if not duplicated_rows.empty:
        logger.warning(
            "Dropped %d duplicated rows: %s",
            len(duplicated_rows),
            list(duplicated_rows["order_id"]),
        )
    return df[~is_duplicated].copy()


def clean_region(df: pd.DataFrame) -> pd.DataFrame:
    """Return a copy with region names written the same way.

    Spaces around the name are removed and only the first letter is a capital,
    so " south" and "SOUTH " both become "South".
    """
    cleaned_df = df.copy()
    cleaned_region = cleaned_df["region"].str.strip().str.title()
    changed_count = (cleaned_region != cleaned_df["region"]).sum()
    logger.info("Fixed the region name in %d rows", changed_count)
    cleaned_df["region"] = cleaned_region
    return cleaned_df


def clean_quantity(df: pd.DataFrame) -> pd.DataFrame:
    """Return a copy with quantity as integers.

    Spaces used to separate thousands are removed, so "1 762" becomes 1762.
    Rows where quantity is still not an integer are dropped.
    Negative quantities are kept and treated as returns.
    """
    cleaned_df = df.copy()
    has_space = cleaned_df["quantity"].str.contains(" ")
    logger.info("Removed spaces from quantity in %d rows", has_space.sum())
    cleaned_df["quantity"] = cleaned_df["quantity"].str.replace(" ", "")

    is_number = cleaned_df["quantity"].str.fullmatch(QUANTITY_PATTERN)
    dropped_rows = cleaned_df[~is_number]
    if not dropped_rows.empty:
        logger.warning(
            "Dropped %d rows with a quantity that is not an integer: %s",
            len(dropped_rows),
            list(dropped_rows["order_id"]),
        )
    cleaned_df = cleaned_df[is_number].copy()
    cleaned_df["quantity"] = cleaned_df["quantity"].astype(int)

    negative_count = (cleaned_df["quantity"] < 0).sum()
    logger.info("Kept %d rows with a negative quantity as returns", negative_count)
    return cleaned_df


def main() -> None:
    """Run the whole pipeline."""
    df = load_sales(INPUT_PATH)
    df = clean_column_names(df)
    df = drop_rows_without_order_id(df)
    df = drop_duplicate_rows(df)
    df = clean_region(df)
    df = clean_quantity(df)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    main()
