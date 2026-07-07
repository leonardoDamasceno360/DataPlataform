import json
from datetime import datetime
from pathlib import Path

from runtime.app.config import (
    EXECUTION_HISTORY_FILE,
    HISTORY_PREVIEW_LIMIT,
    HISTORY_ROOT,
)

PROJECT_ROOT = Path(__file__).resolve().parents[3]
FALLBACK_HISTORY_ROOT = PROJECT_ROOT / "runtime_data" / "history"
FALLBACK_EXECUTION_HISTORY_FILE = (
    PROJECT_ROOT
    / "runtime_data"
    / "logs"
    / "execution_history.jsonl"
)


def _ensure_parent(path_obj: Path):
    path_obj.parent.mkdir(
        parents=True,
        exist_ok=True,
    )


def append_history_entry(entry: dict):
    candidate_files = [
        EXECUTION_HISTORY_FILE,
        FALLBACK_EXECUTION_HISTORY_FILE,
    ]
    payload = json.dumps(
        entry,
        ensure_ascii=False,
    )
    last_error = None

    for history_file in candidate_files:
        try:
            _ensure_parent(history_file)
            with history_file.open(
                "a",
                encoding="utf-8",
            ) as handle:
                handle.write(payload)
                handle.write("\n")
            return
        except OSError as exc:
            last_error = exc

    if last_error is not None:
        raise last_error


def _load_entries_from_path(history_file: Path):
    if not history_file.exists():
        return []

    rows = []

    with history_file.open(
        "r",
        encoding="utf-8",
    ) as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            rows.append(
                json.loads(line)
            )
    return rows


def load_history_entries(limit=None):
    rows = _load_entries_from_path(
        EXECUTION_HISTORY_FILE
    )

    if not rows:
        rows = _load_entries_from_path(
            FALLBACK_EXECUTION_HISTORY_FILE
        )

    rows.sort(
        key=lambda item: item.get(
            "finished_at",
            "",
        ),
        reverse=True,
    )

    if limit is not None:
        return rows[:limit]

    return rows


def list_recent_history():
    rows = load_history_entries(
        limit=HISTORY_PREVIEW_LIMIT
    )

    if rows:
        return [
            {
                "Executed At": item.get(
                    "finished_at",
                    "",
                ),
                "Input File": item.get(
                    "input_file",
                    "",
                ),
                "Pipeline": item.get(
                    "pipeline_name",
                    "",
                ),
                "Status": item.get(
                    "status",
                    "",
                ),
                "Rows": item.get(
                    "rows_generated",
                    0,
                ),
                "Duration (s)": round(
                    item.get(
                        "execution_time",
                        0.0,
                    ),
                    2,
                ),
            }
            for item in rows
        ]

    files = []

    history_roots = [
        HISTORY_ROOT,
        FALLBACK_HISTORY_ROOT,
    ]
    available_root = next(
        (
            root
            for root in history_roots
            if root.exists()
        ),
        None,
    )

    if available_root is None:
        return files

    for path in available_root.rglob("*"):
        if path.is_file():
            files.append(path)

    files.sort(
        key=lambda item: item.stat().st_mtime,
        reverse=True,
    )

    fallback_rows = []

    for path in files[:HISTORY_PREVIEW_LIMIT]:
        fallback_rows.append(
            {
                "Executed At": datetime.fromtimestamp(
                    path.stat().st_mtime
                ).strftime("%Y-%m-%d %H:%M"),
                "Input File": path.name,
                "Pipeline": path.parent.name,
                "Status": "Stored",
                "Rows": "",
                "Duration (s)": "",
            }
        )

    return fallback_rows
