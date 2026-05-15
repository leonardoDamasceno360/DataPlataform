import unicodedata
def normalize_text(text):

    text = unicodedata.normalize(
        "NFKD",
        str(text).lower()
    )

    return "".join(
        c for c in text
        if not unicodedata.combining(c)
    )
def detect_automation(df, file_name=""):

    file_name = normalize_text(file_name)

    # =====================================================
    # EXISTENTES
    # =====================================================

    if "speed" in file_name:
        return "Speed"

    if "gems" in file_name:
        return "Gems"

    if "xcelerate" in file_name:
        return "XCelerate"

    if "period" in file_name:
        return "Periódicos"

    if "ibelong" in file_name:
        return "IBelong"

    # =====================================================
    # NOVAS AUTOMAÇÕES
    # =====================================================

    # OT
    if (
        "ot" in file_name
        or
        "overtime" in file_name
    ):
        return "OT"
    
    

    # RP
    
    if (
        "inter" in file_name
        or
        "interjornada" in file_name
        or
        "rp" in file_name
    ):
        return "Rest Period"
    
    # Documentos
    if (
        "ass" in file_name
        or
        "document" in file_name
    ):
        return "Documentos"

    # QG
    if (
        "qg" in file_name
        or
        "quadro" in file_name
    ):
        return "Quadro Geral"

    # Separation Forms
    if (
        "separation" in file_name
    ):
        return "Separation Forms"

    # Ult Mov Sal
    if (
        "ultima" in file_name
        or
        "mov" in file_name
        or
        "sal" in file_name
    ):
        return "Ult Mov Sal"

    # Desligados
    if (
        "deslig" in file_name
        or
        "demit" in file_name
        or
        "colaborador" in file_name
    ):
        return "Desligados Geral"

    return None