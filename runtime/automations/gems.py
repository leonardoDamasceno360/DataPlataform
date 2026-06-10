from runtime.core.schema_utils import (
    current_report_month,
    select_and_rename_columns,
)


class Gems:

    COLUMN_SPECS = [
        ("ID", ["ID"]),
        ("Nomeador", ["Nomeador"]),
        ("Data da Nomeação", ["Data da Nomeação", "Data da NomeaÃ§Ã£o"]),
        ("Premiação", ["Premiação", "PremiaÃ§Ã£o"]),
        ("Tipo de Prêmio", ["Tipo de Prêmio", "Tipo de PrÃªmio"]),
        ("Marco de serviço", ["Marco de serviço", "Marco de serviÃ§o"]),
        ("Trimestre", ["Trimestre"]),
    ]

    def process(self, df):

        result = select_and_rename_columns(
            df,
            self.COLUMN_SPECS,
        )
        result["Report Month"] = current_report_month()
        return result
