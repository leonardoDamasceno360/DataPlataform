import re
import unicodedata


# =========================================================
# NORMALIZE TEXT
# =========================================================
def normalize_text(value):

    text = unicodedata.normalize(
        "NFKD",
        str(value).strip().lower()
    )

    text = "".join(
        char for char in text
        if not unicodedata.combining(char)
    )

    return re.sub(
        r"\s+",
        " ",
        text
    )


# =========================================================
# FIND COLUMN
# =========================================================
def find_column(
    df,
    aliases
):

    normalized = {

        normalize_text(col): col

        for col in df.columns
    }

    for alias in aliases:

        alias_norm = normalize_text(alias)

        if alias_norm in normalized:

            return normalized[
                alias_norm
            ]

    return None