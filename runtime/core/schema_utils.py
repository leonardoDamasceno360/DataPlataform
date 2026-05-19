import re
import unicodedata


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
