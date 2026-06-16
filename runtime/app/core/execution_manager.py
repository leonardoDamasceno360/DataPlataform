import hashlib
import io
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from time import perf_counter

import pandas as pd
import streamlit as st
from openpyxl.utils import get_column_letter

from runtime.automations import AUTOMATIONS
from runtime.app.config import (
    HISTORY_ROOT,
    LOG_ROOT,
    PIPELINE_SHEET_NAMES,
    SCHEMA_RULES,
)
from runtime.app.core.history_manager import append_history_entry
from runtime.app.models import (
    OutputFile,
    PipelineResult,
    ValidationResult,
)
from runtime.core.detector import detect_automation
from runtime.core.engine import AutomationEngine
from runtime.core.loader import load_file
from runtime.core.schema_utils import (
    find_column,
    normalized_columns,
    normalize_text,
)


logger = logging.getLogger("data_platform")


def pipeline_label(base_name, display_names):

    return display_names.get(
        base_name,
        base_name,
    )


def pipeline_sheet_name(base_name, display_names):

    return PIPELINE_SHEET_NAMES.get(
        base_name,
        pipeline_label(base_name, display_names),
    )


def safe_text(value, fallback="Not available"):

    if value is None:
        return fallback

    return str(value)


def file_hash(file_bytes, file_name):

    return hashlib.md5(
        file_name.encode("utf-8") + file_bytes
    ).hexdigest()


def build_file_object(file_bytes, file_name):

    file_like = io.BytesIO(file_bytes)
    file_like.name = file_name
    return file_like


def get_pipeline_load_aliases(base_label):

    automation = AUTOMATIONS.get(base_label)

    if automation is None:
        return None

    column_specs = getattr(
        automation,
        "COLUMN_SPECS",
        None,
    )

    if not column_specs:
        return None

    aliases = []

    for _, column_aliases in column_specs:
        aliases.extend(column_aliases)

    return tuple(dict.fromkeys(aliases))


def validate_input_schema(df, base_label):
    automation = AUTOMATIONS.get(base_label)
    column_specs = getattr(
        automation,
        "COLUMN_SPECS",
        None,
    )

    if column_specs:
        return [
            output_name
            for output_name, aliases in column_specs
            if not find_column(df, aliases)
        ]

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


def unique_history_path(history_dir, file_name):

    target_path = history_dir / file_name

    if not target_path.exists():
        return target_path

    stem = target_path.stem
    suffix = target_path.suffix

    for counter in range(1, 1000):
        candidate = history_dir / f"{stem}_{counter:02d}{suffix}"

        if not candidate.exists():
            return candidate

    raise RuntimeError(
        f"Unable to allocate a unique history name for {file_name}"
    )


def save_history(file_name, buffer):

    history_dir = HISTORY_ROOT / datetime.today().strftime("%Y-%m-%d")
    history_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path = unique_history_path(
        history_dir,
        file_name,
    )
    output_path.write_bytes(buffer.getvalue())
    return output_path


def format_excel_report_dates(worksheet, result_df):

    if "Report Month" not in result_df.columns:
        return

    column_index = result_df.columns.get_loc("Report Month") + 1
    column_letter = get_column_letter(column_index)

    for cell in worksheet[column_letter][1:]:
        cell.number_format = "DD/MM/YYYY"


def format_output_path(path_obj):

    return str(path_obj).replace("\\", "/")


@st.cache_data(show_spinner=False)
def cached_load(
    file_hash_key,
    file_bytes,
    file_name,
    selected_aliases=None,
):

    return load_file(
        build_file_object(
            file_bytes,
            file_name,
        ),
        selected_aliases=selected_aliases,
    )


@st.cache_data(show_spinner=False)
def cached_detect(
    file_hash_key,
    file_name,
):

    return detect_automation(None, file_name)


@st.cache_data(show_spinner=False)
def cached_validate(
    file_hash_key,
    file_bytes,
    file_name,
):

    input_df = cached_load(
        file_hash_key,
        file_bytes,
        file_name,
        None,
    )
    detected_base = detect_automation(
        input_df,
        file_name,
    ) or cached_detect(
        file_hash_key,
        file_name,
    )

    if not detected_base:
        return ValidationResult(
            file_name=file_name,
            file_hash=file_hash_key,
            file_size_kb=round(len(file_bytes) / 1024, 1),
            is_valid=False,
            pipeline_name=None,
            errors=["Automatic pipeline detection failed."],
            detected_columns=list(input_df.columns),
            action_label="Select pipeline",
        ).to_dict()

    missing_columns = []

    if detected_base != "IBelong":
        missing_columns = validate_input_schema(
            input_df,
            detected_base,
        )

    is_valid = len(missing_columns) == 0
    errors = []

    if missing_columns:
        errors.append(
            "Missing columns: "
            + ", ".join(missing_columns)
        )

    return ValidationResult(
        file_name=file_name,
        file_hash=file_hash_key,
        file_size_kb=round(len(file_bytes) / 1024, 1),
        is_valid=is_valid,
        pipeline_name=detected_base,
        errors=errors,
        detected_columns=list(input_df.columns),
        missing_columns=missing_columns,
        action_label=(
            "Process"
            if is_valid
            else "Manual recovery"
        ),
    ).to_dict()


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


def validate_uploaded_files(
    file_payloads,
    display_names,
):
    validations = []

    for item in file_payloads:
        validation = cached_validate(
            item["hash"],
            item["bytes"],
            item["name"],
        )
        validation["pipeline_label"] = pipeline_label(
            validation.get("pipeline_name") or "Unidentified",
            display_names,
        )
        validation["validation_message"] = (
            "; ".join(validation["errors"])
            if validation["errors"]
            else "Schema validated successfully."
        )
        validations.append(validation)

    return validations


def _write_execution_log(file_hash_key, lines):
    LOG_ROOT.mkdir(
        parents=True,
        exist_ok=True,
    )
    log_path = LOG_ROOT / f"{file_hash_key}.log"
    log_path.write_text(
        "\n".join(lines),
        encoding="utf-8",
    )
    return log_path


def process_file(
    file_index,
    file_name,
    file_bytes,
    display_names,
    selected_base=None,
):

    hash_key = None
    started_at = datetime.now()
    execution_start = perf_counter()

    try:
        logger.info(
            "Starting processing for %s",
            file_name,
        )

        hash_key = file_hash(
            file_bytes,
            file_name,
        )
        if selected_base:
            detected_base = selected_base
            selected_aliases = get_pipeline_load_aliases(
                detected_base
            )
            input_df = cached_load(
                hash_key,
                file_bytes,
                file_name,
                selected_aliases,
            )
        else:
            input_df = cached_load(
                hash_key,
                file_bytes,
                file_name,
                None,
            )
            detected_base = detect_automation(
                input_df,
                file_name,
            ) or cached_detect(
                hash_key,
                file_name,
            )

        if not detected_base:
            raise ValueError(
                "Automatic pipeline detection failed for this file."
            )

        if detected_base != "IBelong":
            missing = validate_input_schema(
                input_df,
                detected_base,
            )

            if missing:
                raise ValueError(
                    "Input schema validation failed for "
                    f"{pipeline_label(detected_base, display_names)}. Missing columns: "
                    f"{', '.join(missing)}"
                )

        result_df = cached_process(
            hash_key,
            input_df,
            detected_base,
        )

        rows = len(result_df)
        buffer = io.BytesIO()
        display_base = pipeline_label(
            detected_base,
            display_names,
        )
        sheet_name = pipeline_sheet_name(
            detected_base,
            display_names,
        )[:31]

        with pd.ExcelWriter(
            buffer,
            engine="openpyxl",
        ) as writer:
            result_df.to_excel(
                writer,
                sheet_name=sheet_name,
                index=False,
            )
            worksheet = writer.sheets[sheet_name]
            format_excel_report_dates(
                worksheet,
                result_df,
            )

        buffer.seek(0)

        output_name = build_output_name(
            detected_base
        )
        output_path = save_history(
            output_name,
            buffer,
        )
        finished_at = datetime.now()
        duration = perf_counter() - execution_start
        log_lines = [
            f"Input file: {file_name}",
            f"Pipeline: {display_base}",
            f"Status: Success",
            f"Rows generated: {rows}",
            f"Started at: {started_at.strftime('%Y-%m-%d %H:%M:%S')}",
            f"Finished at: {finished_at.strftime('%Y-%m-%d %H:%M:%S')}",
            f"Duration seconds: {duration:.2f}",
            f"Output path: {format_output_path(output_path)}",
        ]
        log_path = _write_execution_log(
            hash_key,
            log_lines,
        )

        pipeline_result = PipelineResult(
            pipeline_name=display_base,
            status="Success",
            rows_generated=rows,
            execution_time=duration,
            started_at=started_at.strftime("%Y-%m-%d %H:%M:%S"),
            finished_at=finished_at.strftime("%Y-%m-%d %H:%M:%S"),
            input_file=file_name,
            file_hash=hash_key,
            log_lines=log_lines,
            output_files=[
                OutputFile(
                    path=format_output_path(output_path),
                    file_name=output_name,
                    rows=rows,
                    created_at=finished_at.strftime("%Y-%m-%d %H:%M:%S"),
                    pipeline_name=display_base,
                )
            ],
        )
        append_history_entry(
            pipeline_result.to_dict()
        )

        return {
            "Hash": hash_key,
            "Order": file_index,
            "Base": detected_base,
            "DisplayBase": display_base,
            "Arquivo": file_name,
            "Status": "Success",
            "Rows": rows,
            "ExecutionTime": duration,
            "StartedAt": pipeline_result.started_at,
            "FinishedAt": pipeline_result.finished_at,
            "DataFrame": result_df,
            "Output": output_name,
            "Bytes": buffer.getvalue(),
            "OutputFiles": [
                output.to_dict()
                for output in pipeline_result.output_files
            ],
            "Log": " | ".join(
                [
                    display_base,
                    f"{rows} rows",
                    f"{duration:.2f}s",
                    "Success",
                ]
            ),
            "LogLines": log_lines,
            "LogPath": format_output_path(log_path),
        }

    except Exception as exc:
        finished_at = datetime.now()
        duration = max(
            perf_counter() - execution_start,
            0.0,
        )
        logger.exception(
            "Processing failed for %s",
            file_name,
        )

        resolved_base = selected_base or "Unidentified"
        display_base = pipeline_label(
            resolved_base,
            display_names,
        )
        log_lines = [
            f"Input file: {file_name}",
            f"Pipeline: {display_base}",
            f"Status: Error",
            f"Error: {exc}",
            f"Started at: {started_at.strftime('%Y-%m-%d %H:%M:%S')}",
            f"Finished at: {finished_at.strftime('%Y-%m-%d %H:%M:%S')}",
        ]
        log_path = _write_execution_log(
            hash_key or file_name,
            log_lines,
        )
        append_history_entry(
            PipelineResult(
                pipeline_name=display_base,
                status="Error",
                errors=[str(exc)],
                execution_time=duration,
                started_at=started_at.strftime("%Y-%m-%d %H:%M:%S"),
                finished_at=finished_at.strftime("%Y-%m-%d %H:%M:%S"),
                input_file=file_name,
                file_hash=hash_key or "",
                log_lines=log_lines,
            ).to_dict()
        )

        return {
            "Hash": hash_key,
            "Order": file_index,
            "Base": resolved_base,
            "DisplayBase": display_base,
            "Arquivo": file_name,
            "Status": "Error",
            "Rows": 0,
            "ExecutionTime": duration,
            "StartedAt": started_at.strftime("%Y-%m-%d %H:%M:%S"),
            "FinishedAt": finished_at.strftime("%Y-%m-%d %H:%M:%S"),
            "DataFrame": None,
            "Output": None,
            "Bytes": None,
            "OutputFiles": [],
            "ErrorMessage": str(exc),
            "Log": f"{file_name} | Error: {exc}",
            "LogLines": log_lines,
            "LogPath": format_output_path(log_path),
        }


def process_uploaded_files(
    file_payloads,
    worker_count,
    display_names,
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
            file_index = len(futures)
            selected_base = None

            if manual_selection:
                selected_base = manual_selection.get(
                    item["name"]
                )

            futures.append(
                executor.submit(
                    process_file,
                    file_index,
                    item["name"],
                    item["bytes"],
                    display_names,
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
    results.sort(key=lambda item: item.get("Order", 0))
    return results


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


def build_status_dataframe(results, display_names):

    return pd.DataFrame(
        [
            {
                "File": result["Arquivo"],
                "Pipeline": result.get(
                    "DisplayBase",
                    pipeline_label(result["Base"], display_names),
                ),
                "Status": result["Status"],
                "Rows": result["Rows"],
                "Duration (s)": round(
                    result.get(
                        "ExecutionTime",
                        0.0,
                    ),
                    2,
                ),
                "Details": result.get(
                    "ErrorMessage",
                    "",
                ),
            }
            for result in results
        ]
    )
