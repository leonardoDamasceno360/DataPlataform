def clean_columns(df):
    df.columns = df.columns.str.strip()
    return df


def remove_unnamed(df):
    return df.loc[:, ~df.columns.str.contains("^Unnamed")]