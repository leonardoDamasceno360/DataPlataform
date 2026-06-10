from runtime.core.schema_utils import sanitize_connect_type_columns


class AutomationEngine:

    def __init__(self, automation):
        self.automation = automation

    def run(self, df):
        df = df.copy()
        df.columns = df.columns.astype(str).str.strip()

        result = self.automation.process(df)
        return sanitize_connect_type_columns(result)
