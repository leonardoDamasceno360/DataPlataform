from runtime.core.schema_utils import (
    current_report_month,
    select_and_rename_columns,
    to_date_series,
    to_integer_series,
)


class Gems:

    COLUMN_SPECS = [
        ("ID", ["ID"]),
        ("Nomeador", ["Nomeador"]),
        (
            "Data da NomeaÃ§Ã£o",
            [
                "Data da NomeaÃ§Ã£o",
                "Data da NomeaÃƒÂ§ÃƒÂ£o",
            ],
        ),
        (
            "PremiaÃ§Ã£o",
            [
                "PremiaÃ§Ã£o",
                "PremiaÃƒÂ§ÃƒÂ£o",
            ],
        ),
        (
            "Tipo de PrÃªmio",
            [
                "Tipo de PrÃªmio",
                "Tipo de PrÃƒÂªmio",
            ],
        ),
        (
            "Marco de serviÃ§o",
            [
                "Marco de serviÃ§o",
                "Marco de serviÃƒÂ§o",
            ],
        ),
        ("Trimestre", ["Trimestre"]),
    ]

    def process(self, df):

        result = select_and_rename_columns(
            df,
            self.COLUMN_SPECS,
        )
        result["ID"] = to_integer_series(
            result["ID"]
        )
        result["Data da NomeaÃ§Ã£o"] = to_date_series(
            result["Data da NomeaÃ§Ã£o"]
        )
        result["Report Month"] = current_report_month()
        return result
