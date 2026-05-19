import pandas as pd

from runtime.core.schema_utils import (
    clean_column_name,
    normalize_text
)


def detect_header_row(preview_df):

    expected_terms = [
        "id",
        "nomeador",
        "employee number",
        "avaliacao",
        "situacao",
        "data da nomeacao"
    ]

    for idx, row in preview_df.iterrows():

        values = [
            normalize_text(str(value))
            for value in row.values
        ]

        matches = sum(
            1
            for term in expected_terms
            if term in values
        )

        if matches >= 2:
            return idx

    return 0


def load_excel(file):

    preview_df = pd.read_excel(
        file,
        header=None,
        nrows=15
    )

    header_row = detect_header_row(preview_df)

    file.seek(0)

    df = pd.read_excel(
        file,
        header=header_row
    )

    return df


def load_csv(file):

    return pd.read_csv(file)


def load_file(file):

    if file.name.endswith(".csv"):

        df = load_csv(file)

    else:

        df = load_excel(file)

    df = df.dropna(how="all")

    df.columns = [
        clean_column_name(col)
        for col in df.columns
    ]

    return df