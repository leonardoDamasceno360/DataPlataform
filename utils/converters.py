import pandas as pd

def to_percentage(series):
    s = series.astype(str).str.replace("%", "").str.strip()
    s = pd.to_numeric(s, errors="coerce")

    # Caso padrão: já vem como 0.85
    return s