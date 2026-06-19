from dataclasses import dataclass

import pandas as pd
from pandas.api.types import is_numeric_dtype

from src.question_parser import ParsedQuestion


class AnalysisPlanError(ValueError):
    """Raised when a parsed question cannot form a safe plan."""


@dataclass(frozen=True)
class AnalysisPlan:
    """Validated instructions for a controlled analysis operation."""

    operation: str
    target_column: str | None
    group_by: str | None
    description: str


NUMERIC_OPERATIONS = {
    "mean",
    "sum",
    "min",
    "max",
}


def _require_existing_column(
    dataframe: pd.DataFrame,
    column_name: str | None,
    role: str,
) -> str:
    """Confirm that a required column exists."""
    if column_name is None:
        raise AnalysisPlanError(
            f"The {role} column was not provided."
        )

    if column_name not in dataframe.columns:
        raise AnalysisPlanError(
            f"The {role} column '{column_name}' "
            "does not exist in the dataset."
        )

    return column_name


def _require_numeric_column(
    dataframe: pd.DataFrame,
    column_name: str | None,
) -> str:
    """Confirm that a target column exists and is numeric."""
    validated_column = _require_existing_column(
        dataframe,
        column_name,
        role="target",
    )

    if not is_numeric_dtype(
        dataframe[validated_column]
    ):
        raise AnalysisPlanError(
            f"Column '{validated_column}' is not numeric "
            "and cannot be used for this calculation."
        )

    return validated_column


def _require_categorical_column(
    dataframe: pd.DataFrame,
    column_name: str | None,
) -> str:
    """Confirm that a column is suitable for categorical analysis."""
    validated_column = _require_existing_column(
        dataframe,
        column_name,
        role="grouping",
    )

    if is_numeric_dtype(
        dataframe[validated_column]
    ):
        raise AnalysisPlanError(
            f"Column '{validated_column}' is numeric and "
            "cannot currently be used as a category."
        )

    return validated_column


def build_analysis_plan(
    parsed_question: ParsedQuestion,
    dataframe: pd.DataFrame,
) -> AnalysisPlan:
    """
    Convert a parsed question into a validated analysis plan.

    The function only permits explicitly approved operations.
    """
    operation = parsed_question.operation

    if operation == "dataset_shape":
        return AnalysisPlan(
            operation=operation,
            target_column=None,
            group_by=None,
            description=(
                "Count the complete dataset's rows and columns."
            ),
        )

    if operation == "missing_columns":
        return AnalysisPlan(
            operation=operation,
            target_column=None,
            group_by=None,
            description=(
                "Identify columns containing one or more "
                "missing values."
            ),
        )

    if operation in NUMERIC_OPERATIONS:
        target_column = _require_numeric_column(
            dataframe,
            parsed_question.target_column,
        )

        descriptions = {
            "mean": (
                f"Calculate the average of '{target_column}', "
                "excluding missing values."
            ),
            "sum": (
                f"Calculate the total of '{target_column}', "
                "excluding missing values."
            ),
            "min": (
                f"Find the minimum value in '{target_column}'."
            ),
            "max": (
                f"Find the maximum value in '{target_column}'."
            ),
        }

        return AnalysisPlan(
            operation=operation,
            target_column=target_column,
            group_by=None,
            description=descriptions[operation],
        )

    if operation == "grouped_mean":
        target_column = _require_numeric_column(
            dataframe,
            parsed_question.target_column,
        )

        group_by = _require_categorical_column(
            dataframe,
            parsed_question.group_by,
        )

        return AnalysisPlan(
            operation=operation,
            target_column=target_column,
            group_by=group_by,
            description=(
                f"Group the dataset by '{group_by}' and calculate "
                f"the average '{target_column}' for each group."
            ),
        )

    if operation == "most_common":
        target_column = _require_categorical_column(
            dataframe,
            parsed_question.target_column,
        )

        return AnalysisPlan(
            operation=operation,
            target_column=target_column,
            group_by=None,
            description=(
                f"Count values in '{target_column}' and return "
                "the most frequent categories."
            ),
        )

    raise AnalysisPlanError(
        f"Operation '{operation}' is not permitted."
    )