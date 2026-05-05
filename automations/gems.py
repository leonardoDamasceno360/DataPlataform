class Gems:

    def process(self, df):
        df.columns = df.columns.str.strip()

        return df[[
            "ID",
            "Nomeador",
            "Data da Nomeação",
            "Premiação",
            "Tipo de Prêmio",
            "Marco de serviço",
            "Trimestre"
        ]]