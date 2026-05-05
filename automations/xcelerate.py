class Xcelerate:

    def process(self, df):
        df.columns = df.columns.str.strip()

        return df[[
            "ID",
            "Status"
        ]]