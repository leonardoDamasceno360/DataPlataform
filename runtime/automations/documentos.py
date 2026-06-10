# =========================================================
# automations/documentos.py
# =========================================================

import pandas as pd
from runtime.core.schema_utils import current_report_month


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

        df["Report Month"] = current_report_month()

        return df.reset_index(drop=True)
