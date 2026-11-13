import re
import operator

import pandas

OPERATORS = {"+": operator.add, "-": operator.sub, "*": operator.mul}


def _is_valid_label(label: str) -> bool:
    """Return True if label is a non-empty string of letters and underscores."""
    if not isinstance(label, str):
        return False
    if re.fullmatch(r"[a-zA-Z_]+", label):
        return True
    return False


def _tokenize(role: str) -> list[str] | None:
    """Split the role into a list of column names and operators.

    Return None if the role contains a character that is not allowed.
    """
    tokens = re.findall(r"[a-zA-Z_]+|[+\-*]", role)
    if "".join(tokens) != "".join(role.split()):
        return None
    return tokens


def _is_valid_expression(tokens: list[str], columns: pandas.Index) -> bool:
    """Return True if the tokens alternate between operands and operators.

    A valid expression starts and ends with an operand.
    """
    if len(tokens) % 2 == 0:
        return False
    operands_ok = all(token in columns for token in tokens[::2])
    operators_ok = all(token in OPERATORS for token in tokens[1::2])
    return operands_ok and operators_ok


def _evaluate(df: pandas.DataFrame, tokens: list[str]) -> pandas.Series:
    """Compute the expression described by the tokens.

    Multiplication is applied before addition and subtraction.
    The tokens must already be validated with _is_valid_expression.
    """
    total = 0
    pending = "+"
    term = df[tokens[0]]
    symbols = tokens[1::2]
    operands = tokens[2::2]
    for symbol, operand in zip(symbols, operands):
        if symbol == "*":
            term = OPERATORS[symbol](term, df[operand])
        else:
            total = OPERATORS[pending](total, term)
            pending = symbol
            term = df[operand]
    return OPERATORS[pending](total, term)


def add_virtual_column(df: pandas.DataFrame, role: str, new_column: str) -> pandas.DataFrame:
    """Return a copy of the DataFrame with a new column computed from the role.

    Return an empty DataFrame if the role or any column label is invalid.
    The input DataFrame is never modified.
    """
    if not _is_valid_label(new_column) or not all(_is_valid_label(label) for label in df.columns):
        return pandas.DataFrame([])

    tokens = _tokenize(role)
    if tokens is None:
        return pandas.DataFrame([])

    if not _is_valid_expression(tokens, df.columns):
        return pandas.DataFrame([])

    virtual_column = _evaluate(df, tokens)
    copied_df = df.copy()
    copied_df[new_column] = virtual_column
    return copied_df
