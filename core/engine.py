class AutomationEngine:

    def __init__(self, automation):
        self.automation = automation

    def run(self, df):
        df = df.copy()
        df.columns = df.columns.astype(str).str.strip()

        for col in df.columns:
            df[col] = df[col].astype(str)

        return self.automation.process(df)