import logging

import pandas as pd

INPUT_PATH = "sales.csv"
OUTPUT_PATH = "revenue_by_region.csv"

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


def main() -> None:
    """Run the whole pipeline."""
    df = load_sales(INPUT_PATH)
    df = clean_column_names(df)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    main()
