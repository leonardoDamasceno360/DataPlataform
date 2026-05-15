from datetime import datetime


class Speed:

    def process(self, df):

        df.columns = df.columns.str.strip()

        result = df[[
            "Employee Number",
            "Avaliação",
            "Current Appraisal Stage",
            "Manager Employee Number SPEED",
            "Manager Name Speed",
            "Reviewer Employee Number",
            "Reviewer Name",
            "Compliance"
        ]].copy()

        # Histórico mensal
        result["Report Month"] = datetime.today().strftime("%Y-%m")

        return result