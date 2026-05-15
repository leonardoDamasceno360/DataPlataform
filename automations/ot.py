from core.schema_utils import find_column

class OT:

    def process(self, df):

        id_col = find_column(
            df,
            [
                "ID",
                "Id"
            ]
        )

        date_col = find_column(
            df,
            [
                "DATE",
                "Date"
            ]
        )

        type_day_col = find_column(
            df,
            [
                "Type of Day",
                "Type Of Day",
                "TYPE OF DAY"
            ]
        )

        request_col = find_column(
            df,
            [
                "Last OT Request Status",
                "Last Ot Request Status"
            ]
        )

        total_ot_col = find_column(
            df,
            [
                "Total OT Hours Done",
                "Total Ot Hours Done"
            ]
        )

        classification_col = find_column(
            df,
            [
                "OT Classification",
                "Ot Classification"
            ]
        )

        compliance_col = find_column(
            df,
            [
                "OT Hours Compliance Classification",
                "Ot Hours Compliance Classification"
            ]
        )

        return df[[

            id_col,

            date_col,

            type_day_col,

            request_col,

            total_ot_col,

            classification_col,

            compliance_col
        ]]