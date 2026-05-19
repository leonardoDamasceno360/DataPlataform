from runtime.core.schema_utils import normalize_text


def detect_automation(df, file_name=""):
    file_name = normalize_text(file_name)

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
    if "ot" in file_name or "overtime" in file_name:
        return "OT"
    if "inter" in file_name or "interjornada" in file_name or "rp" in file_name:
        return "Rest Period"
    if "ass" in file_name or "document" in file_name:
        return "Documentos"
    if "qg" in file_name or "quadro" in file_name:
        return "Quadro Geral"
    if "separation" in file_name:
        return "Separation Forms"
    if "ultima" in file_name or "mov" in file_name or "sal" in file_name:
        return "Ult Mov Sal"
    if "deslig" in file_name or "demit" in file_name or "colaborador" in file_name:
        return "Desligados Geral"

    return None
