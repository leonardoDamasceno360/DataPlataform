from datetime import datetime

from runtime.core.schema_utils import find_column


class Periodicos:
    def process(self, df):
        df = df.copy()
        df.columns = df.columns.astype(str).str.strip()

        id_col = find_column(
            df,
            ["id", "employee id", "associate id", "matricula"],
        )
        date_col = find_column(
            df,
            [
                "date expiration aso",
                "expiration",
                "expiration date",
                "validity",
                "due date",
            ],
        )
        status_col = find_column(df, ["status aso", "status"])

        result = df[[id_col, date_col, status_col]].copy()
        result.columns = ["ID", "DATE EXPIRATION ASO", "STATUS ASO"]
        result["Report Month"] = datetime.today().strftime("%Y-%m")
        return result
