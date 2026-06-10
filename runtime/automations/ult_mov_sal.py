from runtime.core.schema_utils import select_and_rename_columns


class UltMovSal:

    COLUMN_SPECS = [
        ("ID", ["ID"]),
        ("EFECTIVE DATE", ["EFECTIVE DATE", "Effective Date"]),
    ]

    def process(self, df):

        return select_and_rename_columns(
            df,
            self.COLUMN_SPECS,
        )
