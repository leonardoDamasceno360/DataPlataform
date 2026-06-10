from runtime.core.schema_utils import (
    current_report_month,
    select_and_rename_columns,
)


class Xcelerate:

    COLUMN_SPECS = [
        ("ID", ["ID"]),
        ("Status", ["Status"]),
    ]

    def process(self, df):

        result = select_and_rename_columns(
            df,
            self.COLUMN_SPECS,
        )
        result["Report Month"] = current_report_month()
        return result
