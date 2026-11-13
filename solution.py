import re
import operator

import pandas

OPERATORS = {"+": operator.add, "-": operator.sub, "*": operator.mul}
NUMBER_PATTERN = r"[0-9]+(?:\.[0-9]+)?"


def _is_valid_label(label: str) -> bool:
    """Return True if label is a non-empty string of letters and underscores."""
    if not isinstance(label, str):
        return False
    if re.fullmatch(r"[a-zA-Z_]+", label):
        return True
    return False


def _is_number(token: str) -> bool:
    """Return True if the token is an integer or decimal number such as 2 or 2.5."""
    if re.fullmatch(NUMBER_PATTERN, token):
        return True
    return False


def _tokenize(role: str) -> list[str] | None:
    """Split the role into a list of column names, numbers and operators.

    Return None if the role contains a character that is not allowed.
    """
    tokens = re.findall(rf"[a-zA-Z_]+|{NUMBER_PATTERN}|[+\-*]", role)
    if "".join(tokens) != "".join(role.split()):
        return None
    return tokens


def _is_operand(token: str, columns: pandas.Index) -> bool:
    """Return True if the token is an existing column name or a number."""
    if token in columns or _is_number(token):
        return True
    return False


def _is_valid_expression(tokens: list[str], columns: pandas.Index) -> bool:
    """Return True if the tokens form a valid expression.

    Operands and operators must alternate, starting and ending with an operand.
    An operand is an existing column name or a number, and the expression
    must use at least one column.
    """
    if len(tokens) % 2 == 0:
        return False
    operands_ok = all(_is_operand(token, columns) for token in tokens[::2])
    has_column = any(token in columns for token in tokens[::2])
    operators_ok = all(token in OPERATORS for token in tokens[1::2])
    return operands_ok and has_column and operators_ok


def _are_numeric(df: pandas.DataFrame, columns: list[str]) -> bool:
    """Return True if all the given columns contain numbers."""
    return all(pandas.api.types.is_numeric_dtype(df[column]) for column in columns)


def _operand_value(df: pandas.DataFrame, token: str) -> pandas.Series | int | float:
    """Return the number or the column that the token stands for."""
    if _is_number(token):
        return float(token) if "." in token else int(token)
    return df[token]


def _evaluate(df: pandas.DataFrame, tokens: list[str]) -> pandas.Series:
    """Compute the expression described by the tokens.

    Multiplication is applied before addition and subtraction.
    The tokens must already be validated with _is_valid_expression.
    """
    total = 0
    pending = "+"
    term = _operand_value(df, tokens[0])
    symbols = tokens[1::2]
    operands = tokens[2::2]
    for symbol, operand in zip(symbols, operands):
        if symbol == "*":
            term = OPERATORS[symbol](term, _operand_value(df, operand))
        else:
            total = OPERATORS[pending](total, term)
            pending = symbol
            term = _operand_value(df, operand)
    return OPERATORS[pending](total, term)


def add_virtual_column(df: pandas.DataFrame, role: str, new_column: str) -> pandas.DataFrame:
    """Return a copy of the DataFrame with a new column computed from the role.

    Return an empty DataFrame if the role or any column label is invalid.
    The input DataFrame is never modified.
    """
    if not _is_valid_label(new_column) or not all(_is_valid_label(label) for label in df.columns):
        return pandas.DataFrame([])

    if new_column in df.columns:
        return pandas.DataFrame([])

    tokens = _tokenize(role)
    if tokens is None:
        return pandas.DataFrame([])

    if not _is_valid_expression(tokens, df.columns):
        return pandas.DataFrame([])

    used_columns = [token for token in tokens[::2] if token in df.columns]
    if not _are_numeric(df, used_columns):
        return pandas.DataFrame([])

    virtual_column = _evaluate(df, tokens)
    copied_df = df.copy()
    copied_df[new_column] = virtual_column
    return copied_df
