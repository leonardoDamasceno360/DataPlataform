import base64
import os
import sys
from pathlib import Path


APP_NAME = "Data Operations Platform"
APP_SUBTITLE = (
    "Enterprise-grade HR and operations processing for batch "
    "automation, validation, previews, downloads, and audit history."
)
MAX_WORKERS = 4
PREVIEW_ROWS = 100
HISTORY_PREVIEW_LIMIT = 20

PIPELINE_DISPLAY_NAMES = {
    "IBelong": "iBelong",
    "Speed": "Speed",
    "Periódicos": "Periodic Exams",
    "Gems": "Gems",
    "XCelerate": "XCelerate",
    "Rest Period": "RP",
    "OT": "OT",
    "Separation Forms": "Separations Forms",
    "Quadro Geral": "Quadro Geral - HC",
    "Documentos": "Documents",
    "Desligados Geral": "Separated Employees",
    "Ult Mov Sal": "Salary Movement",
}

PIPELINE_SHEET_NAMES = {
    "Quadro Geral": "HC",
    "Separation Forms": "Separations Forms",
    "Rest Period": "RP",
    "OT": "OT",
}

PIPELINE_ORDER = [
    "IBelong",
    "Speed",
    "Periódicos",
    "Gems",
    "XCelerate",
    "Rest Period",
    "OT",
    "Separation Forms",
    "Quadro Geral",
    "Documentos",
    "Desligados Geral",
    "Ult Mov Sal",
]

SCHEMA_RULES = {
    "Speed": [
        "Employee Number",
        "Avaliação",
        "Current Appraisal Stage",
        "Manager Employee Number SPEED",
        "Manager Name Speed",
        "Reviewer Employee Number",
        "Reviewer Name",
        "Compliance",
    ],
    "Gems": [
        "ID",
        "Nomeador",
        "Data da Nomeação",
        "Premiação",
        "Tipo de Prêmio",
        "Marco de serviço",
        "Trimestre",
    ],
    "XCelerate": [
        "ID",
        "Status",
    ],
    "Periódicos": [
        "ID",
        "DATE EXPIRATION ASO",
        "STATUS ASO",
    ],
    "OT": [
        "Type of Day",
        "Total OT Hours Done",
        "Last OT Request Status",
    ],
    "Rest Period": [
        "Id Contratado",
        "Data do Dia (Data/Hora)",
        "Interjornada Praticada",
    ],
    "Quadro Geral": [
        "Segment HEAD",
        "Horizontal Line",
        "Sindicato",
        "Situação",
    ],
    "Documentos": [
        "Status da Assinatura Digital do Documento",
    ],
    "Separation Forms": [
        "Separation type",
    ],
    "Ult Mov Sal": [
        "ID",
        "EFECTIVE DATE",
    ],
    "Desligados Geral": [
        "Id Contratado",
        "SEPARATION REASON",
        "CATEGORY",
    ],
}

THEME_TOKENS = {
    "light": {
        "background": "#EDF2F8",
        "surface": "#FFFFFF",
        "surface_alt": "#E2EBF6",
        "sidebar": "#E3EBF5",
        "sidebar_surface": "#D7E2F0",
        "border": "#BECBDD",
        "text": "#112238",
        "muted": "#58708D",
        "accent": "#0F4C97",
        "accent_alt": "#0A356B",
        "success": "#0F7A5E",
        "error": "#B53A50",
        "warning": "#A66C1F",
        "shadow": "0 18px 42px rgba(15, 23, 42, 0.10)",
        "hero_ring": "rgba(15, 76, 151, 0.18)",
        "hero_glow": "rgba(10, 53, 107, 0.10)",
    },
    "dark": {
        "background": "#06101A",
        "surface": "#0E1A28",
        "surface_alt": "#16273B",
        "sidebar": "#040B14",
        "sidebar_surface": "#091220",
        "border": "#243852",
        "text": "#F1F6FC",
        "muted": "#A0B3C8",
        "accent": "#66A3FF",
        "accent_alt": "#2E6ED0",
        "success": "#4FC89C",
        "error": "#FF7A93",
        "warning": "#F4C15C",
        "shadow": "0 20px 50px rgba(0, 0, 0, 0.38)",
        "hero_ring": "rgba(102, 163, 255, 0.20)",
        "hero_glow": "rgba(46, 110, 208, 0.12)",
    },
}


def resource_path(relative_path):

    try:
        base_path = Path(sys._MEIPASS)
    except Exception:
        base_path = Path(__file__).resolve().parent.parent

    return base_path / relative_path


def get_app_home():

    configured_path = os.getenv("DATA_PLATFORM_HOME")

    if configured_path:
        return Path(configured_path)

    local_app_data = os.getenv("LOCALAPPDATA")

    if local_app_data:
        return Path(local_app_data) / "DataPlatform"

    return Path.home() / ".dataplatform"


APP_HOME = get_app_home()
OUTPUT_ROOT = Path(
    os.getenv(
        "DATA_PLATFORM_OUTPUT_DIR",
        APP_HOME / "data" / "outputs",
    )
)
HISTORY_ROOT = Path(
    os.getenv(
        "DATA_PLATFORM_HISTORY_DIR",
        APP_HOME / "data" / "history",
    )
)
CACHE_ROOT = Path(
    os.getenv(
        "DATA_PLATFORM_CACHE_DIR",
        APP_HOME / "data" / "cache",
    )
)
LOG_ROOT = Path(
    os.getenv(
        "DATA_PLATFORM_LOG_DIR",
        APP_HOME / "data" / "logs",
    )
)
EXECUTION_HISTORY_FILE = LOG_ROOT / "execution_history.jsonl"

OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
HISTORY_ROOT.mkdir(parents=True, exist_ok=True)
CACHE_ROOT.mkdir(parents=True, exist_ok=True)
LOG_ROOT.mkdir(parents=True, exist_ok=True)


def load_logo_base64(file_name):

    candidates = [
        resource_path(f"runtime/assets/{file_name}"),
        resource_path(f"assets/{file_name}"),
    ]

    logo_path = next(
        (path for path in candidates if path.exists()),
        None,
    )

    if logo_path is None:
        return None

    return base64.b64encode(
        logo_path.read_bytes()
    ).decode("utf-8")


LOGO_VARIANTS = {
    "light": load_logo_base64("tcs_logo_black.png"),
    "dark": load_logo_base64("tcs_logo_white.png"),
}
