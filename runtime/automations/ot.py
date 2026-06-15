import re

import pandas as pd

from runtime.core.schema_utils import (
    normalize_text,
    select_and_rename_columns,
)


class OT:

    COLUMN_SPECS = [
        ("ID", ["ID", "Id"]),
        ("DATE", ["DATE", "Date"]),
        ("Type of Day", ["Type of Day"]),
        (
            "Last OT Request Status",
            ["Last OT Request Status", "Last Ot Request Status"],
        ),
        (
            "Total OT Hours Done",
            ["Total OT Hours Done", "Total Ot Hours Done"],
        ),
        (
            "OT Classification",
            ["OT Classification", "Ot Classification"],
        ),
        (
            "OT Hours Compliance Classification",
            [
                "OT Hours Compliance Classification",
                "Ot Hours Compliance Classification",
                "OT Hours Compliance MN1",
                "Ot Hours Compliance MN1",
                "OT Hours Compliance",
            ],
        ),
    ]

    def process(self, df):

        result = select_and_rename_columns(
            df,
            self.COLUMN_SPECS,
        )
        result["Compliance as per MN1"] = result.apply(
            self._build_compliance_status,
            axis=1,
        )
        result["Request Status"] = result[
            "Last OT Request Status"
        ].apply(self._build_request_status)
        return result

    @staticmethod
    def _parse_ot_hours(value):

        if pd.isna(value):
            return None

        if isinstance(value, pd.Timedelta):
            return value.total_seconds() / 3600

        if isinstance(value, str):
            text = value.strip().replace(",", ".")

            time_match = re.fullmatch(
                r"(\d{1,2}):(\d{2})(?::(\d{2}))?",
                text,
            )
            if time_match:
                hours = int(time_match.group(1))
                minutes = int(time_match.group(2))
                seconds = int(time_match.group(3) or 0)
                return hours + (minutes / 60) + (seconds / 3600)

            numeric_match = re.search(r"-?\d+(?:\.\d+)?", text)
            if numeric_match:
                return float(numeric_match.group(0))

            return None

        numeric = pd.to_numeric(
            pd.Series([value]),
            errors="coerce",
        ).iloc[0]

        if pd.isna(numeric):
            return None

        return float(numeric)

    @classmethod
    def _build_compliance_status(cls, row):

        current_value = row.get(
            "OT Hours Compliance Classification"
        )
        day_type = normalize_text(row.get("Type of Day", ""))
        ot_hours = cls._parse_ot_hours(
            row.get("Total OT Hours Done")
        )

        if day_type == "regular day" and ot_hours is not None and ot_hours > 4:
            return "Not Compliant"

        if pd.isna(current_value):
            return ""

        return str(current_value).strip()

    @staticmethod
    def _build_request_status(value):

        if pd.isna(value):
            return "Not Requested"

        normalized_value = normalize_text(value)

        if not normalized_value:
            return "Not Requested"

        negative_markers = (
            "non requested",
            "non request",
            "non requested status",
            "not requested",
            "no request",
            "without request",
            "not request",
            "nao solicitado",
            "nao requisitado",
            "sem solicitacao",
        )
        if any(
            marker in normalized_value
            for marker in negative_markers
        ):
            return "Not Requested"

        if "request" in normalized_value:
            return "Requested"

        return "Requested"
