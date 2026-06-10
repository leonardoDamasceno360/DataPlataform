from runtime.core.schema_utils import (
    current_report_month,
    select_and_rename_columns,
)


class Speed:

    COLUMN_SPECS = [
        ("Employee Number", ["Employee Number"]),
        ("Avaliação", ["Avaliação", "Avaliacao", "AvaliaÃ§Ã£o"]),
        ("Current Appraisal Stage", ["Current Appraisal Stage"]),
        (
            "Manager Employee Number SPEED",
            ["Manager Employee Number SPEED"],
        ),
        ("Manager Name Speed", ["Manager Name Speed"]),
        ("Reviewer Employee Number", ["Reviewer Employee Number"]),
        ("Reviewer Name", ["Reviewer Name"]),
        ("Compliance", ["Compliance"]),
    ]

    def process(self, df):

        result = select_and_rename_columns(
            df,
            self.COLUMN_SPECS,
        )
        result["Report Month"] = current_report_month()
        return result
