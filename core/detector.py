def detect_automation(df, file_name=None):
    file_name = (file_name or "").lower()

    # 1) Nome do arquivo (mais confiável)
    if "ibelong" in file_name:
        return "IBelong"
    if "xcelerate" in file_name:
        return "Xcelerate"
    if "gems" in file_name:
        return "Gems"
    if "period" in file_name or "periód" in file_name:
        return "Periódicos"
    if "speed" in file_name:
        return "Speed"

    # 2) Fallback por colunas
    cols = [str(c).lower() for c in df.columns]

    if "date expiration aso" in cols:
        return "Periódicos"

    if "employee number" in cols and "compliance" in cols:
        return "Speed"

    if "nomeador" in cols:
        return "Gems"

    if "competency match %" in cols:
        return "Xcelerate"

    # 3) Fallback por conteúdo (IBelong header deslocado)
    preview = df.head(20).astype(str)
    text_blob = " ".join(map(str, preview.values.flatten())).lower()

    if "new joiner feedback compliance report" in text_blob:
        return "IBelong"

    return None