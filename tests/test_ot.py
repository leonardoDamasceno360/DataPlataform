import unittest
from pathlib import Path
import sys

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from runtime.automations.ot import OT


class OTTestCase(unittest.TestCase):

    def _process_rows(self, rows, compliance_column="OT Hours Compliance Classification"):
        source_rows = []

        for index, row in enumerate(rows, start=1):
            source_rows.append(
                {
                    "ID": index,
                    "DATE": "2026-07-14",
                    "Type of Day": row.get("type_of_day"),
                    "Last OT Request Status": row.get(
                        "request_status",
                        "Aprovado",
                    ),
                    "Total OT Hours Done": row.get("hours"),
                    "OT Classification": "",
                    compliance_column: row.get(
                        "source_compliance",
                        "Compliance",
                    ),
                }
            )

        return OT().process(pd.DataFrame(source_rows))

    def test_compliance_as_per_mn1_boundaries(self):
        result = self._process_rows(
            [
                {"type_of_day": "Regular Day", "hours": 4},
                {"type_of_day": "Regular Day", "hours": 4.01},
                {"type_of_day": "Weekend", "hours": 8},
                {"type_of_day": "Weekend", "hours": 8.01},
                {"type_of_day": "Holiday", "hours": 8},
                {"type_of_day": "Holiday", "hours": 8.01},
                {"type_of_day": "Regular Day", "hours": ""},
                {"type_of_day": "Unknown", "hours": 1},
            ]
        )

        self.assertEqual(
            result["Compliance as per MN1"].tolist(),
            [
                "Compliant",
                "Non-Compliant",
                "Compliant",
                "Non-Compliant",
                "Compliant",
                "Non-Compliant",
                "",
                "",
            ],
        )

    def test_original_compliance_is_preserved_and_mn1_is_independent(self):
        result = self._process_rows(
            [
                {
                    "type_of_day": "Regular Day",
                    "hours": 3,
                    "source_compliance": "Non Compliance",
                },
                {
                    "type_of_day": "Regular Day",
                    "hours": 5,
                    "source_compliance": "Compliance",
                },
            ]
        )

        self.assertEqual(
            result["Ot hours compliance classification"].tolist(),
            [
                "Non-Compliant",
                "Compliant",
            ],
        )
        self.assertEqual(
            result["Compliance as per MN1"].tolist(),
            [
                "Compliant",
                "Non-Compliant",
            ],
        )

    def test_mn1_compliance_alias_is_supported(self):
        result = self._process_rows(
            [
                {
                    "type_of_day": "Regular Day",
                    "hours": "04:00:00",
                    "source_compliance": "Compliance",
                }
            ],
            compliance_column="OT Hours Compliance MN1",
        )

        self.assertEqual(
            result["Ot hours compliance classification"].iloc[0],
            "Compliant",
        )
        self.assertEqual(
            result["Compliance as per MN1"].iloc[0],
            "Compliant",
        )

    def test_ot_classification_and_final_column_order(self):
        result = self._process_rows(
            [
                {"type_of_day": "Regular Day", "hours": 0.5},
                {"type_of_day": "Regular Day", "hours": "2,00"},
                {"type_of_day": "Regular Day", "hours": "04:00"},
                {
                    "type_of_day": "Regular Day",
                    "hours": pd.Timedelta(hours=4, minutes=1),
                },
            ]
        )

        self.assertEqual(
            result["Ot classification"].tolist(),
            [
                "Up to 30min",
                "30 min to 2 hours",
                "2 hours to 4 hours",
                "over 4 hours",
            ],
        )
        self.assertEqual(
            list(result.columns),
            [
                "Id",
                "Date",
                "Type of day",
                "Last ot request status",
                "Total ot hours done",
                "Ot classification",
                "Ot hours compliance classification",
                "Compliance as per MN1",
                "Request Status",
            ],
        )

    def test_request_status_standardization(self):
        result = self._process_rows(
            [
                {"type_of_day": "Regular Day", "hours": 1, "request_status": "Aprovado"},
                {"type_of_day": "Regular Day", "hours": 1, "request_status": "Reprovado"},
                {"type_of_day": "Regular Day", "hours": 1, "request_status": "Em Andamento"},
                {"type_of_day": "Regular Day", "hours": 1, "request_status": "Non Requested"},
            ]
        )

        self.assertEqual(
            result["Request Status"].tolist(),
            [
                "Approved",
                "Reproved",
                "Requested",
                "Not Requested",
            ],
        )


if __name__ == "__main__":
    unittest.main()
