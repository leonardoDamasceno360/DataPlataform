import numpy as np

from runtime.core.schema_utils import (
    current_report_month,
    normalize_text,
    select_and_rename_columns,
)


class QuadroGeral:

    SINDICATO_MAP = {
        "sindpd sp sind trab emp proc dados est sp": "SP",
        "sindpd rj sind trab emp e serv pub e priv de inf internet e sim rj": "RJ",
        "nenhum": "Other",
        "sintinorp londrina sind trab empr cursos inf con s i d p a bco dados m": "Londrina",
        "sindpd df sind dos trab em empr e orgaos publ proc dados s i s do df": "Other",
        "sindados mg sind dos empreg emp de proc dados serv de info simil mg": "Other",
        "sindpd ma sind dos empregados proc dados no est do maranhao": "Other",
        "sindpd pa sind trabalhadoras e trabalhadores em tecn informacao para": "Other",
        "sindpd pa sind trabalhadores e trabalhadoras em tecn informacao para": "Other",
        "sindpd es sind empreg emp proc dados e trab em inform do est es": "Other",
        "sppd ms sind profissionais de proc de dados e tec informacao de ms": "Other",
        "sindpd pr sind dos trab em empr de processamento do estado do parana": "Other",
        "sindpd pe sind trab em proc de dados informat tecn da inform do pe": "Other",
        "sindpd rs sind dos trabalhadores em processamento de dados no est rs": "Other",
        "sindpd joinville sind empreg em empr proc dados inform simil joinv": "Other",
        "sitepd sind dos trab empr priv de proc de dados de curitiba e regiao": "Other",
        "sindados ba sind trab empr e orgaos publ proc dados s i ti com ba": "Other",
    }

    COLUMN_SPECS = [
        ("Id Contratado", ["Id Contratado"]),
        ("Nome Completo", ["Nome Completo"]),
        ("Modelo de Folha", ["Modelo de Folha"]),
        ("Data da Admissão", ["Data da Admissão", "Data da AdmissÃ£o", "Data da AdmissÃƒÆ’Ã‚Â£o"]),
        ("Data da Rescisão", ["Data da Rescisão", "Data da RescisÃ£o", "Data da RescisÃƒÆ’Ã‚Â£o"]),
        ("Cargo", ["Cargo"]),
        (
            "Quantidade de Horas no Mês",
            [
                "Quantidade de Horas no Mês",
                "Quantidade de Horas no MÃªs",
                "Quantidade de Horas no MÃƒÆ’Ã‚Âªs",
            ],
        ),
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
        ("Situação", ["Situação", "SituaÃ§Ã£o", "SituaÃƒÆ’Ã‚Â§ÃƒÆ’Ã‚Â£o"]),
        (
            "Código Flexível Contratado 9",
            [
                "Código Flexível Contratado 9",
                "CÃ³digo FlexÃ­vel Contratado 9",
                "CÃƒÆ’Ã‚Â³digo FlexÃƒÆ’Ã‚Â­vel Contratado 9",
            ],
        ),
        ("Nome Grade", ["Nome Grade"]),
        ("É PCD?", ["É PCD?", "Ã‰ PCD?", "ÃƒÆ’Ã¢â‚¬Â° PCD?", "E PCD?", "PCD?"]),
        (
            "Tipo de Deficiência",
            ["Tipo de Deficiência", "Tipo de DeficiÃªncia", "Tipo de DeficiÃƒÆ’Ã‚Âªncia"],
        ),
    ]

    def process(self, df):

        df = select_and_rename_columns(
            df,
            self.COLUMN_SPECS,
        )
        raw_status_by_row = (
            df["Situação"].copy()
            if "Situação" in df.columns
            else None
        )

        if "Segment HEAD" in df.columns:
            df["Segment HEAD"] = df["Segment HEAD"].replace(
                {
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
                    np.nan: "ESU",
                }
            )

        if "Horizontal Line" in df.columns:
            df["Horizontal Line"] = df["Horizontal Line"].replace(
                {
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
                    np.nan: "Other",
                }
            )

        if "Sindicato" in df.columns:
            df["Sindicato"] = df["Sindicato"].apply(
                self._map_sindicato_value
            )

        if "Situação" in df.columns:
            df["Situação"] = df["Situação"].replace(
                {
                    "Demitido em Meses Anteriores": "Separated",
                    "Demitido no Mês": "Separated",
                    "Em Atividade Normal": "Active",
                    "Gozando Férias": "Active",
                    "Auxílio-Doença": "Afastado",
                    "Suspensão Contratual (Art. 476-A da CLT)": "Afastado",
                    "Licença-Maternidade": "Afastado",
                    "Afastado sem Remuneração": "Afastado",
                    "Afastado por Aposentadoria Invalidez": "Afastado",
                    "Afastado Pré-Auxílio-Doença": "Afastado",
                }
            )

        df["PCD Cota?"] = df.apply(
            lambda row: self._build_pcd_cota(
                row,
                raw_status_by_row,
            ),
            axis=1,
        )
        df["Modalidade de Trabalho"] = df.apply(
            self._build_work_mode,
            axis=1,
        )
        df["Report Month"] = current_report_month()

        return df

    @staticmethod
    def _build_pcd_cota(row, raw_status_by_row):

        raw_status = ""
        if raw_status_by_row is not None:
            raw_status = raw_status_by_row.iloc[row.name]

        status_value = normalize_text(raw_status)
        role_value = normalize_text(row.get("Cargo", ""))

        if status_value == "afastado por aposentadoria invalidez":
            return "N"

        if "estagiario" in role_value or "aprendiz" in role_value:
            return "N"

        return "S"

    @staticmethod
    def _build_work_mode(row):

        sindicato_value = normalize_text(
            row.get("Sindicato", "")
        )

        if sindicato_value == "londrina":
            return "Presencial"

        if sindicato_value in {"sp", "sao paulo"}:
            return "Híbrido"

        return "Remoto"

    @classmethod
    def _map_sindicato_value(cls, value):

        normalized_value = normalize_text(value)

        if normalized_value in cls.SINDICATO_MAP:
            return cls.SINDICATO_MAP[normalized_value]

        return value
