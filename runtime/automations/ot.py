import re

import pandas as pd

from runtime.core.schema_utils import (
    find_column,
    normalize_text,
    select_and_rename_columns,
    to_date_series,
    to_decimal_series,
    to_integer_series,
)


class OT:

    COMMON_COLUMN_SPECS = [
        ("Id", ["ID", "Id"]),
        ("Date", ["DATE", "Date"]),
        ("Type of day", ["Type of Day", "Type of day"]),
        (
            "Last ot request status",
            ["Last OT Request Status", "Last Ot Request Status"],
        ),
        (
            "Total ot hours done",
            ["Total OT Hours Done", "Total Ot Hours Done"],
        ),
        (
            "Ot classification",
            ["OT Classification", "Ot Classification"],
        ),
    ]

    NORMAL_COMPLIANCE_ALIASES = [
        "OT Hours Compliance Classification",
        "Ot Hours Compliance Classification",
    ]

    MN1_COMPLIANCE_ALIASES = [
        "OT Hours Compliance MN1",
        "Ot Hours Compliance MN1",
    ]

    COLUMN_SPECS = COMMON_COLUMN_SPECS + [
        (
            "Ot hours compliance classification",
            NORMAL_COMPLIANCE_ALIASES
            + MN1_COMPLIANCE_ALIASES
            + ["OT Hours Compliance"],
        ),
    ]

    def process(self, df):

        result = select_and_rename_columns(
            df,
            self.COMMON_COLUMN_SPECS,
        )
        compliance_source = self._resolve_compliance_source(df)
        result["Ot hours compliance classification"] = df[
            compliance_source
        ].apply(self._normalize_compliance_label)
        result["Id"] = to_integer_series(
            result["Id"]
        )
        result["Date"] = to_date_series(
            result["Date"]
        )
        result["Total ot hours done"] = to_decimal_series(
            result["Total ot hours done"]
        )
        result["Ot classification"] = result.apply(
            self._build_ot_classification,
            axis=1,
        )
        result["Compliance as per MN1"] = result.apply(
            self._build_compliance_status,
            axis=1,
        )
        result["Request Status"] = result[
            "Last ot request status"
        ].apply(self._build_request_status)
        final_columns = [
            "Id",
            "Date",
            "Type of day",
            "Last ot request status",
            "Total ot hours done",
            "Ot classification",
            "Ot hours compliance classification",
            "Compliance as per MN1",
            "Request Status",
        ]
        return result[final_columns]

    @classmethod
    def _resolve_compliance_source(cls, df):

        normal_source = find_column(
            df,
            cls.NORMAL_COMPLIANCE_ALIASES,
        )
        if normal_source:
            return normal_source

        mn1_source = find_column(
            df,
            cls.MN1_COMPLIANCE_ALIASES,
        )
        if mn1_source:
            return mn1_source

        fallback_source = find_column(
            df,
            ["OT Hours Compliance"],
        )
        if fallback_source:
            return fallback_source

        raise ValueError(
            "Required column not found: Ot hours compliance classification"
        )

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
    def _build_ot_classification(cls, row):

        ot_hours = cls._parse_ot_hours(
            row.get("Total ot hours done")
        )

        if ot_hours is not None:
            if ot_hours <= 0.5:
                return "Up to 30min"

            if ot_hours <= 2:
                return "30 min to 2 hours"

            if ot_hours <= 4:
                return "2 hours to 4 hours"

            return "over 4 hours"

        return cls._translate_ot_classification(
            row.get("Ot classification")
        )

    @staticmethod
    def _translate_ot_classification(value):

        if pd.isna(value):
            return ""

        text = str(value).strip()

        if not text:
            return ""

        normalized_value = normalize_text(text)

        classification_map = {
            "ate 30 min": "Up to 30min",
            "ate 30 mins": "Up to 30min",
            "up to 30 min": "Up to 30min",
            "up to 30 mins": "Up to 30min",
            "ate 2 hrs": "30 min to 2 hours",
            "ate 2 hr": "30 min to 2 hours",
            "ate 2 horas": "30 min to 2 hours",
            "up to 2 hrs": "30 min to 2 hours",
            "up to 2 hours": "30 min to 2 hours",
            "30 min a 2 hrs": "30 min to 2 hours",
            "30 min a 2 hr": "30 min to 2 hours",
            "30 min a 2 horas": "30 min to 2 hours",
            "30 min to 2 hrs": "30 min to 2 hours",
            "30 min to 2 hours": "30 min to 2 hours",
            "de 2 ate 4 hrs": "2 hours to 4 hours",
            "de 2 ate 4 hr": "2 hours to 4 hours",
            "de 2 ate 4 horas": "2 hours to 4 hours",
            "2 hrs a 4 hrs": "2 hours to 4 hours",
            "2 hr a 4 hr": "2 hours to 4 hours",
            "2 horas a 4 horas": "2 hours to 4 hours",
            "2 hours to 4 hours": "2 hours to 4 hours",
            "mais de 4 hrs": "over 4 hours",
            "mais de 4 hr": "over 4 hours",
            "mais de 4 horas": "over 4 hours",
            "more than 4 hours": "over 4 hours",
            "over 4 hours": "over 4 hours",
        }

        if normalized_value in classification_map:
            return classification_map[
                normalized_value
            ]

        return text

    @classmethod
    def _build_compliance_status(cls, row):

        day_type = normalize_text(row.get("Type of day", ""))
        ot_hours = cls._parse_ot_hours(
            row.get("Total ot hours done")
        )

        if ot_hours is None:
            return ""

        if day_type == "regular day":
            return (
                "Non-Compliant"
                if ot_hours > 4
                else "Compliant"
            )

        if day_type in ("weekend", "holiday"):
            return (
                "Non-Compliant"
                if ot_hours > 8
                else "Compliant"
            )

        return ""

    @staticmethod
    def _normalize_compliance_label(value):

        if pd.isna(value):
            return ""

        text = str(value).strip()

        if not text:
            return ""

        normalized_value = normalize_text(text)

        compliance_map = {
            "non compliance": "Non-Compliant",
            "non-compliance": "Non-Compliant",
            "not compliant": "Non-Compliant",
            "not-compliant": "Non-Compliant",
            "compliance": "Compliant",
            "compliant": "Compliant",
        }

        return compliance_map.get(
            normalized_value,
            text,
        )

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

        if "approved" in normalized_value or "aprovado" in normalized_value:
            return "Approved"

        if "reproved" in normalized_value or "reprovado" in normalized_value:
            return "Reproved"

        if "request" in normalized_value:
            return "Requested"

        return "Requested"
