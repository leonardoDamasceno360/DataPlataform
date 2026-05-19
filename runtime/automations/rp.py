from runtime.core.schema_utils import find_column


class RP:

    def process(self, df):

        id_col = find_column(
            df,
            [
                "Id Contratado",
                "ID",
                "Employee ID"
            ]
        )

        date_col = find_column(
            df,
            [
                "Data do Dia (Data/Hora)",
                "Date"
            ]
        )

        rest_col = find_column(
            df,
            [
                "Interjornada Praticada",
                "Rest Period Hours"
            ]
        )

        return df[[

            id_col,

            date_col,

            rest_col
        ]]
