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

    Return None if the role is not a string or contains a character that is not allowed.
    """
    if not isinstance(role, str):
        return None
    tokens = re.findall(rf"[a-zA-Z_]+|{NUMBER_PATTERN}|[+\-*]", role)
    if "".join(tokens) != "".join(role.split()):
        return None
    return tokens


def _merge_signs(tokens: list[str]) -> list[str]:
    """Join each minus that acts as a sign with the operand that follows it.

    A minus is a sign when it starts the expression or follows an operator.
    """
    merged = []
    index = 0
    while index < len(tokens):
        token = tokens[index]
        is_sign_position = not merged or merged[-1] in OPERATORS
        has_operand_next = index + 1 < len(tokens) and tokens[index + 1] not in OPERATORS
        if token == "-" and is_sign_position and has_operand_next:
            merged.append("-" + tokens[index + 1])
            index += 2
        else:
            merged.append(token)
            index += 1
    return merged


def _is_operand(token: str, columns: pandas.Index) -> bool:
    """Return True if the token is a column name or a number, with an optional minus sign."""
    name = token.removeprefix("-")
    return name in columns or _is_number(name)


def _is_valid_expression(tokens: list[str], columns: pandas.Index) -> bool:
    """Return True if the tokens form a valid expression.

    Operands and operators must alternate, starting and ending with an operand.
    An operand is an existing column name or a number, and the expression
    must use at least one column.
    """
    if len(tokens) % 2 == 0:
        return False
    operands_ok = all(_is_operand(token, columns) for token in tokens[::2])
    has_column = any(token.removeprefix("-") in columns for token in tokens[::2])
    operators_ok = all(token in OPERATORS for token in tokens[1::2])
    return operands_ok and has_column and operators_ok


def _are_numeric(df: pandas.DataFrame, columns: list[str]) -> bool:
    """Return True if all the given columns contain numbers.

    Boolean columns do not count as numbers.
    """
    return all(
        pandas.api.types.is_numeric_dtype(df[column])
        and not pandas.api.types.is_bool_dtype(df[column])
        for column in columns
    )


def _operand_value(df: pandas.DataFrame, token: str) -> pandas.Series | int | float:
    """Return the number or the column that the token stands for."""
    if token.startswith("-"):
        return -_operand_value(df, token.removeprefix("-"))
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

    The role is an expression of column names and numbers joined by +, - and *,
    for example "quantity * price - discount". A minus can also be a sign,
    as in "-a + b". Multiplication is applied before addition and subtraction.

    Return an empty DataFrame if the role or any column label is invalid.
    The input DataFrame is never modified.
    """
    if not _is_valid_label(new_column) or not all(_is_valid_label(label) for label in df.columns):
        return pandas.DataFrame([])

    if not df.columns.is_unique:
        return pandas.DataFrame([])

    if new_column in df.columns:
        return pandas.DataFrame([])

    tokens = _tokenize(role)
    if tokens is None:
        return pandas.DataFrame([])
    tokens = _merge_signs(tokens)

    if not _is_valid_expression(tokens, df.columns):
        return pandas.DataFrame([])

    operand_names = [token.removeprefix("-") for token in tokens[::2]]
    used_columns = [name for name in operand_names if name in df.columns]
    if not _are_numeric(df, used_columns):
        return pandas.DataFrame([])

    virtual_column = _evaluate(df, tokens)
    copied_df = df.copy()
    copied_df[new_column] = virtual_column
    return copied_df
