import html

import streamlit as st

from runtime.app.config import LOGO_VARIANTS, MAX_WORKERS, PIPELINE_ORDER
from runtime.app.services import file_hash, pipeline_label


def render_logo(theme_mode):

    logo_base64 = LOGO_VARIANTS.get(
        theme_mode
    ) or LOGO_VARIANTS.get("light")

    if not logo_base64:
        return

    st.markdown(
        (
            '<div class="sidebar-logo-shell">'
            f'<img src="data:image/png;base64,{logo_base64}" alt="TCS logo" />'
            "</div>"
        ),
        unsafe_allow_html=True,
    )


def render_sidebar(theme_selection, theme_mode, display_names):

    with st.sidebar:
        render_logo(theme_mode)
        st.caption("Workspace")
        st.markdown(
            '<div class="sidebar-note">Compact controls for theme, execution capacity and session reset.</div>',
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

        st.markdown(
            f'<div class="sidebar-meta">Available pipelines: <strong>{len(display_names)}</strong></div>',
            unsafe_allow_html=True,
        )

        with st.popover(
            "Supported Pipelines",
            use_container_width=True,
            key="pipeline_popover",
        ):
            for base_name in PIPELINE_ORDER:
                st.markdown(
                    (
                        '<div class="status-chip">'
                        f'{html.escape(pipeline_label(base_name, display_names))}'
                        "</div>"
                    ),
                    unsafe_allow_html=True,
                )

        clear_clicked = st.button(
            "Clear Session",
            use_container_width=True,
            key="clear_session_button",
            type="secondary",
        )

    return {
        "theme_selection": selected_theme,
        "worker_count": worker_count,
        "clear_clicked": clear_clicked,
    }


def render_header(app_name, display_names):

    st.markdown(
        f"""
        <section class="app-header-compact">
            <div class="header-inline">
                <div>
                    <div class="header-kicker">Internal Operations Workspace</div>
                    <h1 class="header-title">{html.escape(app_name)}</h1>
                    <p class="header-copy">
                        Centralize uploads, execute the right automation and review deliverables in one operational workspace.
                    </p>
                </div>
                <div class="header-flow-line">1 Upload <span>&rarr;</span> 2 Process <span>&rarr;</span> 3 Review <span>&rarr;</span> 4 Download</div>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def render_upload_section():

    st.markdown(
        """
        <div class="section-caption">Input</div>
        <h2 class="section-title">Batch Upload</h2>
        <p class="section-copy">Select one or more source files and run the batch when the selection is ready.</p>
        <div class="upload-guidance">Accepted formats: <strong>.xlsx</strong> and <strong>.csv</strong></div>
        """,
        unsafe_allow_html=True,
    )

    upload_col, action_col = st.columns([4.5, 1.05], vertical_alignment="bottom")

    with upload_col:
        uploaded_files = st.file_uploader(
            "Upload files",
            type=["xlsx", "csv"],
            accept_multiple_files=True,
            label_visibility="collapsed",
            key=f"uploader_{st.session_state['uploader_key']}",
        )

    file_payloads = []

    if uploaded_files:
        for file in uploaded_files:
            file_bytes = file.getvalue()
            file_payloads.append(
                {
                    "name": file.name,
                    "bytes": file_bytes,
                    "hash": file_hash(
                        file_bytes,
                        file.name,
                    ),
                }
            )

    with action_col:
        run_clicked = st.button(
            "Process Files",
            type="primary",
            disabled=not uploaded_files,
            key="process_button",
        )

    return uploaded_files, file_payloads, run_clicked


def render_manual_recovery_section(results, file_payloads, display_names):
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
        <section class="section-card-compact">
            <div class="section-caption">Recovery</div>
            <h3 class="section-title">Manual Pipeline Recovery</h3>
            <p class="section-copy">Assign a pipeline only for failed files and rerun those items without affecting successful outputs.</p>
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
            f"**{html.escape(result['Arquivo'])}**  \n{html.escape(result.get('ErrorMessage', 'Processing error'))}"
        )
        manual_selection[result["Arquivo"]] = st.selectbox(
            f"Pipeline for {result['Arquivo']}",
            options=PIPELINE_ORDER,
            index=0,
            format_func=lambda item: pipeline_label(item, display_names),
            key=f"retry_manual_{result['Hash']}",
        )

    retry_clicked = st.button(
        "Retry Failed Files",
        use_container_width=True,
        key="retry_failed_files_button",
    )

    return retry_clicked, retry_payloads, manual_selection
