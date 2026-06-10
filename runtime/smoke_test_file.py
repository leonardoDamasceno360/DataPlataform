import argparse
from pathlib import Path

from runtime.automations import AUTOMATIONS
from runtime.core.detector import detect_automation
from runtime.core.engine import AutomationEngine
from runtime.core.loader import load_file


def main():
    parser = argparse.ArgumentParser(
        description="Smoke test a single input file against the processing engine."
    )
    parser.add_argument(
        "file_path",
        help="Path to the input Excel or CSV file.",
    )
    parser.add_argument(
        "--expected-pipeline",
        dest="expected_pipeline",
        help="Fail if the detected pipeline differs from this value.",
    )
    args = parser.parse_args()

    file_path = Path(args.file_path)

    if not file_path.exists():
        raise SystemExit(f"File not found: {file_path}")

    with file_path.open("rb") as handle:
        df = load_file(handle)

    detected = detect_automation(
        df,
        file_path.name,
    )

    if not detected:
        raise SystemExit("Pipeline detection failed.")

    if args.expected_pipeline and detected != args.expected_pipeline:
        raise SystemExit(
            "Unexpected pipeline. "
            f"Expected '{args.expected_pipeline}', got '{detected}'."
        )

    engine = AutomationEngine(
        AUTOMATIONS[detected]
    )
    result = engine.run(df)

    print(f"file={file_path.name}")
    print(f"pipeline={detected}")
    print(f"input_columns={list(df.columns)}")
    print(f"output_columns={list(result.columns)}")
    print(f"rows={len(result)}")
    print(result.head(5).to_string(index=False))


if __name__ == "__main__":
    main()
