import pandas as pd


DEFAULT_PREVIEW_ROWS = 5


def get_dataset_dimensions(dataframe: pd.DataFrame) -> tuple[int, int]:
    """
    Return the number of rows and columns in a DataFrame.

    Args:
        dataframe: The dataset to inspect.

    Returns:
        A tuple containing row count and column count.
    """
    row_count, column_count = dataframe.shape

    return int(row_count), int(column_count)


def get_dataset_preview(
    dataframe: pd.DataFrame,
    row_count: int = DEFAULT_PREVIEW_ROWS,
) -> pd.DataFrame:
    """
    Return the first rows of a dataset.

    Args:
        dataframe: The dataset to preview.
        row_count: Maximum number of rows to return.

    Returns:
        A copy containing the requested first rows.

    Raises:
        ValueError: If row_count is less than one.
    """
    if row_count < 1:
        raise ValueError("Preview row count must be at least 1.")

    return dataframe.head(row_count).copy()


def build_schema_summary(dataframe: pd.DataFrame) -> pd.DataFrame:
    """
    Build a summary containing every column name and Pandas data type.

    Args:
        dataframe: The dataset whose schema will be inspected.

    Returns:
        A DataFrame containing column positions, names, and data types.
    """
    schema_records = []

    for position, column_name in enumerate(dataframe.columns, start=1):
        schema_records.append(
            {
                "position": position,
                "column_name": str(column_name),
                "data_type": str(dataframe[column_name].dtype),
            }
        )

    return pd.DataFrame(schema_records)