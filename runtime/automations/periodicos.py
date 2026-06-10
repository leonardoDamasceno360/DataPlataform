from runtime.core.schema_utils import (
    current_report_month,
    select_and_rename_columns,
)


class Periodicos:

    COLUMN_SPECS = [
        ("ID", ["id", "employee id", "associate id", "matricula"]),
        (
            "DATE EXPIRATION ASO",
            [
                "date expiration aso",
                "expiration",
                "expiration date",
                "validity",
                "due date",
            ],
        ),
        ("STATUS ASO", ["status aso", "status"]),
    ]

    def process(self, df):

        result = select_and_rename_columns(
            df,
            self.COLUMN_SPECS,
        )
        result["Report Month"] = current_report_month()
        return result
