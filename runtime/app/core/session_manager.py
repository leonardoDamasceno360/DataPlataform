import streamlit as st


DEFAULT_THEME = "Auto"
DEFAULT_LAST_RUN = "Not available"


def initialize_session_state():

    defaults = {
        "uploader_key": 0,
        "last_results": [],
        "last_file_payloads": [],
        "validation_rows": [],
        "execution_logs": [],
        "ui_theme": DEFAULT_THEME,
        "last_run_at": DEFAULT_LAST_RUN,
        "last_run_seconds": 0.0,
        "output_manifest": [],
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def safe_clear_session(rerun_app):

    preserved_theme = st.session_state.get(
        "theme_selector",
        st.session_state.get("ui_theme", DEFAULT_THEME),
    )
    next_uploader_key = st.session_state.get(
        "uploader_key",
        0,
    ) + 1

    st.session_state.clear()
    st.session_state["ui_theme"] = preserved_theme
    st.session_state["theme_selector"] = preserved_theme
    st.session_state["uploader_key"] = next_uploader_key
    st.session_state["last_results"] = []
    st.session_state["last_file_payloads"] = []
    st.session_state["validation_rows"] = []
    st.session_state["execution_logs"] = []
    st.session_state["output_manifest"] = []
    st.session_state["last_run_seconds"] = 0.0
    st.session_state["last_run_at"] = DEFAULT_LAST_RUN
    rerun_app()
