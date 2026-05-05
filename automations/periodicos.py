class Periodicos:

    def process(self, df):

        # Normalização básica
        df = df.copy()
        df.columns = df.columns.astype(str).str.strip()

        # Função para encontrar colunas de forma flexível
        def find_column(df, name):
            for col in df.columns:
                if name.lower() in col.lower():
                    return col
            raise ValueError(f"Coluna parecida com '{name}' não encontrada")

        # Encontrar colunas dinamicamente
        id_col = find_column(df, "id")
        date_col = find_column(df, "expiration")
        status_col = find_column(df, "status")

        # Seleção final
        result = df[[id_col, date_col, status_col]].copy()

        # Renomear para padrão esperado
        result.columns = [
            "ID",
            "DATE EXPIRATION ASO",
            "STATUS ASO"
        ]

        return result