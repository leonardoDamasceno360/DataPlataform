import logging
import sys
from datetime import datetime
from pathlib import Path

import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from runtime.app.config import APP_NAME, PIPELINE_DISPLAY_NAMES
from runtime.app.core.execution_manager import (
    build_session_file_payloads,
    merge_results,
    process_uploaded_files,
    validate_uploaded_files,
)
from runtime.app.core.session_manager import (
    initialize_session_state,
    safe_clear_session,
)
from runtime.app.ui_components import (
    render_header,
    render_manual_recovery_section,
    render_sidebar,
    render_upload_section,
)
from runtime.app.ui_layout import (
    render_downloads_tab,
    render_empty_state,
    render_history_tab,
    render_logs_tab,
    render_overview_tab,
    render_preview_tab,
)
from runtime.app.ui_styles import (
    get_effective_theme,
    get_requested_theme,
    inject_global_styles,
)


st.set_page_config(
    page_title=APP_NAME,
    page_icon=":bar_chart:",
    layout="wide",
    initial_sidebar_state="expanded",
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger("data_platform_main")


def rerun_app():

    if hasattr(st, "rerun"):
        st.rerun()
        return

    st.experimental_rerun()


def run_app():

    initialize_session_state()

    theme_mode = get_effective_theme(
        get_requested_theme()
    )
    inject_global_styles(theme_mode)

    sidebar_state = render_sidebar(
        get_requested_theme(),
        theme_mode,
        PIPELINE_DISPLAY_NAMES,
    )

    st.session_state["ui_theme"] = sidebar_state[
        "theme_selection"
    ]

    if sidebar_state["clear_clicked"]:
        safe_clear_session(rerun_app)

    render_header(
        APP_NAME,
        PIPELINE_DISPLAY_NAMES,
    )

    results = st.session_state.get(
        "last_results",
        [],
    )
    validations = st.session_state.get(
        "validation_rows",
        [],
    )

    uploaded_files, file_payloads, run_clicked = render_upload_section()
    current_hashes = [
        item["hash"]
        for item in file_payloads
    ]
    stored_hashes = [
        item["hash"]
        for item in st.session_state.get(
            "last_file_payloads",
            [],
        )
    ]

    if current_hashes != stored_hashes:
        st.session_state["validation_rows"] = []
        st.session_state["execution_logs"] = []
        st.session_state["output_manifest"] = []
        if file_payloads:
            st.session_state["last_results"] = []

    validations = st.session_state.get(
        "validation_rows",
        [],
    )

    if run_clicked:
        logger.info(
            "Run triggered with %s file(s)",
            len(file_payloads),
        )
        st.session_state["last_file_payloads"] = build_session_file_payloads(
            file_payloads
        )
        if not validations:
            st.session_state["validation_rows"] = validate_uploaded_files(
                file_payloads,
                PIPELINE_DISPLAY_NAMES,
            )
        run_started = datetime.now()
        st.session_state["last_results"] = process_uploaded_files(
            file_payloads=file_payloads,
            worker_count=sidebar_state["worker_count"],
            display_names=PIPELINE_DISPLAY_NAMES,
        )
        run_finished = datetime.now()
        st.session_state["last_run_at"] = run_finished.strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        st.session_state["last_run_seconds"] = (
            run_finished - run_started
        ).total_seconds()

    results = st.session_state.get(
        "last_results",
        [],
    )

    retry_clicked, retry_payloads, retry_manual_selection = render_manual_recovery_section(
        results,
        st.session_state.get("last_file_payloads", []),
        PIPELINE_DISPLAY_NAMES,
    )

    if retry_clicked:
        logger.info(
            "Manual retry triggered for %s file(s)",
            len(retry_payloads),
        )
        retry_started = datetime.now()
        retried_results = process_uploaded_files(
            file_payloads=retry_payloads,
            worker_count=sidebar_state["worker_count"],
            display_names=PIPELINE_DISPLAY_NAMES,
            manual_selection=retry_manual_selection,
        )
        st.session_state["last_results"] = merge_results(
            results,
            retried_results,
        )
        retry_finished = datetime.now()
        st.session_state["last_run_at"] = retry_finished.strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        st.session_state["last_run_seconds"] = (
            retry_finished - retry_started
        ).total_seconds()

    results = st.session_state.get(
        "last_results",
        [],
    )

    if not results and not file_payloads:
        render_empty_state()
    elif results:
        active_view = st.radio(
            "Workspace section",
            [
                "Overview",
                "Preview",
                "Downloads",
                "Logs",
                "History",
            ],
            horizontal=True,
            label_visibility="collapsed",
            key="workspace_section",
        )

        if active_view == "Overview":
            render_overview_tab(
                results,
                PIPELINE_DISPLAY_NAMES,
            )

        elif active_view == "Preview":
            render_preview_tab(results)

        elif active_view == "Downloads":
            render_downloads_tab(results)

        elif active_view == "Logs":
            render_logs_tab(results)

        else:
            render_history_tab()


try:
    run_app()
except Exception as exc:
    logger.exception("Unhandled app failure")
    st.error(
        "The app hit an unexpected error during this interaction."
    )
    st.exception(exc)
