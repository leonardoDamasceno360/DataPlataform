import html
import io
import zipfile
from datetime import datetime

import pandas as pd
import streamlit as st

from runtime.app.config import APP_HOME, HISTORY_ROOT, OUTPUT_ROOT, PREVIEW_ROWS
from runtime.app.services import (
    build_status_dataframe,
    format_output_path,
    list_recent_history,
)


def render_empty_state():

    st.markdown(
        """
        <section class="section-card-compact">
            <div class="section-caption">Ready</div>
            <h3 class="section-title">Start a new batch</h3>
            <p class="section-copy">Use the upload area to load files, validate schema compatibility and then process only when the batch is ready.</p>
        </section>
        """,
        unsafe_allow_html=True,
    )


def render_overview_tab(results, display_names):

    st.markdown(
        """
        <section class="section-card-compact">
            <div class="section-caption">Overview</div>
            <h3 class="section-title">Execution Status</h3>
            <p class="section-copy">Review file status, generated rows and runtime before downloading the outputs.</p>
        </section>
        """,
        unsafe_allow_html=True,
    )

    st.dataframe(
        build_status_dataframe(
            results,
            display_names,
        ),
        use_container_width=True,
        hide_index=True,
    )


def render_preview_tab(results):

    st.markdown(
        """
        <section class="section-card-compact">
            <div class="section-caption">Preview</div>
            <h3 class="section-title">Processed Samples</h3>
            <p class="section-copy">Inspect the first rows of each successful output without opening the final Excel file.</p>
        </section>
        """,
        unsafe_allow_html=True,
    )

    preview_results = [
        result
        for result in results
        if result["DataFrame"] is not None
    ]

    if not preview_results:
        st.warning("No previews are available.")
        return

    for result in preview_results:
        with st.expander(
            f"{result['DisplayBase']} | {result['Arquivo']}",
            expanded=False,
        ):
            st.dataframe(
                result["DataFrame"].head(PREVIEW_ROWS),
                use_container_width=True,
                hide_index=True,
            )


def render_downloads_tab(results):

    st.markdown(
        """
        <section class="section-card-compact">
            <div class="section-caption">Downloads</div>
            <h3 class="section-title">Export Center</h3>
            <p class="section-copy">Review generated files, row counts and export timestamps, then download individual outputs or the full ZIP package.</p>
        </section>
        """,
        unsafe_allow_html=True,
    )

    successful_results = [
        result
        for result in results
        if result["Status"] == "Success"
    ]

    if not successful_results:
        st.warning("No successful outputs are available for download.")
        return

    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, "w") as zip_file:
        for result in successful_results:
            zip_file.writestr(
                result["Output"],
                result["Bytes"],
            )

    zip_buffer.seek(0)

    top_cols = st.columns([1.3, 3.0])
    with top_cols[0]:
        st.download_button(
            "Download Full ZIP",
            zip_buffer,
            file_name=f"processed_{datetime.today().strftime('%Y-%m-%d')}.zip",
            use_container_width=True,
        )
    with top_cols[1]:
        st.markdown(
            '<div class="inline-note">ZIP export groups every successful output from the latest batch without reprocessing the files.</div>',
            unsafe_allow_html=True,
        )

    st.markdown('<div class="export-table">', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="export-row header">
            <div class="export-cell">File Name</div>
            <div class="export-cell">Pipeline</div>
            <div class="export-cell">Rows</div>
            <div class="export-cell">Generated At</div>
            <div class="export-cell">Action</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    for index, result in enumerate(successful_results):
        output_meta = result.get(
            "OutputFiles",
            [],
        )[0]

        cols = st.columns([2.2, 1.0, 0.8, 1.2, 0.9])
        cols[0].markdown(
            f"<div class='export-cell'>{html.escape(output_meta['file_name'])}</div>",
            unsafe_allow_html=True,
        )
        cols[1].markdown(
            f"<div class='export-cell'>{html.escape(output_meta['pipeline_name'])}</div>",
            unsafe_allow_html=True,
        )
        cols[2].markdown(
            f"<div class='export-cell'>{output_meta['rows']}</div>",
            unsafe_allow_html=True,
        )
        cols[3].markdown(
            f"<div class='export-cell'>{html.escape(output_meta['created_at'])}</div>",
            unsafe_allow_html=True,
        )
        cols[4].download_button(
            "Download",
            data=result["Bytes"],
            file_name=result["Output"],
            key=f"download_{index}_{result['Output']}",
            use_container_width=True,
        )

    st.markdown("</div>", unsafe_allow_html=True)


def render_logs_tab(results):

    st.markdown(
        """
        <section class="section-card-compact">
            <div class="section-caption">Logs</div>
            <h3 class="section-title">Execution Logs</h3>
            <p class="section-copy">Each file execution produces its own log entry and saved log file for traceability.</p>
        </section>
        """,
        unsafe_allow_html=True,
    )

    combined_lines = []

    for result in results:
        combined_lines.extend(
            result.get("LogLines", [result["Log"]])
        )
        combined_lines.append("")

    log_text = "\n".join(combined_lines).strip()

    st.code(
        log_text,
        language="text",
    )
    st.download_button(
        "Download Combined Log",
        data=log_text.encode("utf-8"),
        file_name=f"execution_log_{datetime.today().strftime('%Y%m%d_%H%M%S')}.txt",
        use_container_width=False,
    )


def render_history_tab():

    st.markdown(
        """
        <section class="section-card-compact">
            <div class="section-caption">History</div>
            <h3 class="section-title">Execution Archive</h3>
            <p class="section-copy">History persists between sessions and records pipeline, file, status, generated rows and execution duration.</p>
        </section>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <span class="path-chip">Outputs: {html.escape(format_output_path(OUTPUT_ROOT))}</span>
        <span class="path-chip">History: {html.escape(format_output_path(HISTORY_ROOT))}</span>
        <span class="path-chip">App Home: {html.escape(format_output_path(APP_HOME))}</span>
        """,
        unsafe_allow_html=True,
    )

    history_rows = list_recent_history()

    if not history_rows:
        st.info("No historical executions were found yet.")
        return

    st.dataframe(
        pd.DataFrame(history_rows),
        use_container_width=True,
        hide_index=True,
    )
