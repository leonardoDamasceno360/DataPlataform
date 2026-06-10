import numpy as np
from runtime.core.schema_utils import (
    current_report_month,
    select_and_rename_columns,
)


class QuadroGeral:

    SINDICATO_MAP = {
        "SINDPD/SP - SIND TRAB EMP PROC DADOS EST SP": "SP",
        "SINDPD/RJ - Sind Trab Emp e Serv Pub e Priv de Inf Internet e Sim RJ": "RJ",
        "Nenhum": "Other",
        "SINTINORP/Londrina-Sind Trab Empr Cursos Inf Con S I D P A Bco Dados M": "Londrina",
        "SINDPD/DF - Sind dos Trab em Empr e Órgãos Publ Proc Dados S I S do DF": "Other",
        "SINDADOS/MG - Sind dos Empreg Emp de Proc Dados, Serv de Info Simil MG": "Other",
        "SINDPD/MA - Sind dos Empregados Proc Dados no Est do Maranhão": "Other",
        "SINDPD/PA - Sind Trabalhadores e Trabalhadoras em Tecn Informação Pará": "Other",
        "SINDPD/ES - Sind Empreg Emp Proc Dados e Trab em Inform do Est ES": "Other",
        "SPPD/MS - Sind Profissionais de Proc de Dados e Tec Informação de MS": "Other",
        "SINDPD/PR - Sind dos Trab em Empr de Processamento do Estado do Paraná": "Other",
        "SINDPD/PE - Sind Trab em Proc de Dados, Informat Tecn da Inform do PE": "Other",
        "SINDPD/RS - Sind dos Trabalhadores em Processamento de Dados no Est RS": "Other",
        "SINDPD/JOINVILLE - Sind Empreg em Empr Proc Dados Inform Simil Joinv": "Other",
        "SITEPD - Sind dos Trab Empr Priv de Proc de Dados de Curitiba e Região": "Other",
        "SINDADOS/BA - Sind Trab Empr e Órgãos Publ Proc Dados S I TI Com BA": "Other",
    }

    COLUMN_SPECS = [
        ("Id Contratado", ["Id Contratado"]),
        ("Nome Completo", ["Nome Completo"]),
        ("Modelo de Folha", ["Modelo de Folha"]),
        ("Data da Admissão", ["Data da Admissão"]),
        ("Data da Rescisão", ["Data da Rescisão"]),
        ("Cargo", ["Cargo"]),
        ("Quantidade de Horas no Mês", ["Quantidade de Horas no Mês"]),
        ("Segment HEAD", ["Segment HEAD"]),
        ("Horizontal Line", ["Horizontal Line"]),
        ("GROUP CUSTOMER", ["GROUP CUSTOMER"]),
        ("Id Centro de Custo", ["Id Centro de Custo"]),
        ("Centro de Custo", ["Centro de Custo"]),
        ("ID Gestor", ["ID Gestor"]),
        ("Nome Gestor", ["Nome Gestor"]),
        ("Sexo", ["Sexo"]),
        ("Quantidade de Anos de Idade", ["Quantidade de Anos de Idade"]),
        ("Sindicato", ["Sindicato"]),
        ("Situação", ["Situação"]),
        ("Código Flexível Contratado 9", ["Código Flexível Contratado 9"]),
        ("Nome Grade", ["Nome Grade"]),
        ("É PCD?", ["É PCD?"]),
        ("Tipo de Deficiência", ["Tipo de Deficiência"]),
    ]

    def process(self, df):

        df = select_and_rename_columns(
            df,
            self.COLUMN_SPECS,
        )

        if "Segment HEAD" in df.columns:

            df["Segment HEAD"] = (
                df["Segment HEAD"]
                .replace({

                    "Krishna Shrivastava": "BFSI",
                    "Natacha Emicuri": "CBG & TSS",
                    "Bruno Folly CMI": "CMI",
                    "Jorge Banharo": "EnR",
                    "Ximena Jofre": "HR",
                    "Bruno Folly LSHC": "LSHC",
                    "Sol Besprosvan": "MFG",
                    "Ashok Kumar": "Nearshore",
                    "Ravi Sanker": "Utilities",
                    "NA": "Other",
                    "Cyril John K": "DIS",
                    "RMG": "Other",
                    "Bruno Rocha": "Other",
                    "Latesh Sewani": "Finance",
                    "Amol Wadikar": "Admin",
                    "Renzo Parodi": "Legal",
                    "V Sathya": "DEG",
                    "ESU": "ESU",
                    "Bruno Folly - ESU": "ESU",
                    "Dhanasekhar V": "ISM",
                    "Alma Leal": "Marketing",
                    "Nenhum": "Other",
                    "ILP": "Other",
                    "Pace Port": "Pace",
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

        if "Sindicato" in df.columns:

            df["Sindicato"] = (
                df["Sindicato"]
                .replace(self.SINDICATO_MAP)
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

        df["Report Month"] = current_report_month()

        return df
