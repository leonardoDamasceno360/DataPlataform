from runtime.core.schema_utils import (
    select_and_rename_columns,
    to_date_series,
    to_integer_series,
)


class UltMovSal:

    COLUMN_SPECS = [
        ("ID", ["ID"]),
        ("EFECTIVE DATE", ["EFECTIVE DATE", "Effective Date"]),
    ]

    def process(self, df):

        result = select_and_rename_columns(
            df,
            self.COLUMN_SPECS,
        )
        result["ID"] = to_integer_series(
            result["ID"]
        )
        result["EFECTIVE DATE"] = to_date_series(
            result["EFECTIVE DATE"]
        )
        return result
