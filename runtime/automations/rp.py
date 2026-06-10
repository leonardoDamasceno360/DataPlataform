from runtime.core.schema_utils import select_and_rename_columns


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

        return select_and_rename_columns(
            df,
            self.COLUMN_SPECS,
        )
