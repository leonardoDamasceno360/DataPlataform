from runtime.core.schema_utils import select_and_rename_columns


class OT:

    COLUMN_SPECS = [
        ("ID", ["ID", "Id"]),
        ("DATE", ["DATE", "Date"]),
        ("Type of Day", ["Type of Day"]),
        (
            "Last OT Request Status",
            ["Last OT Request Status", "Last Ot Request Status"],
        ),
        (
            "Total OT Hours Done",
            ["Total OT Hours Done", "Total Ot Hours Done"],
        ),
        (
            "OT Classification",
            ["OT Classification", "Ot Classification"],
        ),
        (
            "OT Hours Compliance Classification",
            [
                "OT Hours Compliance Classification",
                "Ot Hours Compliance Classification",
            ],
        ),
    ]

    def process(self, df):

        return select_and_rename_columns(
            df,
            self.COLUMN_SPECS,
        )
