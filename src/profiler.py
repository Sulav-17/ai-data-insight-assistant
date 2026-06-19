import pandas as pd


MISSING_SUMMARY_COLUMNS = [
    "column_name",
    "missing_count",
    "missing_percentage",
]

NUMERIC_SUMMARY_COLUMNS = [
    "column_name",
    "count",
    "mean",
    "std",
    "min",
    "25%",
    "50%",
    "75%",
    "max",
]

CATEGORICAL_SUMMARY_COLUMNS = [
    "column_name",
    "non_null_count",
    "unique_count",
    "most_common_value",
    "most_common_count",
]


def build_missing_value_summary(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """
    Calculate missing-value counts and percentages for every column.

    Args:
        dataframe: The dataset to inspect.

    Returns:
        A DataFrame containing missing-value information.
    """
    total_rows = len(dataframe)
    missing_counts = dataframe.isna().sum()

    if total_rows == 0:
        missing_percentages = missing_counts.astype(float)
    else:
        missing_percentages = (
            missing_counts / total_rows * 100
        ).round(2)

    return pd.DataFrame(
        {
            "column_name": [
                str(column_name)
                for column_name in dataframe.columns
            ],
            "missing_count": missing_counts.astype(int).to_numpy(),
            "missing_percentage": missing_percentages.to_numpy(),
        },
        columns=MISSING_SUMMARY_COLUMNS,
    )


def count_duplicate_rows(dataframe: pd.DataFrame) -> int:
    """
    Count rows that duplicate an earlier row.

    Args:
        dataframe: The dataset to inspect.

    Returns:
        Number of duplicate rows.
    """
    return int(dataframe.duplicated().sum())


def build_numeric_summary(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """
    Build descriptive statistics for numeric columns.

    Args:
        dataframe: The dataset to inspect.

    Returns:
        A DataFrame containing numeric descriptive statistics.
    """
    numeric_dataframe = dataframe.select_dtypes(
        include="number"
    )

    if numeric_dataframe.empty:
        return pd.DataFrame(columns=NUMERIC_SUMMARY_COLUMNS)

    summary = (
        numeric_dataframe.describe()
        .transpose()
        .reset_index()
        .rename(columns={"index": "column_name"})
    )

    return summary[NUMERIC_SUMMARY_COLUMNS]


def build_categorical_summary(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """
    Build frequency summaries for categorical-style columns.

    Args:
        dataframe: The dataset to inspect.

    Returns:
        A DataFrame containing categorical summaries.
    """
    categorical_dataframe = dataframe.select_dtypes(
        include=["object", "string", "category", "bool"]
    )

    summary_records = []

    for column_name in categorical_dataframe.columns:
        column = categorical_dataframe[column_name]
        non_null_values = column.dropna()
        value_counts = non_null_values.value_counts()

        if value_counts.empty:
            most_common_value = None
            most_common_count = 0
        else:
            most_common_value = str(value_counts.index[0])
            most_common_count = int(value_counts.iloc[0])

        summary_records.append(
            {
                "column_name": str(column_name),
                "non_null_count": int(non_null_values.count()),
                "unique_count": int(non_null_values.nunique()),
                "most_common_value": most_common_value,
                "most_common_count": most_common_count,
            }
        )

    return pd.DataFrame(
        summary_records,
        columns=CATEGORICAL_SUMMARY_COLUMNS,
    )