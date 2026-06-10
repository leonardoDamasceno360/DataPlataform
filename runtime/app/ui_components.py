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
        st.caption("Workspace Controls")
        st.markdown(
            '<div class="sidebar-note">Theme and execution controls stay here so the main canvas remains operational.</div>',
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

    chip_html = "".join(
        [
            '<span class="status-chip">Automatic routing</span>',
            '<span class="status-chip">Validated outputs</span>',
            '<span class="status-chip">Desktop-ready exports</span>',
        ]
    )

    st.markdown(
        f"""
        <section class="app-header-compact">
            <div class="header-grid">
                <div>
                    <div class="header-kicker">TCS Operations Platform</div>
                    <h1 class="header-title">{html.escape(app_name)}</h1>
                    <p class="header-copy">
                        Upload, process and export RH or operations files in one compact workflow tuned for notebook screens at 100% zoom.
                    </p>
                    <div class="chip-row">{chip_html}</div>
                </div>
                <div class="header-aside">
                    <div class="header-aside-label">Pipelines</div>
                    <div class="header-aside-value">{len(display_names)}</div>
                    <div class="header-aside-copy">Current catalog available for automatic detection and manual recovery.</div>
                </div>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def render_upload_section():

    st.markdown(
        """
        <section class="upload-panel-compact">
            <div class="section-caption">Input</div>
            <h2 class="section-title">Batch Upload Workspace</h2>
            <p class="section-copy">Load one or more Excel or CSV files and process the batch when you are ready.</p>
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

    return uploaded_files, file_payloads


def render_action_bar(uploaded_files, worker_count):
    columns = st.columns([1.15, 2.45])

    with columns[0]:
        run_clicked = st.button(
            "Process Files",
            use_container_width=True,
            disabled=not uploaded_files,
            key="process_button",
        )

    with columns[1]:
        st.markdown(
            f"""
            <div class="inline-note">
                {len(uploaded_files) if uploaded_files else 0} file(s) selected with {worker_count} worker(s). Automatic validation runs inside processing.
            </div>
            """,
            unsafe_allow_html=True,
        )

    return run_clicked


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
