import pandas as pd


DEFAULT_MAX_QUESTIONS = 6


def humanize_column_name(column_name: str) -> str:
    """
    Convert a technical column name into a readable label.

    Example:
        "units_sold" becomes "units sold"
    """
    return str(column_name).replace("_", " ").strip()


def is_likely_identifier(column_name: str) -> bool:
    """
    Determine whether a column name looks like an identifier.

    Identifier columns are usually unsuitable for averages,
    totals, or grouped business analysis.
    """
    normalized_name = str(column_name).strip().lower()

    return (
        normalized_name in {"id", "index", "row_number"}
        or normalized_name.endswith("_id")
        or normalized_name.startswith("id_")
    )


def get_numeric_analysis_columns(
    dataframe: pd.DataFrame,
) -> list[str]:
    """
    Return numeric columns that appear suitable for analysis.

    Obvious identifier columns are excluded.
    """
    numeric_columns = dataframe.select_dtypes(
        include="number"
    ).columns

    return [
        str(column_name)
        for column_name in numeric_columns
        if not is_likely_identifier(str(column_name))
    ]


def get_categorical_analysis_columns(
    dataframe: pd.DataFrame,
) -> list[str]:
    """
    Return categorical columns suitable for grouping.

    High-cardinality columns are excluded because grouping by
    nearly unique values is usually not useful.
    """
    categorical_dataframe = dataframe.select_dtypes(
        include=["object", "string", "category", "bool"]
    )

    total_rows = len(dataframe)
    maximum_unique_values = max(
        10,
        int(total_rows * 0.5),
    )

    suitable_columns = []

    for column_name in categorical_dataframe.columns:
        unique_count = categorical_dataframe[
            column_name
        ].nunique(dropna=True)

        if unique_count <= maximum_unique_values:
            suitable_columns.append(str(column_name))

    return suitable_columns


def suggest_analysis_questions(
    dataframe: pd.DataFrame,
    max_questions: int = DEFAULT_MAX_QUESTIONS,
) -> list[str]:
    """
    Generate deterministic analysis questions from a dataset schema.

    Args:
        dataframe: Dataset used to create suggestions.
        max_questions: Maximum number of questions to return.

    Returns:
        A list of unique suggested questions.

    Raises:
        ValueError: If max_questions is less than one.
    """
    if max_questions < 1:
        raise ValueError(
            "Maximum question count must be at least 1."
        )

    numeric_columns = get_numeric_analysis_columns(
        dataframe
    )

    categorical_columns = get_categorical_analysis_columns(
        dataframe
    )

    suggestions: list[str] = []

    def add_question(question: str) -> None:
        if (
            question not in suggestions
            and len(suggestions) < max_questions
        ):
            suggestions.append(question)

    for column_name in numeric_columns[:2]:
        readable_name = humanize_column_name(column_name)

        add_question(
            f"What is the average {readable_name}?"
        )

        add_question(
            f"What is the total {readable_name}?"
        )

    if numeric_columns and categorical_columns:
        numeric_name = humanize_column_name(
            numeric_columns[0]
        )

        categorical_name = humanize_column_name(
            categorical_columns[0]
        )

        add_question(
            f"How does average {numeric_name} "
            f"compare across {categorical_name}?"
        )

    for column_name in categorical_columns[:2]:
        readable_name = humanize_column_name(column_name)

        add_question(
            f"What are the most common values in "
            f"{readable_name}?"
        )

    if len(numeric_columns) >= 2:
        first_name = humanize_column_name(
            numeric_columns[0]
        )

        second_name = humanize_column_name(
            numeric_columns[1]
        )

        add_question(
            f"Is there a relationship between "
            f"{first_name} and {second_name}?"
        )

    if not suggestions:
        add_question(
            "How many rows and columns are in the dataset?"
        )

        add_question(
            "Which columns contain missing values?"
        )

    return suggestions
