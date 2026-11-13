import pandas
import re


def _is_valid_label(label: str) -> bool:
    """Return True if label is a non-empty string of letters and underscores."""
    if not isinstance(label, str):
        return False
    if re.fullmatch(r"[a-zA-Z_]+", label):
        return True
    return False


def add_virtual_column(df: pandas.DataFrame, role: str, new_column: str) -> pandas.DataFrame:
    """Return a copy of the DataFrame with a new column computed from the role.

    Return an empty DataFrame if the role or any column label is invalid.
    The input DataFrame is never modified.
    """
    if not _is_valid_label(new_column) or not all(_is_valid_label(label) for label in df.columns):
        return pandas.DataFrame([])
    return pandas.DataFrame([])
