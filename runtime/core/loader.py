import pandas as pd

from runtime.core.schema_utils import (
    clean_column_name,
    normalize_text
)


HEADER_HINTS = {
    "id",
    "nomeador",
    "employee number",
    "avaliacao",
    "situacao",
    "data da nomeacao",
    "segment head",
    "horizontal line",
    "status",
    "date expiration aso",
    "new joinee emp id",
    "separation reason",
    "termination reason",
    "separation type",
    "category",
    "id contratado",
}


def detect_header_row(preview_df):

    best_idx = 0
    best_score = -1

    for idx, row in preview_df.iterrows():

        values = {
            normalize_text(str(value))
            for value in row.values
        }

        matches = sum(
            1
            for term in HEADER_HINTS
            if term in values
        )

        if matches >= 2:
            return idx

        if matches > best_score:
            best_idx = idx
            best_score = matches

    return best_idx if best_score > 0 else 0


def load_excel(file, selected_aliases=None):
    usecols = build_usecols_filter(selected_aliases)
    last_error = None

    for engine in resolve_excel_engines(file.name):
        try:
            file.seek(0)
            preview_df = pd.read_excel(
                file,
                header=None,
                nrows=15,
                engine=engine,
            )

            header_row = detect_header_row(preview_df)

            file.seek(0)

            return pd.read_excel(
                file,
                header=header_row,
                usecols=usecols,
                engine=engine,
            )
        except Exception as exc:
            last_error = exc

    raise last_error


def should_redetect_header(columns):

    normalized = [
        normalize_text(str(column))
        for column in columns
    ]

    header_hints = {
        "id",
        "nome completo",
        "employee number",
        "segment head",
        "horizontal line",
        "situacao",
        "status",
        "date expiration aso",
        "new joinee emp id",
    }

    if any(column in header_hints for column in normalized):
        return False

    unnamed_like = sum(
        1
        for column in normalized
        if not column or column.startswith("unnamed")
    )

    return unnamed_like >= max(1, len(normalized) // 3)


def load_csv(file, selected_aliases=None):

    usecols = build_usecols_filter(selected_aliases)

    attempts = [
        {"encoding": "utf-8-sig", "sep": None, "engine": "python"},
        {"encoding": "utf-8", "sep": None, "engine": "python"},
        {"encoding": "latin1", "sep": None, "engine": "python"},
    ]
    last_error = None

    for kwargs in attempts:
        try:
            file.seek(0)
            return pd.read_csv(
                file,
                usecols=usecols,
                **kwargs,
            )
        except Exception as exc:
            last_error = exc

    raise last_error


def build_usecols_filter(selected_aliases):

    if not selected_aliases:
        return None

    normalized_aliases = {
        normalize_text(alias)
        for alias in selected_aliases
    }

    def usecols(column_name):
        return normalize_text(column_name) in normalized_aliases

    return usecols


def resolve_excel_engines(file_name):

    lowered = file_name.lower()
    engines = []

    if lowered.endswith((".xlsx", ".xlsm", ".xlsb", ".xls")):
        engines.extend(["calamine", "openpyxl"])

    if not engines:
        engines.append(None)

    unique_engines = []

    for engine in engines:
        if engine not in unique_engines:
            unique_engines.append(engine)

    return unique_engines


def load_file(file, selected_aliases=None):

    if file.name.endswith(".csv"):

        df = load_csv(
            file,
            selected_aliases=selected_aliases,
        )

    else:

        df = load_excel(
            file,
            selected_aliases=selected_aliases,
        )

    df = df.dropna(how="all")

    df.columns = [
        clean_column_name(col)
        for col in df.columns
    ]

    return df
