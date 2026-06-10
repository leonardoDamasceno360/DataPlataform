from runtime.automations import AUTOMATIONS
from runtime.core.schema_utils import find_column, normalize_text


def detect_by_filename(file_name=""):
    file_name = normalize_text(file_name)

    if "speed" in file_name:
        return "Speed"
    if "gems" in file_name:
        return "Gems"
    if "xcelerate" in file_name:
        return "XCelerate"
    if "period" in file_name:
        return "PeriÃ³dicos"
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


def detect_by_content(df, filename_guess=None):
    if df is None or df.empty:
        return None

    candidates = []

    for base_name, automation in AUTOMATIONS.items():
        column_specs = getattr(
            automation,
            "COLUMN_SPECS",
            None,
        )

        if not column_specs:
            continue

        matched = sum(
            1
            for _, aliases in column_specs
            if find_column(df, aliases)
        )
        total = len(column_specs)

        if matched == 0:
            continue

        candidates.append(
            (
                matched / total,
                matched,
                1 if base_name == filename_guess else 0,
                -total,
                base_name,
            )
        )

    if not candidates:
        return None

    best_ratio, best_matched, _, _, best_name = max(candidates)

    if best_matched >= 2 and best_ratio >= 0.67:
        return best_name

    if best_ratio == 1:
        return best_name

    return None


def detect_automation(df, file_name=""):
    filename_guess = detect_by_filename(file_name)
    content_guess = detect_by_content(
        df,
        filename_guess=filename_guess,
    )

    return content_guess or filename_guess
