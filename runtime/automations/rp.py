from runtime.core.schema_utils import (
    select_and_rename_columns,
    to_date_series,
    to_decimal_series,
    to_integer_series,
)


class RP:

    COLUMN_SPECS = [
        ("Id Contratado", ["Id Contratado", "ID", "Employee ID"]),
        (
            "Data do Dia (Data/Hora)",
            ["Data do Dia (Data/Hora)", "Date"],
        ),
        (
            "Interjornada Praticada",
            ["Interjornada Praticada", "Rest Period Hours"],
        ),
    ]

    def process(self, df):

        result = select_and_rename_columns(
            df,
            self.COLUMN_SPECS,
        )
        result["Id Contratado"] = to_integer_series(
            result["Id Contratado"]
        )
        result["Data do Dia (Data/Hora)"] = to_date_series(
            result["Data do Dia (Data/Hora)"]
        )
        result["Interjornada Praticada"] = to_decimal_series(
            result["Interjornada Praticada"]
        )
        return result
