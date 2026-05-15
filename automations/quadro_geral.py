# =========================================================
# automations/quadro_geral.py
# =========================================================

import pandas as pd
import numpy as np
from datetime import datetime


class QuadroGeral:

    def process(self, df):

        df = df.copy()

        df.columns = df.columns.astype(str).str.strip()

        colunas_remover = (
            list(df.columns[2:24]) +
            list(df.columns[26:32]) +
            list(df.columns[33:35]) +
            list(df.columns[36:42]) +
            list(df.columns[44:49]) +
            list(df.columns[50:52]) +
            list(df.columns[56:64]) +
            list(df.columns[65:71]) +
            list(df.columns[75:77])
        )

        df = df.drop(
            colunas_remover,
            axis=1
        )

        if "Segment HEAD" in df.columns:

            df["Segment HEAD"] = (
                df["Segment HEAD"]
                .replace({

                    "Tushar Parikh": "BFSI",
                    "Sangram Sahoo": "CBG",
                    "Bruno Folly CMI": "CMI",
                    "Jorge Banharo": "EnR",
                    "Ximena Jofre": "HR",
                    "Bruno Folly LSHC": "LSHC",
                    "Sol Besprosvan": "MFG",
                    "Ashok Kumar": "Nearshore",
                    "Sabyasachi Chandra": "Utilities",

                    "NA": "ESU",
                    "Cyril John K": "ESU",
                    "RMG": "ESU",
                    "Bruno Rocha": "ESU",
                    "Latesh Sewani": "ESU",
                    "Amol Wadikar": "ESU",
                    "Renzo Parodi": "ESU",
                    "V Sathya": "ESU",
                    "ESU": "ESU",
                    "Bruno Folly - ESU": "ESU",
                    "Dhanasekhar V": "ESU",
                    "Alma Leal": "ESU",
                    "Nenhum": "ESU",
                    "ILP": "ESU",
                    "Pace Port": "ESU",
                    np.nan: "ESU"
                })
            )

        if "Horizontal Line" in df.columns:

            df["Horizontal Line"] = (
                df["Horizontal Line"]
                .replace({

                    "Business Process Services": "BPS",
                    "Enterprise Solutions": "ESU",

                    "NA": "Other",
                    "Application Development & Maint.": "Other",
                    "Application Development &amp; Maint.": "Other",
                    "Asset Leverage Solutions": "Other",
                    "Infrastructure Services": "Other",
                    "IoT & Digital Engineering": "Other",
                    "IoT &amp; Digital Engineering": "Other",
                    "Global Consulting Practice": "Other",
                    "Quality Engineering and Transformation": "Other",
                    "Cognitive Business Operation": "Other",
                    "Other": "Other",
                    "Nenhum": "Other",
                    "Data & Analytics": "Other",
                    "Data &amp; Analytics": "Other",
                    "Digital Interactive": "Other",
                    "Analytics & Insights": "Other",
                    "Analytics &amp; Insights": "Other",
                    "Amazon Web Services": "Other",
                    "Cyber Security": "Other",
                    "Google Business Unit": "Other",
                    "Microsoft Business Unit": "Other",
                    "Cloud Apps, Microservices & APIfication": "Other",
                    "AI Transformation": "Other",
                    np.nan: "Other"
                })
            )

        if "Situação" in df.columns:

            df["Situação"] = (
                df["Situação"]
                .replace({

                    "Demitido em Meses Anteriores": "Separated",
                    "Demitido no Mês": "Separated",

                    "Em Atividade Normal": "Active",
                    "Gozando Férias": "Active",

                    "Auxílio-Doença": "Afastado",
                    "Suspensão Contratual (Art. 476-A da CLT)": "Afastado",
                    "Licença-Maternidade": "Afastado",
                    "Afastado sem Remuneração": "Afastado",
                    "Afastado por Aposentadoria Invalidez": "Afastado",
                    "Afastado Pré-Auxílio-Doença": "Afastado"
                })
            )

        df["Report Month"] = (
            datetime.today().strftime("%Y-%m")
        )

        return df