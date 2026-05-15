# =========================================================
# IMPORTS
# =========================================================
import hashlib
import io
import logging
import os
import re
import sys
import unicodedata
import zipfile

from concurrent.futures import (
    ThreadPoolExecutor,
    as_completed
)

from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st

from PIL import Image


# =========================================================
# PATH
# =========================================================
sys.path.append(
    os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            ".."
        )
    )
)


# =========================================================
# IMPORTS INTERNOS
# =========================================================
from automations import AUTOMATIONS

from core.detector import detect_automation

from core.engine import AutomationEngine

from core.loader import load_file

from core.schema_utils import (
    normalize_text,
    find_column
)
# =========================================================
# CONFIG
# =========================================================
st.set_page_config(
    page_title="Data Processing Platform",
    page_icon="📊",
    layout="wide"
)


# =========================================================
# LOGO
# =========================================================
logo = Image.open(
    "assets/tcs_logo.png"
)


# =========================================================
# LOGGING
# =========================================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(
    "data_platform"
)


# =========================================================
# PATHS
# =========================================================
BASE_DIR = Path(__file__).resolve().parent.parent

OUTPUT_ROOT = BASE_DIR / "outputs"

HISTORY_ROOT = BASE_DIR / "history"

OUTPUT_ROOT.mkdir(
    parents=True,
    exist_ok=True
)

HISTORY_ROOT.mkdir(
    parents=True,
    exist_ok=True
)


# =========================================================
# CONSTANTS
# =========================================================
MAX_WORKERS = 4

PREVIEW_ROWS = 100

FULL_PREVIEW_ROWS = 500


# =========================================================
# SCHEMA RULES
# =========================================================
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
        "Status"
    ],

    "Periódicos": [
        "ID",
        "DATE EXPIRATION ASO",
        "STATUS ASO"
    ],

    "OT": [
        "Type of Day",
        "Total OT Hours Done",
        "Last OT Request Status"
    ],

    "Rest Period": [
        "Id Contratado",
        "Data do Dia (Data/Hora)",
        "Interjornada Praticada"
    ],

    "Quadro Geral": [
        "Segment HEAD",
        "Horizontal Line",
        "Sindicato",
        "Situação"
    ],

    "Documentos": [
        "Status da Assinatura Digital do Documento"
    ],

    "Separation Forms": [
        "Separation type"
    ],

    "Ult Mov Sal": [
        "ID",
        "EFECTIVE DATE"
    ],

    "Desligados Geral": [
        "Id Contratado",
        "SEPARATION REASON",
        "CATEGORY"
    ]
}

# =========================================================
# HELPERS
# =========================================================
def normalized_columns(df):

    return {
        normalize_text(col): col
        for col in df.columns.astype(str)
    }


def file_hash(file_bytes, file_name):

    return hashlib.md5(
        file_name.encode("utf-8") + file_bytes
    ).hexdigest()


def build_file_object(file_bytes, file_name):

    file_like = io.BytesIO(file_bytes)

    file_like.name = file_name

    return file_like
# =========================================================
# FLEXIBLE COLUMN FINDER
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


def normalized_columns(df):

    return {
        normalize_text(col): col
        for col in df.columns.astype(str)
    }


def file_hash(file_bytes, file_name):

    return hashlib.md5(
        file_name.encode("utf-8") + file_bytes
    ).hexdigest()


def build_file_object(file_bytes, file_name):

    file_like = io.BytesIO(file_bytes)

    file_like.name = file_name

    return file_like


# =========================================================
# VALIDATION
# =========================================================
def validate_input_schema(
    df,
    base_label
):

    cols = normalized_columns(df)

    expected = SCHEMA_RULES.get(
        base_label,
        []
    )

    missing = [

        col

        for col in expected

        if normalize_text(col) not in cols
    ]

    return missing


# =========================================================
# OUTPUT NAME
# =========================================================
def build_output_name(base_label):

    current_date = datetime.now().strftime(
        "%d%m%y"
    )

    return (
        f"{base_label}_{current_date}.xlsx"
    )


# =========================================================
# SAVE HISTORY
# =========================================================
def save_history(
    file_name,
    buffer
):

    history_dir = (
        HISTORY_ROOT
        /
        datetime.today().strftime(
            "%Y-%m-%d"
        )
    )

    history_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    output_path = history_dir / file_name

    output_path.write_bytes(
        buffer.getvalue()
    )

    return output_path


# =========================================================
# CACHE
# =========================================================
@st.cache_data(show_spinner=False)
def cached_detect(
    file_hash_key,
    file_bytes,
    file_name
):

    df = load_file(
        build_file_object(
            file_bytes,
            file_name
        )
    )

    return detect_automation(
        df,
        file_name
    )


@st.cache_data(show_spinner=False)
def cached_process(
    file_hash_key,
    df,
    base_label
):

    engine = AutomationEngine(
        AUTOMATIONS[base_label]
    )

    return engine.run(df)


# =========================================================
# PROCESS FILE
# =========================================================
def process_file(
    file_name,
    file_bytes,
    preview_mode=False,
    selected_base=None
):

    try:

        logger.info(
            "Iniciando processamento: %s",
            file_name
        )

        hash_key = file_hash(
            file_bytes,
            file_name
        )

        detected_base = (
            selected_base
            or
            cached_detect(
                hash_key,
                file_bytes,
                file_name
            )
        )

        if not detected_base:

            raise ValueError(
                "Não foi possível identificar automaticamente a base."
            )

        input_df = load_file(
            build_file_object(
                file_bytes,
                file_name
            )
        )

        if detected_base != "IBelong":

            missing = validate_input_schema(
                input_df,
                detected_base
            )

            if missing:

                raise ValueError(
                    f"Schema inválido para "
                    f"{detected_base}: "
                    f"faltando {', '.join(missing)}"
                )

        result_df = cached_process(
            hash_key,
            input_df,
            detected_base
        )

        rows = len(result_df)

        buffer = io.BytesIO()

        with pd.ExcelWriter(
            buffer,
            engine="openpyxl"
        ) as writer:

            result_df.to_excel(
                writer,
                sheet_name=detected_base[:31],
                index=False
            )

        buffer.seek(0)

        output_name = build_output_name(
            detected_base
        )

        save_history(
            output_name,
            buffer
        )

        return {

            "Base": detected_base,

            "Arquivo": file_name,

            "Status": "OK",

            "Rows": rows,

            "DataFrame": result_df,

            "Output": output_name,

            "Bytes": buffer.getvalue(),

            "Log": (
                f"{detected_base} | "
                f"{rows} linhas | OK"
            )
        }

    except Exception as exc:

        logger.exception(
            "Erro em %s",
            file_name
        )

        return {

            "Base": (
                selected_base
                or
                "Não identificado"
            ),

            "Arquivo": file_name,

            "Status": "Erro",

            "Rows": 0,

            "DataFrame": None,

            "Output": None,

            "Bytes": None,

            "ErrorMessage": str(exc),

            "Log": (
                f"{file_name} | "
                f"ERRO: {exc}"
            )
        }


# =========================================================
# STYLE
# =========================================================
st.markdown(
    """
    <style>

    .stApp {
        background-color: #F5F7FA;
    }

    .main .block-container {
        max-width: 1400px;
        padding-top: 2rem;
    }

    section[data-testid="stSidebar"] {
        background-color: #FFFFFF;
        border-right: 1px solid #E5E7EB;
    }

    h1, h2, h3 {
        color: #111827 !important;
    }

    div[data-testid="stFileUploader"] {
        border: 2px dashed #C7D2FE;
        border-radius: 14px;
        background-color: #FFFFFF;
        padding: 1rem;
    }

    div.stButton > button {
        background-color: #2563EB;
        color: white;
        border-radius: 10px;
        border: none;
        height: 48px;
        font-weight: 600;
    }

    div.stButton > button:hover {
        background-color: #1D4ED8;
    }

    .stDownloadButton button {
        background-color: #2563EB;
        color: white;
        border-radius: 10px;
        border: none;
    }

    .metric-box {
        background-color: white;
        border: 1px solid #E5E7EB;
        border-radius: 14px;
        padding: 20px;
    }

    </style>
    """,
    unsafe_allow_html=True
)

# =========================================================
# HEADER
# =========================================================

st.markdown(
    """
    <h1 style="
        margin-bottom:0;
        margin-top:15px;
        font-size:42px;
        font-weight:700;
        color:#111827;
    ">
        Data Processing Platform
    </h1>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <p style="
        color:#6B7280;
        margin-top:-5px;
        font-size:16px;
    ">
        Enterprise automation platform for HR datasets,
        compliance workflows and operational processing.
    </p>
    """,
    unsafe_allow_html=True
)
# =========================================================
# SIDEBAR
# =========================================================
with st.sidebar:

    st.image(
        logo,
        width=180
    )

    st.markdown("---")

    st.markdown("## Execution")

    mode = st.radio(
        "Mode",
        ["Manual", "Automático"],
        horizontal=True
    )

    preview_mode = st.toggle(
        "Quick Preview",
        value=True
    )

    worker_count = st.slider(
        "Parallel Processing",
        min_value=1,
        max_value=MAX_WORKERS,
        value=3
    )

    st.markdown("---")

    st.markdown("## Supported Pipelines")

    supported_bases = [

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
        "Ult Mov Sal"
    ]

    for base in supported_bases:

        st.markdown(
            f"""
            <div style="
                background:white;
                border:1px solid #E5E7EB;
                border-radius:10px;
                padding:10px;
                margin-bottom:8px;
            ">
                {base}
            </div>
            """,
            unsafe_allow_html=True
        )

# =========================================================
# CLEAR SESSION
# =========================================================

if "uploader_key" not in st.session_state:

    st.session_state["uploader_key"] = 0


col_clear1, col_clear2 = st.columns([6, 1])

with col_clear2:

    if st.button(
        "Limpar",
        use_container_width=True
    ):

        st.session_state["uploader_key"] += 1

        st.session_state["last_results"] = []

        st.rerun()

# =========================================================
# UPLOAD
# =========================================================
st.markdown("## Upload Files")

uploaded_files = st.file_uploader(
    "Upload",
    type=["xlsx", "csv"],
    accept_multiple_files=True,
    label_visibility="collapsed",
    key=f"uploader_{st.session_state['uploader_key']}"
)

manual_selection = {}

file_payloads = []

if uploaded_files:

    file_payloads = [

        {
            "name": file.name,

            "bytes": file.getvalue(),

            "hash": file_hash(
                file.getvalue(),
                file.name
            )
        }

        for file in uploaded_files
    ]

    if mode == "Manual":

        for item in file_payloads:

            manual_selection[
                item["name"]
            ] = st.selectbox(
                f"Automation for {item['name']}",
                list(AUTOMATIONS.keys()),
                key=f"manual_{item['hash']}"
            )

    else:

        st.info(
            "Automatic mode enabled."
        )

run_clicked = st.button(
    "Process Files",
    use_container_width=True,
    disabled=not uploaded_files,
    key="process_button"
)

# =========================================================
# RESULTS
# =========================================================
results = st.session_state.get(
    "last_results",
    []
)

if results:

    success_count = sum(
        1
        for r in results
        if r["Status"] == "OK"
    )

    error_count = (
        len(results)
        - success_count
    )

    total_rows = sum(
        r["Rows"]
        for r in results
    )

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric(
            "Arquivos",
            len(results)
        )

    with c2:
        st.metric(
            "Sucesso",
            success_count
        )

    with c3:
        st.metric(
            "Linhas",
            total_rows
        )

    st.subheader("Status")

    status_df = pd.DataFrame([

        {
            "Arquivo": r["Arquivo"],
            "Base": r["Base"],
            "Status": r["Status"],
            "Linhas": r["Rows"],
            "Detalhe": r.get(
                "ErrorMessage",
                ""
            )
        }

        for r in results
    ])

    st.dataframe(
        status_df,
        use_container_width=True,
        hide_index=True
    )

    st.subheader("Pré-visualização")

    for result in results:

        if result["DataFrame"] is None:
            continue

        with st.expander(
            f"{result['Base']} | "
            f"{result['Arquivo']}"
        ):

            st.dataframe(
                result["DataFrame"].head(
                    PREVIEW_ROWS
                ),
                use_container_width=True,
                hide_index=True
            )

    st.subheader("Downloads")

    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(
        zip_buffer,
        "w"
    ) as zip_file:

        for result in results:

            if result["Status"] == "OK":

                zip_file.writestr(
                    result["Output"],
                    result["Bytes"]
                )

    zip_buffer.seek(0)

    st.download_button(
        "Baixar ZIP completo",
        zip_buffer,
        file_name=(
            f"processed_"
            f"{datetime.today().strftime('%Y-%m-%d')}.zip"
        ),
        use_container_width=True
    )

    for result in results:

        if result["Status"] != "OK":
            continue

        st.download_button(
            f"Baixar {result['Base']}",
            data=result["Bytes"],
            file_name=result["Output"],
            key=result["Output"],
            use_container_width=True
        )

    st.subheader("Logs")

    logs = [
        result["Log"]
        for result in results
    ]

    st.code(
        "\n".join(logs),
        language="text"
    )