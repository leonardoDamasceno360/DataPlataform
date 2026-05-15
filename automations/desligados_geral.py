import pandas as pd
from datetime import datetime


class DesligadosGeral:

    def process(self, df):

        df = df.copy()

        df.columns = df.columns.str.strip()

        result = df[[

            "Id Contratado",

            "SEPARATION REASON",

            "CATEGORY"

        ]].copy()

        result["Report Month"] = (
            datetime.today().strftime("%Y-%m")
        )

        return result