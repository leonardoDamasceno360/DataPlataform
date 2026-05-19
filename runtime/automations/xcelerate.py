from datetime import datetime


class Xcelerate:

    def process(self, df):

        df.columns = df.columns.str.strip()

        result = df[[
            "ID",
            "Status"
        ]].copy()

        # Histórico mensal
        result["Report Month"] = datetime.today().strftime("%Y-%m")

        return result