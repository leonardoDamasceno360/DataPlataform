from runtime.core.schema_utils import (
    current_report_month,
    select_and_rename_columns,
)


class DesligadosGeral:

    COLUMN_SPECS = [
        ("Id Contratado", ["Id Contratado", "ID", "\nID"]),
        (
            "SEPARATION REASON",
            [
                "SEPARATION REASON",
                "Separation Reason",
                "TERMINATION REASON",
                "Termination Reason",
            ],
        ),
        ("CATEGORY", ["CATEGORY", "Category"]),
    ]

    def process(self, df):

        result = select_and_rename_columns(
            df,
            self.COLUMN_SPECS,
        )
        result["Report Month"] = current_report_month()
        return result
