from runtime.core.schema_utils import find_column

class UltMovSal:

    def process(self, df):

        id_col = find_column(
            df,
            [
                "ID"
            ]
        )

        date_col = find_column(
            df,
            [
                "EFECTIVE DATE",
                "Effective Date"
            ]
        )

        return df[[

            id_col,

            date_col
        ]]
