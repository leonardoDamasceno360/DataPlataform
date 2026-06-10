import re
import unicodedata
from datetime import datetime

import pandas as pd


MOJIBAKE_REPLACEMENTS = {
    "Ã¡": "á",
    "Ã ": "à",
    "Ã¢": "â",
    "Ã£": "ã",
    "Ã¤": "ä",
    "Ã©": "é",
    "Ãª": "ê",
    "Ã­": "í",
    "Ã³": "ó",
    "Ã´": "ô",
    "Ãµ": "õ",
    "Ãº": "ú",
    "Ã§": "ç",
    "Ã": "Ç",
    "Â": "",
    "\ufeff": "",
    "\u200b": "",
    "\u200c": "",
    "\u200d": "",
    "\xa0": " ",
}


def _repair_mojibake(text):

    repaired = str(text)

    for source, target in MOJIBAKE_REPLACEMENTS.items():
        repaired = repaired.replace(source, target)

    return repaired


def clean_column_name(col):

    cleaned = _repair_mojibake(col)
    cleaned = cleaned.replace("\r", " ")
    cleaned = cleaned.replace("\n", " ")
    cleaned = cleaned.replace("\t", " ")
    cleaned = "".join(
        char for char in cleaned
        if unicodedata.category(char)[0] != "C"
        or char == " "
    )
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned.strip()


def normalize_text(text):

    cleaned = clean_column_name(text).lower()
    cleaned = unicodedata.normalize("NFKD", cleaned)
    cleaned = "".join(
        char for char in cleaned
        if not unicodedata.combining(char)
    )
    cleaned = re.sub(r"[^a-z0-9]+", " ", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned.strip()


def normalized_columns(df):

    return {
        normalize_text(col): col
        for col in df.columns.astype(str)
    }


def find_column(df, aliases):

    normalized = normalized_columns(df)

    for alias in aliases:
        alias_norm = normalize_text(alias)

        if alias_norm in normalized:
            return normalized[alias_norm]

    return None


def require_column(df, aliases, field_name=None):

    column = find_column(df, aliases)

    if column:
        return column

    expected_name = field_name or aliases[0]

    raise ValueError(
        f"Required column not found: {expected_name}"
    )


def select_and_rename_columns(df, column_specs):

    selected_columns = []
    renamed_columns = []

    for output_name, aliases in column_specs:
        selected_columns.append(
            require_column(
                df,
                aliases,
                field_name=output_name,
            )
        )
        renamed_columns.append(output_name)

    result = df[selected_columns].copy()
    result.columns = renamed_columns
    return result


def current_report_month():

    return datetime.today().date()


CONNECT_TYPE_REMOVED_OPTIONS = {
    "second project",
    "project 2",
    "segundo projeto",
    "2nd project",
}


def _clean_connect_type_value(value):

    if pd.isna(value):
        return value

    text = clean_column_name(value)

    if not text:
        return value

    if normalize_text(text) in CONNECT_TYPE_REMOVED_OPTIONS:
        return ""

    parts = [
        part.strip()
        for part in re.split(r"[,\n;|]+", text)
    ]

    if len(parts) <= 1:
        return value

    filtered_parts = [
        part
        for part in parts
        if normalize_text(part) not in CONNECT_TYPE_REMOVED_OPTIONS
    ]

    if len(filtered_parts) == len(parts):
        return value

    return ", ".join(filtered_parts)


def sanitize_connect_type_columns(df):

    result = df.copy()

    for column in result.columns:
        normalized_name = normalize_text(column)

        if "connect" not in normalized_name:
            continue

        if "type" not in normalized_name:
            continue

        result[column] = result[column].apply(
            _clean_connect_type_value
        )

    return result
