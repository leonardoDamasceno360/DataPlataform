# =========================================================
# automations/documentos.py
# =========================================================

import pandas as pd
from datetime import datetime


class Documentos:

    def process(self, df):

        df = df.copy()

        df.columns = df.columns.astype(str).str.strip()

        colunas_remover = (
            list(df.columns[1:10]) +
            list(df.columns[12:15])
        )

        df = df.drop(
            colunas_remover,
            axis=1
        )

        if "Status da Assinatura Digital do Documento" in df.columns:

            df = df[
                df[
                    "Status da Assinatura Digital do Documento"
                ]
                .astype(str)
                .str.contains(
                    "Pendente",
                    case=False,
                    na=False
                )
            ]

        df["Report Month"] = (
            datetime.today().strftime("%Y-%m")
        )

        return df.reset_index(drop=True)