from runtime.core.schema_utils import find_column


class SeparationForms:

    def process(self, df):

        id_col = find_column(
            df,
            [
                "ID",
                "\nID"
            ]
        )

        type_col = find_column(
            df,
            [
                "Separation type",
                "\nSeparation type"
            ]
        )

        remarks_col = find_column(
            df,
            [
                "HR Remarks",
                "\nHR Remarks"
            ]
        )

        return df[[

            id_col,

            type_col,

            remarks_col
        ]]
