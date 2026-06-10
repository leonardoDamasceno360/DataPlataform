from runtime.core.schema_utils import select_and_rename_columns


class SeparationForms:

    COLUMN_SPECS = [
        ("ID", ["ID", "\nID"]),
        ("Separation type", ["Separation type", "\nSeparation type"]),
        ("HR Remarks", ["HR Remarks", "\nHR Remarks"]),
    ]

    def process(self, df):

        return select_and_rename_columns(
            df,
            self.COLUMN_SPECS,
        )
