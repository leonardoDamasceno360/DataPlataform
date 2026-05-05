import pandas as pd
import unicodedata


class IBelong:

    TARGET_COLUMNS = [
        "New Joinee emp id",
        "Total feedback questions triggered",
        "Total feedback questions answered",
        "ASI",
        "Feedback Compliance (%)",
        "Suggestions to improve candidate  joining experience from offer acceptance to joining date",
        "I was given necessary information on background check process, joining documentation process and Day 1 plan before joining TCS.",
        "I found the Onboarding Manager approachable and responsive.",
        "My first day in TCS was",
        "My role and job responsibilities have been explained to me by my manager",
        "My job responsiblities are in line with the expectations set during the recruitment process",
        "My manager or a designated member of the team has connected me to the people I need to know to function in my role",
        "My first month in TCS was",
        "My Immediate Manager connects with me on a regular basis.",
        "My HR team has made me aware of the TCS connect platforms (townhalls etc) I can participate in and contribute to",
        "My HR team has made me aware of the fit4life, engagement, and community activities that I can participate.",
        "My first quarter in TCS was",
        "I felt it useful to have a Buddy.",
        "My buddy was available when I needed help.",
        "I would like to be a Buddy for future new joiners.",
        "My HR has connected with me regularly in the first three months.",
        "My Immediate Manager has given me feedback on my progress in the first six months.",
        "I will recommend TCS to my friends.",
        "I know how to succeed in my role and TCS.",
        "My Immediate Manager has given me feedback on my overall progress in the first year.",
        "My HR has connected with me regularly throughout the first year.",
        "I had discussions on my career aspirations with my Manager.",
        "I feel very much a part of TCS.",
        "Please rate your overall experience with the iBELONG Programme.",
        "How useful was the induction module on your local geography?",
        "How useful was the content in the 'Know Your Customer' module?",
        "How useful was the content in the 'Know Your Project' module?",
        "How did you find the initial induction session?",
        "How did you find the second induction session?",
        "How useful was the induction module on your business or functional unit?",
        "I had discussions on my role-related training requirements with my Manager.",
        "My manager or a designated member of the team has oriented me about the Customer(s)/ Function(s)/ Project(s) that I am a part of"
    ]

    def process(self, df: pd.DataFrame) -> pd.DataFrame:

        raw = df.copy()

        # -------------------------
        # DETECTAR HEADER
        # -------------------------
        header_idx = None

        for i in range(len(raw)):
            row = raw.iloc[i].astype(str).str.lower()
            if row.str.contains("new joinee emp id", na=False).any():
                header_idx = i
                break

        if header_idx is None:
            raise ValueError("Header não encontrado")

        # -------------------------
        # RECONSTRUIR DATAFRAME
        # -------------------------
        header = raw.iloc[header_idx].astype(str).str.replace("\n", " ").str.strip()

        df = raw.iloc[header_idx + 1:].reset_index(drop=True)
        df.columns = header

        df.columns = df.columns.astype(str).str.strip()
        df = df.loc[:, ~df.columns.str.contains("^Unnamed", na=False)]

        # -------------------------
        # NORMALIZAÇÃO
        # -------------------------
        normalized_map = {
            self._normalize(col): col for col in df.columns
        }

        # -------------------------
        # CRIA FINAL_DF (ANTES DE USAR)
        # -------------------------
        final_df = pd.DataFrame(index=df.index)

        # -------------------------
        # MATCH DE COLUNAS
        # -------------------------
        for target in self.TARGET_COLUMNS:
            target_norm = self._normalize(target)

            matched_col = self._match_column(target_norm, normalized_map)

            final_df[target] = df[matched_col] if matched_col else pd.NA

        # -------------------------
        # LIMPEZA FINAL
        # -------------------------
        if "New Joinee emp id" in final_df.columns:
            final_df["New Joinee emp id"] = (
                final_df["New Joinee emp id"]
                .astype(str)
                .str.strip()
            )

            # remove linhas inválidas
            final_df = final_df[
                final_df["New Joinee emp id"].str.match(r"^\d+$", na=False)
            ]

        final_df = final_df.reset_index(drop=True)

        return self._convert_types(final_df)

    # -------------------------
    # HELPERS
    # -------------------------

    def _normalize(self, text):
        text = unicodedata.normalize("NFKD", str(text).lower().strip())
        return "".join(c for c in text if not unicodedata.combining(c))

    def _match_column(self, target_norm, normalized_map):

        best_match = None
        best_score = 0

        for norm, original in normalized_map.items():

            target_words = set(target_norm.split())
            norm_words = set(norm.split())

            score = len(target_words & norm_words)

            if score > best_score:
                best_score = score
                best_match = original

        return best_match if best_score >= 3 else None

    def _convert_types(self, df):

        for col in df.columns:
            col_lower = col.lower()

            if "asi" in col_lower or "compliance" in col_lower:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        return df