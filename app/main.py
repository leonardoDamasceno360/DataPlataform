import sys
import os
from datetime import datetime
import io
import zipfile
import hashlib
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
import pandas as pd

from core.loader import load_file
from core.engine import AutomationEngine
from core.detector import detect_automation
from automations import AUTOMATIONS


# =========================================================
# MELHORIA: LOGGING ESTRUTURADO
# =========================================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)
logger = logging.getLogger("data_platform")


# =========================================================
# CONFIG
# =========================================================
st.set_page_config(page_title="Data Platform", layout="wide")

st.markdown("""
<style>
div[data-testid="stFileUploader"] {
    border: 2px dashed #4A90E2;
    border-radius: 12px;
    padding: 30px;
    background-color: #f9fbfd;
}
</style>
""", unsafe_allow_html=True)

st.title("Plataforma de Tratamento de Dados")

mode = st.radio(
    "Modo de execução:",
    ["Manual", "Automático"],
    horizontal=True
)

# =========================================================
# MELHORIA: PREVIEW VS FULL
# =========================================================
fast_mode = st.toggle("Modo rápido (preview)")

uploaded_files = st.file_uploader(
    "Upload dos arquivos",
    type=["xlsx", "csv"],
    accept_multiple_files=True
)

# =========================================================
# MELHORIA: PROGRESS + LOGS
# =========================================================
progress_bar = st.progress(0)
logs = []

# =========================================================
# MELHORIA: HISTÓRICO
# =========================================================
history_dir = Path("history") / datetime.today().strftime("%Y-%m-%d")
history_dir.mkdir(parents=True, exist_ok=True)


# =========================================================
# MELHORIA: HASH (BASE CACHE)
# =========================================================
def file_hash(file):
    return hashlib.md5(file.getvalue()).hexdigest()


# =========================================================
# MELHORIA: CACHE
# =========================================================
@st.cache_data(show_spinner=False)
def cached_process(file_bytes, file_name, fast_mode_flag):
    file_like = io.BytesIO(file_bytes)
    file_like.name = file_name

    df = load_file(file_like)

    detected = detect_automation(df, file_name)
    if not detected:
        raise ValueError("Base não identificada")

    if fast_mode_flag:
        df = df.head(500)

    engine = AutomationEngine(AUTOMATIONS[detected])
    result = engine.run(df)

    return detected, result


# =========================================================
# MELHORIA: SCHEMA VALIDATION
# =========================================================
SCHEMA_RULES = {
    "Periódicos": ["ID"],
    "Speed": ["Employee Number"],
    "Gems": ["Nomeador"],
    "Xcelerate": ["ID"],
    "IBelong": ["New Joinee emp id"]
}

def validate_schema(df, base):
    required = SCHEMA_RULES.get(base, [])
    missing = [c for c in required if c not in df.columns]
    return missing


# =========================================================
# PROCESSAMENTO (PARALELO)
# =========================================================
results = []
downloads = {}

def process_file(file):

    name = file.name

    try:
        logger.info(f"Iniciando: {name}")

        if mode == "Automático":

            base_label, result_df = cached_process(
                file.getvalue(),
                file.name,
                fast_mode
            )

        else:
            df = load_file(file)
            base_label = st.selectbox(
                f"Escolha automação para {file.name}",
                list(AUTOMATIONS.keys()),
                key=file.name
            )

            engine = AutomationEngine(AUTOMATIONS[base_label])
            result_df = engine.run(df)

        # =====================
        # VALIDAÇÃO
        # =====================
        missing = validate_schema(result_df, base_label)
        if missing:
            raise ValueError(f"Colunas faltantes: {missing}")

        rows = len(result_df)

        # =====================
        # SALVAR HISTÓRICO
        # =====================
        filename = f"{base_label}_{datetime.now().strftime('%H%M%S')}.xlsx"
        output_path = history_dir / filename
        result_df.to_excel(output_path, index=False)

        # =====================
        # BUFFER DOWNLOAD
        # =====================
        buffer = io.BytesIO()
        result_df.to_excel(buffer, index=False)
        buffer.seek(0)

        downloads[filename] = buffer

        logs.append(f"{base_label} | {rows} linhas | OK")

        logger.info(f"Sucesso: {name}")

        return {
            "Base": base_label,
            "Arquivo": name,
            "Status": "OK",
            "Rows": rows,
            "DataFrame": result_df,
            "Output": filename
        }

    except Exception as e:

        logs.append(f"{name} | ERRO: {str(e)}")
        logger.error(f"Erro em {name}: {str(e)}")

        return {
            "Base": name,
            "Arquivo": name,
            "Status": f"Erro: {str(e)}",
            "Rows": 0,
            "DataFrame": None,
            "Output": None
        }


# =========================================================
# EXECUÇÃO
# =========================================================
if uploaded_files:

    futures = []

    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(process_file, f) for f in uploaded_files]

        for i, future in enumerate(as_completed(futures)):
            results.append(future.result())
            progress_bar.progress((i + 1) / len(uploaded_files))


# =========================================================
# UI RESULTADOS
# =========================================================
if results:

    st.subheader("Status")

    status_df = pd.DataFrame(results)[["Arquivo", "Base", "Status", "Rows"]]
    st.dataframe(status_df, use_container_width=True)

    st.subheader("Pré-visualização")

    for r in results:

        if r["DataFrame"] is not None:

            with st.expander(f"{r['Base']} ({r['Arquivo']})"):

                st.write(f"Linhas: {r['Rows']}")

                # =====================
                # PREVIEW LIMITADO
                # =====================
                st.dataframe(
                    r["DataFrame"].head(100),
                    use_container_width=True
                )

                st.download_button(
                    f"Download {r['Base']}",
                    downloads[r["Output"]],
                    file_name=r["Output"]
                )

    # =====================================================
    # ZIP DOWNLOAD
    # =====================================================
    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, "w") as zf:
        for name, file_data in downloads.items():
            zf.writestr(name, file_data.getvalue())

    zip_buffer.seek(0)

    st.download_button(
        "Download ZIP",
        zip_buffer,
        file_name=f"processed_{datetime.today().strftime('%Y-%m-%d')}.zip"
    )

    # =====================================================
    # LOGS
    # =====================================================
    st.subheader("Logs")
    st.text("\n".join(logs))