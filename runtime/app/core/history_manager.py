import json
from datetime import datetime
from pathlib import Path

from runtime.app.config import (
    EXECUTION_HISTORY_FILE,
    HISTORY_PREVIEW_LIMIT,
    HISTORY_ROOT,
)


def _ensure_parent(path_obj: Path):
    path_obj.parent.mkdir(
        parents=True,
        exist_ok=True,
    )


def append_history_entry(entry: dict):
    _ensure_parent(EXECUTION_HISTORY_FILE)
    with EXECUTION_HISTORY_FILE.open(
        "a",
        encoding="utf-8",
    ) as handle:
        handle.write(
            json.dumps(
                entry,
                ensure_ascii=False,
            )
        )
        handle.write("\n")


def load_history_entries(limit=None):
    if not EXECUTION_HISTORY_FILE.exists():
        return []

    rows = []

    with EXECUTION_HISTORY_FILE.open(
        "r",
        encoding="utf-8",
    ) as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))

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

    if not HISTORY_ROOT.exists():
        return files

    for path in HISTORY_ROOT.rglob("*"):
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
