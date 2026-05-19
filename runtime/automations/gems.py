from datetime import datetime


class Gems:

    def process(self, df):

        df.columns = df.columns.str.strip()

        result = df[[
            "ID",
            "Nomeador",
            "Data da Nomeação",
            "Premiação",
            "Tipo de Prêmio",
            "Marco de serviço",
            "Trimestre"
        ]].copy()

        # Histórico mensal
        result["Report Month"] = datetime.today().strftime("%Y-%m")

        return result