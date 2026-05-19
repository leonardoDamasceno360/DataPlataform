# =========================================================
# IMPORTS
# =========================================================
import base64
import hashlib
import html
import io
import logging
import os
import sys
import zipfile

from concurrent.futures import (
    ThreadPoolExecutor,
    as_completed,
)
from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st


# =========================================================
# PATH
# =========================================================
PROJECT_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# =========================================================
# INTERNAL IMPORTS
# =========================================================
from runtime.automations import AUTOMATIONS
from runtime.core.detector import detect_automation
from runtime.core.engine import AutomationEngine
from runtime.core.loader import load_file
from runtime.core.schema_utils import (
    normalized_columns,
    normalize_text,
)


# =========================================================
# APP CONFIG
# =========================================================
st.set_page_config(
    page_title="Data Operations Platform",
    page_icon=":bar_chart:",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =========================================================
# LOGGING
# =========================================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger("data_platform")


# =========================================================
# CONSTANTS
# =========================================================
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
    "PeriÃ³dicos": "Periodic Exams",
    "Gems": "Gems",
    "XCelerate": "XCelerate",
    "Rest Period": "Rest Period",
    "OT": "Overtime",
    "Separation Forms": "Separation Forms",
    "Quadro Geral": "Workforce Overview",
    "Documentos": "Documents",
    "Desligados Geral": "Separated Employees",
    "Ult Mov Sal": "Salary Movement",
}

PIPELINE_ORDER = [
    "IBelong",
    "Speed",
    "PeriÃ³dicos",
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
        "AvaliaÃ§Ã£o",
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
        "Data da NomeaÃ§Ã£o",
        "PremiaÃ§Ã£o",
        "Tipo de PrÃªmio",
        "Marco de serviÃ§o",
        "Trimestre",
    ],
    "XCelerate": [
        "ID",
        "Status",
    ],
    "PeriÃ³dicos": [
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
        "SituaÃ§Ã£o",
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
        "background": "#F3F6FB",
        "surface": "#FFFFFF",
        "surface_alt": "#E9EEF7",
        "sidebar": "#F7F9FD",
        "sidebar_surface": "#EEF3FA",
        "border": "#D7E0EE",
        "text": "#102033",
        "muted": "#5E7188",
        "accent": "#1F5AA6",
        "accent_alt": "#2C4C8F",
        "success": "#147A5A",
        "error": "#B5475C",
        "warning": "#B67A2D",
        "shadow": "0 16px 40px rgba(15, 23, 42, 0.08)",
        "hero_ring": "rgba(31, 90, 166, 0.16)",
    },
    "dark": {
        "background": "#07111F",
        "surface": "#0C1728",
        "surface_alt": "#132238",
        "sidebar": "#060D18",
        "sidebar_surface": "#0B1424",
        "border": "#22324A",
        "text": "#EDF3FB",
        "muted": "#9AAAC1",
        "accent": "#7BA7F0",
        "accent_alt": "#5F8FDB",
        "success": "#4AC39A",
        "error": "#FF8194",
        "warning": "#F6C26A",
        "shadow": "0 18px 40px rgba(0, 0, 0, 0.34)",
        "hero_ring": "rgba(123, 167, 240, 0.16)",
    },
}


# =========================================================
# RESOURCE PATHS
# =========================================================
def resource_path(relative_path):

    try:
        base_path = Path(sys._MEIPASS)
    except Exception:
        base_path = Path(__file__).resolve().parent.parent

    return base_path / relative_path


def rerun_app():

    if hasattr(st, "rerun"):
        st.rerun()
        return

    st.experimental_rerun()


def safe_text(value, fallback="Not available"):

    if value is None:
        return fallback

    return str(value)


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

OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
HISTORY_ROOT.mkdir(parents=True, exist_ok=True)


# =========================================================
# LOGO
# =========================================================
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


# =========================================================
# THEME
# =========================================================
def get_effective_theme(theme_selection):

    if theme_selection == "Light":
        return "light"

    if theme_selection == "Dark":
        return "dark"

    configured_theme = (
        st.get_option("theme.base")
        or "light"
    ).lower()

    return (
        "dark"
        if configured_theme == "dark"
        else "light"
    )


def get_requested_theme():

    if "theme_selector" in st.session_state:
        return st.session_state["theme_selector"]

    return st.session_state.get(
        "ui_theme",
        "Auto",
    )


def inject_global_styles(theme_mode):

    tokens = THEME_TOKENS[theme_mode]

    st.markdown(
        f"""
        <style>
        :root {{
            --app-bg: {tokens["background"]};
            --surface: {tokens["surface"]};
            --surface-alt: {tokens["surface_alt"]};
            --sidebar: {tokens["sidebar"]};
            --sidebar-surface: {tokens["sidebar_surface"]};
            --border: {tokens["border"]};
            --text: {tokens["text"]};
            --muted: {tokens["muted"]};
            --accent: {tokens["accent"]};
            --accent-alt: {tokens["accent_alt"]};
            --success: {tokens["success"]};
            --error: {tokens["error"]};
            --warning: {tokens["warning"]};
            --shadow: {tokens["shadow"]};
            --hero-ring: {tokens["hero_ring"]};
            --radius-lg: 20px;
            --radius-md: 16px;
            --radius-sm: 12px;
        }}

        html, body, [data-testid="stAppViewContainer"], .stApp {{
            background: var(--app-bg);
            color: var(--text);
        }}

        [data-testid="stHeader"] {{
            background: transparent;
        }}

        [data-testid="stSidebar"] {{
            background:
                radial-gradient(circle at top left, rgba(255,255,255,0.05), transparent 32%),
                linear-gradient(180deg, var(--sidebar) 0%, var(--sidebar-surface) 100%);
            border-right: 1px solid var(--border);
            min-width: 292px !important;
            max-width: 292px !important;
        }}

        [data-testid="stSidebar"] * {{
            color: var(--text);
        }}

        .main .block-container {{
            max-width: 1240px;
            padding-top: 0.9rem;
            padding-bottom: 2rem;
        }}

        h1, h2, h3, h4, h5, h6, p, span, label, div {{
            color: inherit;
        }}

        .hero-card {{
            position: relative;
            overflow: hidden;
            padding: 1.2rem 1.3rem 1.1rem 1.3rem;
            border-radius: var(--radius-lg);
            background:
                radial-gradient(circle at top right, var(--hero-ring), transparent 26%),
                linear-gradient(135deg, var(--surface) 0%, var(--surface-alt) 100%);
            border: 1px solid var(--border);
            box-shadow: var(--shadow);
            margin-bottom: 0.9rem;
        }}

        .hero-title {{
            font-size: clamp(1.7rem, 2vw, 2.35rem);
            line-height: 1.08;
            font-weight: 700;
            letter-spacing: -0.03em;
            margin: 0 0 0.45rem 0;
            overflow-wrap: anywhere;
        }}

        .hero-subtitle {{
            max-width: 760px;
            color: var(--muted);
            font-size: 0.9rem;
            line-height: 1.5;
            margin: 0;
        }}

        .hero-chip-row {{
            display: flex;
            flex-wrap: wrap;
            gap: 0.55rem;
            margin-top: 0.9rem;
        }}

        .hero-chip {{
            border-radius: 999px;
            padding: 0.48rem 0.8rem;
            background: rgba(255,255,255,0.3);
            border: 1px solid var(--border);
            font-size: 0.79rem;
            color: var(--muted);
            white-space: nowrap;
        }}

        .logo-shell {{
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 100%;
            padding: 0.8rem 0.9rem 0.72rem 0.9rem;
            border-radius: 18px;
            background: rgba(255,255,255,0.05);
            border: 1px solid var(--border);
            margin-bottom: 0.75rem;
            backdrop-filter: blur(10px);
        }}

        .logo-shell img {{
            width: 100%;
            max-width: 184px;
            height: auto;
            object-fit: contain;
            display: block;
        }}

        .section-caption {{
            font-size: 0.76rem;
            text-transform: uppercase;
            letter-spacing: 0.16em;
            color: var(--muted);
            margin-bottom: 0.3rem;
            font-weight: 700;
        }}

        .section-title {{
            font-size: 1.14rem;
            line-height: 1.2;
            margin: 0 0 0.3rem 0;
            font-weight: 700;
        }}

        .section-copy {{
            color: var(--muted);
            font-size: 0.88rem;
            line-height: 1.5;
            margin: 0 0 0.85rem 0;
        }}

        .metric-card {{
            border-radius: var(--radius-md);
            border: 1px solid var(--border);
            background: linear-gradient(180deg, var(--surface) 0%, var(--surface-alt) 100%);
            box-shadow: var(--shadow);
            padding: 1rem 1.05rem;
            min-height: 114px;
            max-height: 114px;
            height: 100%;
        }}

        .metric-label {{
            color: var(--muted);
            font-size: 0.78rem;
            text-transform: uppercase;
            letter-spacing: 0.12em;
            font-weight: 700;
            line-height: 1.35;
        }}

        .metric-value {{
            margin-top: 0.55rem;
            font-size: clamp(1.28rem, 1.5vw, 1.75rem);
            font-weight: 700;
            line-height: 1.08;
            overflow-wrap: anywhere;
        }}

        .metric-footnote {{
            margin-top: 0.6rem;
            color: var(--muted);
            font-size: 0.79rem;
            line-height: 1.35;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }}

        .sidebar-card {{
            border-radius: 16px;
            background: rgba(255,255,255,0.04);
            border: 1px solid var(--border);
            padding: 0.85rem 0.9rem;
            margin-bottom: 0.7rem;
        }}

        .sidebar-card h4 {{
            margin: 0 0 0.45rem 0;
            font-size: 0.95rem;
            font-weight: 700;
            color: var(--text);
        }}

        .sidebar-card p {{
            margin: 0;
            color: var(--muted);
            font-size: 0.86rem;
            line-height: 1.55;
        }}

        .sidebar-meta {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 0.6rem;
            border-radius: 14px;
            border: 1px solid var(--border);
            background: rgba(255,255,255,0.03);
            padding: 0.72rem 0.85rem;
            margin-bottom: 0.75rem;
        }}

        .sidebar-meta strong {{
            display: block;
            font-size: 0.82rem;
            line-height: 1.2;
        }}

        .sidebar-meta span {{
            display: block;
            color: var(--muted);
            font-size: 0.76rem;
            margin-top: 0.12rem;
        }}

        .sidebar-badge {{
            padding: 0.32rem 0.58rem;
            border-radius: 999px;
            background: rgba(31, 90, 166, 0.12);
            color: var(--accent);
            font-size: 0.74rem;
            font-weight: 700;
            white-space: nowrap;
        }}

        .pipeline-pill {{
            display: inline-flex;
            align-items: center;
            gap: 0.45rem;
            width: 100%;
            padding: 0.58rem 0.72rem;
            margin-bottom: 0.45rem;
            border-radius: 12px;
            background: rgba(255,255,255,0.04);
            border: 1px solid var(--border);
            font-size: 0.82rem;
            color: var(--text);
        }}

        .pipeline-dot {{
            width: 8px;
            height: 8px;
            border-radius: 999px;
            background: #7BA7F0;
            flex: 0 0 auto;
        }}

        .empty-panel {{
            border-radius: var(--radius-lg);
            border: 1px solid var(--border);
            background: linear-gradient(180deg, rgba(255,255,255,0.06), rgba(255,255,255,0.03));
            padding: 1.6rem 1.4rem;
            text-align: center;
        }}

        .empty-panel h3 {{
            margin: 0 0 0.45rem 0;
            font-size: 1.25rem;
            font-weight: 700;
        }}

        .empty-panel p {{
            margin: 0 auto;
            max-width: 620px;
            color: var(--muted);
            line-height: 1.55;
        }}

        .status-note {{
            padding: 0.75rem 0.9rem;
            border-radius: 12px;
            background: rgba(255,255,255,0.03);
            border: 1px solid var(--border);
            color: var(--muted);
            font-size: 0.84rem;
            margin-top: 0;
            min-height: 3.5rem;
            display: flex;
            align-items: center;
        }}

        .upload-shell,
        .recovery-shell {{
            border-radius: var(--radius-lg);
            border: 1px solid var(--border);
            background: linear-gradient(180deg, rgba(255,255,255,0.06), rgba(255,255,255,0.03));
            padding: 1rem 1rem 0.85rem 1rem;
            box-shadow: var(--shadow);
            margin-bottom: 0.85rem;
        }}

        .upload-meta-row {{
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
            margin: 0 0 0.65rem 0;
        }}

        .upload-meta-pill {{
            padding: 0.42rem 0.68rem;
            border-radius: 999px;
            background: rgba(31, 90, 166, 0.1);
            border: 1px solid var(--border);
            color: var(--muted);
            font-size: 0.76rem;
            font-weight: 600;
        }}

        div[data-testid="stFileUploader"] {{
            border: 1.5px dashed var(--accent);
            background: linear-gradient(180deg, rgba(255,255,255,0.2), rgba(255,255,255,0.06));
            border-radius: 18px;
            padding: 0.55rem;
            box-shadow: inset 0 1px 0 rgba(255,255,255,0.08);
        }}

        div[data-testid="stFileUploader"]:hover {{
            border-color: var(--accent-alt);
            box-shadow: 0 0 0 4px rgba(31, 90, 166, 0.08);
        }}

        div.stButton > button,
        div[data-testid="stDownloadButton"] > button {{
            border-radius: 12px;
            border: 1px solid transparent;
            background: linear-gradient(180deg, var(--accent) 0%, var(--accent-alt) 100%);
            color: #FFFFFF;
            font-weight: 700;
            min-height: 2.8rem;
            box-shadow: 0 10px 22px rgba(31, 90, 166, 0.18);
            transition: transform 120ms ease, box-shadow 120ms ease, opacity 120ms ease;
            white-space: normal;
            line-height: 1.25;
        }}

        div.stButton > button:hover,
        div[data-testid="stDownloadButton"] > button:hover {{
            transform: translateY(-1px);
            box-shadow: 0 16px 28px rgba(31, 90, 166, 0.28);
        }}

        div.stButton > button[kind="secondary"] {{
            background: var(--surface);
            color: var(--text);
            border-color: var(--border);
            box-shadow: none;
        }}

        .stTabs [data-baseweb="tab-list"] {{
            align-items: center;
            gap: 0.35rem;
            background: transparent;
            margin-bottom: 0.6rem;
            flex-wrap: wrap;
        }}

        .stTabs [data-baseweb="tab"] {{
            min-height: 2.45rem;
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 999px;
            padding: 0.45rem 0.88rem;
            color: var(--muted);
            font-weight: 600;
            white-space: nowrap;
            font-size: 0.84rem;
        }}

        .stTabs [aria-selected="true"] {{
            color: #FFFFFF !important;
            background: linear-gradient(180deg, var(--accent) 0%, var(--accent-alt) 100%) !important;
            border-color: transparent !important;
        }}

        div[data-testid="stExpander"] {{
            border: 1px solid var(--border);
            border-radius: 16px;
            background: var(--surface);
            overflow: hidden;
        }}

        div[data-testid="stExpander"] details summary {{
            padding-top: 0.15rem;
            padding-bottom: 0.15rem;
        }}

        div[data-testid="stDataFrame"] {{
            border-radius: 16px;
            overflow: hidden;
            border: 1px solid var(--border);
            box-shadow: var(--shadow);
        }}

        div[data-testid="stCodeBlock"] {{
            border-radius: 18px;
            border: 1px solid var(--border);
        }}

        [data-baseweb="select"] > div,
        [data-baseweb="input"] > div,
        div[data-baseweb="base-input"] {{
            border-radius: 14px !important;
            border-color: var(--border) !important;
            background: var(--surface) !important;
        }}

        div[data-testid="stMarkdownContainer"] a {{
            color: var(--accent);
            text-decoration: none;
        }}

        .path-chip {{
            display: inline-flex;
            align-items: center;
            gap: 0.35rem;
            padding: 0.45rem 0.7rem;
            border-radius: 12px;
            background: rgba(255,255,255,0.04);
            border: 1px solid var(--border);
            color: var(--muted);
            font-size: 0.78rem;
            margin: 0.25rem 0.4rem 0 0;
        }}

        div[data-testid="column"] > div:has(.metric-card) {{
            height: 100%;
        }}

        .action-shell {{
            display: flex;
            align-items: stretch;
            height: 100%;
            margin-top: 0;
            min-height: 3.5rem;
        }}

        .action-shell .status-note {{
            width: 100%;
        }}

        .st-key-pipeline_popover button {{
            background: var(--surface) !important;
            color: var(--text) !important;
            border: 1px solid var(--border) !important;
            box-shadow: none !important;
            min-height: 2.55rem !important;
        }}

        .st-key-pipeline_popover button:hover {{
            border-color: var(--accent) !important;
            box-shadow: 0 8px 18px rgba(31, 90, 166, 0.12) !important;
        }}

        .st-key-clear_session_button button {{
            background: linear-gradient(180deg, #C63D4F 0%, #A82F42 100%) !important;
            color: #FFFFFF !important;
            border: 1px solid rgba(255,255,255,0.08) !important;
            box-shadow: 0 12px 24px rgba(168, 47, 66, 0.28) !important;
            margin-top: 0.7rem;
        }}

        .st-key-clear_session_button button:hover {{
            box-shadow: 0 16px 28px rgba(168, 47, 66, 0.34) !important;
        }}

        .st-key-clear_session_button {{
            position: sticky;
            bottom: 0.5rem;
            padding-top: 0.6rem;
            background: linear-gradient(180deg, rgba(0,0,0,0), var(--sidebar-surface) 30%);
        }}

        .st-key-process_button button {{
            min-height: 3.5rem;
            margin-top: 0;
            font-size: 0.92rem;
        }}

        @media (max-width: 1280px) {{
            .hero-title {{
                font-size: clamp(1.55rem, 2vw, 2.05rem);
            }}

            .hero-subtitle {{
                max-width: 100%;
            }}

            [data-testid="stSidebar"] {{
                min-width: 272px !important;
                max-width: 272px !important;
            }}
        }}

        @media (max-width: 980px) {{
            .hero-card {{
                padding: 1rem;
            }}

            .hero-chip-row {{
                gap: 0.55rem;
            }}

            .hero-chip {{
                white-space: normal;
            }}

            [data-testid="stSidebar"] {{
                min-width: auto !important;
                max-width: none !important;
            }}
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# HELPERS
# =========================================================
def pipeline_label(base_name):

    return PIPELINE_DISPLAY_NAMES.get(
        base_name,
        base_name,
    )


def file_hash(file_bytes, file_name):

    return hashlib.md5(
        file_name.encode("utf-8") + file_bytes
    ).hexdigest()


def build_file_object(file_bytes, file_name):

    file_like = io.BytesIO(file_bytes)
    file_like.name = file_name
    return file_like


def validate_input_schema(df, base_label):

    cols = normalized_columns(df)
    expected = SCHEMA_RULES.get(base_label, [])

    return [
        column_name
        for column_name in expected
        if normalize_text(column_name) not in cols
    ]


def build_output_name(base_label):

    current_date = datetime.now().strftime("%d%m%y")
    return f"{base_label}_{current_date}.xlsx"


def save_history(file_name, buffer):

    history_dir = (
        HISTORY_ROOT
        / datetime.today().strftime("%Y-%m-%d")
    )
    history_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path = history_dir / file_name
    output_path.write_bytes(buffer.getvalue())
    return output_path


def list_recent_history():

    files = []

    if not HISTORY_ROOT.exists():
        return files

    for path in HISTORY_ROOT.rglob("*"):
        if path.is_file():
            files.append(path)

    files.sort(
        key=lambda item: item.stat().st_mtime,
        reverse=True,
    )

    rows = []

    for path in files[:HISTORY_PREVIEW_LIMIT]:
        rows.append(
            {
                "File": path.name,
                "Folder": path.parent.name,
                "Modified": datetime.fromtimestamp(
                    path.stat().st_mtime
                ).strftime("%Y-%m-%d %H:%M"),
                "Size KB": round(
                    path.stat().st_size / 1024,
                    1,
                ),
            }
        )

    return rows


def format_output_path(path_obj):

    return str(path_obj).replace("\\", "/")


# =========================================================
# CACHE
# =========================================================
@st.cache_data(show_spinner=False)
def cached_detect(
    file_hash_key,
    file_bytes,
    file_name,
):

    df = load_file(
        build_file_object(
            file_bytes,
            file_name,
        )
    )

    return detect_automation(df, file_name)


@st.cache_data(show_spinner=False)
def cached_process(
    file_hash_key,
    df,
    base_label,
):

    engine = AutomationEngine(
        AUTOMATIONS[base_label]
    )
    return engine.run(df)


# =========================================================
# BUSINESS FLOW
# =========================================================
def process_file(
    file_name,
    file_bytes,
    selected_base=None,
):

    try:
        logger.info(
            "Starting processing for %s",
            file_name,
        )

        hash_key = file_hash(
            file_bytes,
            file_name,
        )

        detected_base = (
            selected_base
            or cached_detect(
                hash_key,
                file_bytes,
                file_name,
            )
        )

        if not detected_base:
            raise ValueError(
                "Automatic pipeline detection failed for this file."
            )

        input_df = load_file(
            build_file_object(
                file_bytes,
                file_name,
            )
        )

        if detected_base != "IBelong":
            missing = validate_input_schema(
                input_df,
                detected_base,
            )

            if missing:
                raise ValueError(
                    "Input schema validation failed for "
                    f"{pipeline_label(detected_base)}. Missing columns: "
                    f"{', '.join(missing)}"
                )

        result_df = cached_process(
            hash_key,
            input_df,
            detected_base,
        )

        rows = len(result_df)
        buffer = io.BytesIO()

        with pd.ExcelWriter(
            buffer,
            engine="openpyxl",
        ) as writer:
            result_df.to_excel(
                writer,
                sheet_name=detected_base[:31],
                index=False,
            )

        buffer.seek(0)

        output_name = build_output_name(
            detected_base
        )

        save_history(
            output_name,
            buffer,
        )

        display_base = pipeline_label(
            detected_base
        )

        return {
            "Hash": hash_key,
            "Base": detected_base,
            "DisplayBase": display_base,
            "Arquivo": file_name,
            "Status": "Success",
            "Rows": rows,
            "DataFrame": result_df,
            "Output": output_name,
            "Bytes": buffer.getvalue(),
            "Log": (
                f"{display_base} | "
                f"{rows} rows | Success"
            ),
        }

    except Exception as exc:
        logger.exception(
            "Processing failed for %s",
            file_name,
        )

        resolved_base = selected_base or "Unidentified"

        return {
            "Hash": hash_key,
            "Base": resolved_base,
            "DisplayBase": pipeline_label(
                resolved_base
            ),
            "Arquivo": file_name,
            "Status": "Error",
            "Rows": 0,
            "DataFrame": None,
            "Output": None,
            "Bytes": None,
            "ErrorMessage": str(exc),
            "Log": f"{file_name} | Error: {exc}",
        }


def process_uploaded_files(
    file_payloads,
    worker_count,
    manual_selection=None,
):

    results = []
    total_files = len(file_payloads)

    progress = st.progress(
        0,
        text="Preparing batch execution...",
    )
    status_placeholder = st.empty()

    with ThreadPoolExecutor(
        max_workers=worker_count
    ) as executor:
        futures = []

        for item in file_payloads:
            selected_base = None

            if manual_selection:
                selected_base = manual_selection.get(
                    item["name"]
                )

            futures.append(
                executor.submit(
                    process_file,
                    item["name"],
                    item["bytes"],
                    selected_base,
                )
            )

        completed = 0

        for future in as_completed(futures):
            results.append(future.result())
            completed += 1
            progress.progress(
                completed / total_files,
                text=(
                    f"Processed {completed} "
                    f"of {total_files} files..."
                ),
            )
            status_placeholder.caption(
                f"Batch execution progress: {completed}/{total_files}"
            )

    progress.empty()
    status_placeholder.empty()
    return results


# =========================================================
# UI
# =========================================================
def render_logo(theme_mode):

    logo_base64 = LOGO_VARIANTS.get(
        theme_mode
    ) or LOGO_VARIANTS.get("light")

    if not logo_base64:
        st.markdown(
            '<div class="sidebar-card"><h4>TCS</h4>'
            '<p>Logo asset not found.</p></div>',
            unsafe_allow_html=True,
        )
        return

    st.markdown(
        (
            '<div class="logo-shell">'
            f'<img src="data:image/png;base64,{logo_base64}" '
            'alt="TCS logo" />'
            "</div>"
        ),
        unsafe_allow_html=True,
    )


def render_sidebar(theme_selection, theme_mode):

    with st.sidebar:
        render_logo(theme_mode)

        st.markdown(
            '<div class="sidebar-card"><h4>Platform Control</h4>'
            '<p>Manage theme, processing capacity, and the current desktop session.</p>'
            "</div>",
            unsafe_allow_html=True,
        )

        st.markdown(
            (
                '<div class="sidebar-meta">'
                '<div><strong>Automation Catalog</strong>'
                '<span>Compact enterprise view</span></div>'
                f'<div class="sidebar-badge">{len(PIPELINE_ORDER)} pipelines</div>'
                "</div>"
            ),
            unsafe_allow_html=True,
        )

        selected_theme = st.radio(
            "Theme",
            ["Auto", "Light", "Dark"],
            index=["Auto", "Light", "Dark"].index(
                theme_selection
            ),
            horizontal=True,
            key="theme_selector",
        )

        worker_count = st.slider(
            "Parallel Workers",
            min_value=1,
            max_value=MAX_WORKERS,
            value=3,
            help="Controls how many files are processed in parallel.",
        )

        with st.popover(
            "Supported Pipelines",
            use_container_width=True,
            help="Open the supported pipeline catalog.",
            key="pipeline_popover",
        ):
            st.caption(
                "Available HR and operations automations."
            )

            for base_name in PIPELINE_ORDER:
                st.markdown(
                    (
                        '<div class="pipeline-pill">'
                        '<span class="pipeline-dot"></span>'
                        f'{html.escape(pipeline_label(base_name))}'
                        "</div>"
                    ),
                    unsafe_allow_html=True,
                )

        clear_clicked = st.button(
            "Clear Session",
            use_container_width=True,
            help="Reset uploads, results, and recovery state.",
            key="clear_session_button",
            type="secondary",
        )

    return {
        "theme_selection": selected_theme,
        "mode": "Automatic",
        "worker_count": worker_count,
        "clear_clicked": clear_clicked,
    }


def render_header():

    chip_html = "".join(
        [
            (
                '<span class="hero-chip">'
                "Batch processing"
                "</span>"
            ),
            (
                '<span class="hero-chip">'
                "Excel automation"
                "</span>"
            ),
            (
                '<span class="hero-chip">'
                "Audit-ready downloads"
                "</span>"
            ),
        ]
    )

    st.markdown(
        f"""
        <section class="hero-card">
            <div class="section-caption">TCS Operations Platform</div>
            <h1 class="hero-title">{html.escape(APP_NAME)}</h1>
            <p class="hero-subtitle">{html.escape(APP_SUBTITLE)}</p>
            <div class="hero-chip-row">{chip_html}</div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def render_metric_cards(results):

    success_count = sum(
        1
        for result in results
        if result["Status"] == "Success"
    )
    error_count = len(results) - success_count
    total_rows = sum(
        result["Rows"]
        for result in results
    )
    last_run_at = st.session_state.get(
        "last_run_at",
        "Not available",
    )

    metrics = [
        (
            "Processed Files",
            str(len(results)),
            "Total files handled in the latest batch run.",
        ),
        (
            "Successful Runs",
            str(success_count),
            f"{error_count} file(s) require attention.",
        ),
        (
            "Output Rows",
            f"{total_rows:,}",
            "Rows generated across all successful outputs.",
        ),
        (
            "Last Execution",
            last_run_at,
            "Timestamp of the latest batch execution.",
        ),
    ]

    columns = st.columns(len(metrics))

    for column, metric in zip(columns, metrics):
        label, value, footnote = metric
        column.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">{html.escape(label)}</div>
                <div class="metric-value">{html.escape(safe_text(value))}</div>
                <div class="metric-footnote">{html.escape(safe_text(footnote, ''))}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_empty_state():

    st.markdown(
        """
        <section class="empty-panel">
            <h3>Ready for a new batch</h3>
            <p>
                Upload one or multiple Excel or CSV files to trigger the
                available HR and operations pipelines. The platform will detect
                the correct automation, validate the schema, generate outputs,
                and store execution history automatically.
            </p>
        </section>
        """,
        unsafe_allow_html=True,
    )


def render_upload_section():

    st.markdown(
        """
        <section class="upload-shell">
        <div class="section-caption">Input</div>
        <h2 class="section-title">Batch Upload Workspace</h2>
        <p class="section-copy">
            Upload one or multiple files. Automatic pipeline detection runs by
            default. If a file cannot be identified, a manual recovery option
            becomes available after the run.
        </p>
        <div class="upload-meta-row">
            <span class="upload-meta-pill">Automatic routing</span>
            <span class="upload-meta-pill">Batch-safe processing</span>
            <span class="upload-meta-pill">Desktop-ready exports</span>
        </div>
        </section>
        """,
        unsafe_allow_html=True,
    )

    uploaded_files = st.file_uploader(
        "Upload files",
        type=["xlsx", "csv"],
        accept_multiple_files=True,
        label_visibility="collapsed",
        key=f"uploader_{st.session_state['uploader_key']}",
    )

    file_payloads = []

    if uploaded_files:
        file_payloads = [
            {
                "name": file.name,
                "bytes": file.getvalue(),
                "hash": file_hash(
                    file.getvalue(),
                    file.name,
                ),
            }
            for file in uploaded_files
        ]

        st.markdown(
            f"""
            <div class="status-note">
                {len(file_payloads)} file(s) queued for automatic execution.
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.info(
            "Automatic mode is enabled. The platform will detect the best matching pipeline for each file."
        )

    return uploaded_files, file_payloads


def safe_clear_session():

    preserved_theme = st.session_state.get(
        "theme_selector",
        st.session_state.get("ui_theme", "Auto"),
    )
    next_uploader_key = (
        st.session_state.get("uploader_key", 0) + 1
    )

    st.session_state.clear()
    st.session_state["ui_theme"] = preserved_theme
    st.session_state["theme_selector"] = preserved_theme
    st.session_state["uploader_key"] = next_uploader_key
    st.session_state["last_results"] = []
    st.session_state["last_file_payloads"] = []
    st.session_state["last_run_at"] = "Not available"
    rerun_app()


def render_manual_recovery_section(results, file_payloads):

    payload_by_hash = {
        item["hash"]: item
        for item in file_payloads
    }
    failed_results = [
        result
        for result in results
        if result["Status"] == "Error"
        and result.get("Hash") in payload_by_hash
    ]

    if not failed_results:
        return False, [], {}

    st.markdown(
        """
        <section class="recovery-shell">
        <div class="section-caption">Recovery</div>
        <h3 class="section-title">Manual Pipeline Recovery</h3>
        <p class="section-copy">
            Automatic detection failed or the file needs a manual retry. Assign the correct pipeline only for the affected files.
        </p>
        </section>
        """,
        unsafe_allow_html=True,
    )

    manual_selection = {}
    retry_payloads = []

    for result in failed_results:
        payload = payload_by_hash[result["Hash"]]
        retry_payloads.append(payload)
        st.markdown(
            f"**{html.escape(result['Arquivo'])}**  \n{html.escape(safe_text(result.get('ErrorMessage'), 'Processing error'))}"
        )
        manual_selection[result["Arquivo"]] = st.selectbox(
            f"Pipeline for {result['Arquivo']}",
            options=PIPELINE_ORDER,
            index=0,
            format_func=pipeline_label,
            key=f"retry_manual_{result['Hash']}",
        )

    retry_clicked = st.button(
        "Retry Failed Files with Manual Assignment",
        use_container_width=True,
        key="retry_failed_files_button",
    )

    return retry_clicked, retry_payloads, manual_selection


def merge_results(existing_results, retried_results):

    retried_by_hash = {
        result["Hash"]: result
        for result in retried_results
    }
    merged = []

    for result in existing_results:
        merged.append(
            retried_by_hash.get(
                result.get("Hash"),
                result,
            )
        )

    return merged


def build_status_dataframe(results):

    return pd.DataFrame(
        [
            {
                "File": result["Arquivo"],
                "Pipeline": result.get(
                    "DisplayBase",
                    pipeline_label(result["Base"]),
                ),
                "Status": result["Status"],
                "Rows": result["Rows"],
                "Details": result.get(
                    "ErrorMessage",
                    "",
                ),
            }
            for result in results
        ]
    )


def render_overview_tab(results):

    st.markdown(
        """
        <div class="section-caption">Overview</div>
        <h3 class="section-title">Execution Status</h3>
        <p class="section-copy">
            Review the latest batch, identify failures quickly, and confirm row counts before sharing outputs.
        </p>
        """,
        unsafe_allow_html=True,
    )

    status_df = build_status_dataframe(results)

    st.dataframe(
        status_df,
        use_container_width=True,
        hide_index=True,
    )


def render_preview_tab(results):

    st.markdown(
        """
        <div class="section-caption">Preview</div>
        <h3 class="section-title">Processed Data Samples</h3>
        <p class="section-copy">
            Inspect the first rows of each successful output before downloading the final files.
        </p>
        """,
        unsafe_allow_html=True,
    )

    preview_results = [
        result
        for result in results
        if result["DataFrame"] is not None
    ]

    if not preview_results:
        st.warning(
            "No previews are available because all files failed during processing."
        )
        return

    for result in preview_results:
        with st.expander(
            f"{result['DisplayBase']} | {result['Arquivo']}",
            expanded=False,
        ):
            st.dataframe(
                result["DataFrame"].head(
                    PREVIEW_ROWS
                ),
                use_container_width=True,
                hide_index=True,
            )


def render_downloads_tab(results):

    st.markdown(
        """
        <div class="section-caption">Downloads</div>
        <h3 class="section-title">Export Center</h3>
        <p class="section-copy">
            Download all successful outputs in a single ZIP file or pick individual files when needed.
        </p>
        """,
        unsafe_allow_html=True,
    )

    successful_results = [
        result
        for result in results
        if result["Status"] == "Success"
    ]

    if not successful_results:
        st.warning(
            "No successful outputs are available for download."
        )
        return

    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(
        zip_buffer,
        "w",
    ) as zip_file:
        for result in successful_results:
            zip_file.writestr(
                result["Output"],
                result["Bytes"],
            )

    zip_buffer.seek(0)

    st.download_button(
        "Download Full ZIP Package",
        zip_buffer,
        file_name=(
            f"processed_{datetime.today().strftime('%Y-%m-%d')}.zip"
        ),
        use_container_width=True,
    )

    download_columns = st.columns(2)

    for index, result in enumerate(successful_results):
        target_column = download_columns[
            index % 2
        ]
        target_column.download_button(
            f"Download {result['DisplayBase']}",
            data=result["Bytes"],
            file_name=result["Output"],
            key=result["Output"],
            use_container_width=True,
        )


def render_logs_tab(results):

    st.markdown(
        """
        <div class="section-caption">Logs</div>
        <h3 class="section-title">Batch Log Stream</h3>
        <p class="section-copy">
            Review the execution summary for every file processed in the latest batch.
        </p>
        """,
        unsafe_allow_html=True,
    )

    logs = [
        result["Log"]
        for result in results
    ]

    st.code(
        "\n".join(logs),
        language="text",
    )


def render_history_tab():

    st.markdown(
        """
        <div class="section-caption">History</div>
        <h3 class="section-title">Execution Archive</h3>
        <p class="section-copy">
            Outputs are stored automatically in the history directory for future traceability and operational reviews.
        </p>
        """,
        unsafe_allow_html=True,
    )

    history_rows = list_recent_history()

    st.markdown(
        f"""
        <span class="path-chip">Outputs: {html.escape(format_output_path(OUTPUT_ROOT))}</span>
        <span class="path-chip">History: {html.escape(format_output_path(HISTORY_ROOT))}</span>
        <span class="path-chip">App Home: {html.escape(format_output_path(APP_HOME))}</span>
        """,
        unsafe_allow_html=True,
    )

    if not history_rows:
        st.info(
            "No historical outputs were found yet."
        )
        return

    st.dataframe(
        pd.DataFrame(history_rows),
        use_container_width=True,
        hide_index=True,
    )


# =========================================================
# SESSION STATE
# =========================================================
if "uploader_key" not in st.session_state:
    st.session_state["uploader_key"] = 0

if "last_results" not in st.session_state:
    st.session_state["last_results"] = []

if "last_file_payloads" not in st.session_state:
    st.session_state["last_file_payloads"] = []

if "ui_theme" not in st.session_state:
    st.session_state["ui_theme"] = "Auto"

if "last_run_at" not in st.session_state:
    st.session_state["last_run_at"] = "Not available"


# =========================================================
# SIDEBAR + THEME
# =========================================================
theme_mode = get_effective_theme(
    get_requested_theme()
)
inject_global_styles(theme_mode)

sidebar_state = render_sidebar(
    get_requested_theme(),
    theme_mode,
)

st.session_state["ui_theme"] = sidebar_state[
    "theme_selection"
]

if sidebar_state["clear_clicked"]:
    safe_clear_session()


# =========================================================
# PAGE BODY
# =========================================================
render_header()

results = st.session_state.get(
    "last_results",
    [],
)

render_metric_cards(results)

st.markdown("")

uploaded_files, file_payloads = render_upload_section()

action_columns = st.columns([1.7, 0.95, 0.95], gap="small")

with action_columns[0]:
    run_clicked = st.button(
        "Process Files",
        use_container_width=True,
        disabled=not uploaded_files,
        key="process_button",
    )

with action_columns[1]:
    st.markdown(
        f"""
        <div class="action-shell">
            <div class="status-note">
                Mode: Automatic<br>
                Failed files unlock manual recovery
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with action_columns[2]:
    st.markdown(
        f"""
        <div class="action-shell">
            <div class="status-note">
                Workers: {sidebar_state["worker_count"]}<br>
                Theme: {html.escape(st.session_state["ui_theme"])}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

if run_clicked:
    st.session_state["last_file_payloads"] = file_payloads
    st.session_state["last_results"] = process_uploaded_files(
        file_payloads=file_payloads,
        worker_count=sidebar_state["worker_count"],
    )
    st.session_state["last_run_at"] = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )
    rerun_app()

results = st.session_state.get(
    "last_results",
    [],
)

retry_clicked, retry_payloads, retry_manual_selection = render_manual_recovery_section(
    results,
    st.session_state.get("last_file_payloads", []),
)

if retry_clicked:
    retried_results = process_uploaded_files(
        file_payloads=retry_payloads,
        worker_count=sidebar_state["worker_count"],
        manual_selection=retry_manual_selection,
    )
    st.session_state["last_results"] = merge_results(
        results,
        retried_results,
    )
    st.session_state["last_run_at"] = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )
    rerun_app()

if not results:
    render_empty_state()
else:
    tab_overview, tab_preview, tab_downloads, tab_logs, tab_history = st.tabs(
        [
            "Overview",
            "Preview",
            "Downloads",
            "Logs",
            "History",
        ]
    )

    with tab_overview:
        render_overview_tab(results)

    with tab_preview:
        render_preview_tab(results)

    with tab_downloads:
        render_downloads_tab(results)

    with tab_logs:
        render_logs_tab(results)

    with tab_history:
        render_history_tab()
