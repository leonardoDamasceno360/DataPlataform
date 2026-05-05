class Speed:

    def process(self, df):
        df.columns = df.columns.str.strip()

        return df[[
            "Employee Number",
            "Avaliação",
            "Current Appraisal Stage",
            "Manager Employee Number SPEED",
            "Manager Name Speed",
            "Reviewer Employee Number",
            "Reviewer Name",
            "Compliance"
        ]]