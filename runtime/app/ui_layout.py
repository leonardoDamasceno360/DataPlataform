import html
import io
import zipfile
from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st

from runtime.app.config import APP_HOME, HISTORY_ROOT, OUTPUT_ROOT, PREVIEW_ROWS
from runtime.app.services import (
    build_status_dataframe,
    format_output_path,
    list_recent_history,
)


def _load_preview_frame(result):

    output_files = result.get("OutputFiles", [])

    if not output_files:
        return None

    output_path = Path(output_files[0]["path"])

    if not output_path.exists():
        return None

    preview_df = pd.read_excel(
        output_path,
        sheet_name=0,
        nrows=PREVIEW_ROWS,
    )

    for column_name in preview_df.columns:
        if pd.api.types.is_datetime64_any_dtype(preview_df[column_name]):
            preview_df[column_name] = preview_df[column_name].dt.strftime("%d/%m/%Y")

    return preview_df


def _read_result_log(result):

    log_path = result.get("LogPath")

    if log_path:
        try:
            log_file = Path(log_path)
            if log_file.exists():
                return log_file.read_text(encoding="utf-8")
        except OSError:
            pass

    return result.get("Log", "")


def render_empty_state():
    return


def render_overview_tab(results, display_names):

    st.markdown(
        """
        <section class="section-card-compact">
            <div class="section-caption">Overview</div>
            <h3 class="section-title">Execution Status</h3>
            <p class="section-copy">Review pipeline, status, rows and runtime before moving to preview or downloads.</p>
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
            <p class="section-copy">Inspect a small sample of each successful output without opening the final Excel file.</p>
        </section>
        """,
        unsafe_allow_html=True,
    )

    preview_results = [
        result
        for result in results
        if result["Status"] == "Success"
        and result.get("OutputFiles")
    ]

    if not preview_results:
        st.warning("No previews are available.")
        return

    for result in preview_results:
        with st.expander(
            f"{result['DisplayBase']} | {result['Arquivo']}",
            expanded=False,
        ):
            try:
                preview_df = _load_preview_frame(result)
            except Exception as exc:
                st.warning(f"Preview unavailable: {exc}")
                continue

            if preview_df is None or preview_df.empty:
                st.info("Preview unavailable for this output.")
                continue

            st.dataframe(
                preview_df,
                use_container_width=True,
                hide_index=True,
            )


def render_downloads_tab(results):

    st.markdown(
        """
        <section class="section-card-compact">
            <div class="section-caption">Downloads</div>
            <h3 class="section-title">Export Center</h3>
            <p class="section-copy">Export individual outputs or package the successful batch into one ZIP file.</p>
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
    zip_available = True

    try:
        with zipfile.ZipFile(zip_buffer, "w") as zip_file:
            for result in successful_results:
                output_meta = result.get(
                    "OutputFiles",
                    [],
                )[0]
                output_path = Path(
                    output_meta["path"]
                )

                if output_path.exists():
                    zip_file.write(
                        output_path,
                        arcname=output_meta["file_name"],
                    )
        zip_buffer.seek(0)
    except OSError:
        zip_available = False

    top_cols = st.columns([3.2, 1.0], vertical_alignment="center")
    with top_cols[0]:
        st.markdown(
            '<div class="inline-note export-note">ZIP export groups every successful file from the current run without reprocessing.</div>',
            unsafe_allow_html=True,
        )
    with top_cols[1]:
        st.download_button(
            "Download ZIP",
            zip_buffer if zip_available else b"",
            file_name=f"processed_{datetime.today().strftime('%Y-%m-%d')}.zip",
            key="download_zip_button",
            disabled=not zip_available,
            use_container_width=True,
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
        output_path = Path(
            output_meta["path"]
        )
        try:
            output_bytes = (
                output_path.read_bytes()
                if output_path.exists()
                else b""
            )
        except OSError:
            output_bytes = b""
        cols[4].download_button(
            "Download",
            data=output_bytes,
            file_name=result["Output"],
            key=f"download_{index}_{result['Output']}",
            disabled=not output_path.exists(),
            use_container_width=True,
        )

    st.markdown("</div>", unsafe_allow_html=True)


def render_logs_tab(results):

    st.markdown(
        """
        <section class="section-card-compact">
            <div class="section-caption">Logs</div>
            <h3 class="section-title">Execution Logs</h3>
            <p class="section-copy">Review the consolidated execution trace for the latest batch and export it when needed.</p>
        </section>
        """,
        unsafe_allow_html=True,
    )

    log_text = "\n\n".join(
        filter(
            None,
            (
                _read_result_log(result)
                for result in results
            ),
        )
    ).strip()

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
            <p class="section-copy">Historical executions remain available between sessions for operational follow-up and auditability.</p>
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
