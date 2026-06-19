from dataclasses import dataclass

import pandas as pd
from pandas.api.types import is_numeric_dtype

from src.analysis_planner import AnalysisPlan
from src.question_suggester import humanize_column_name


class AnalysisExecutionError(ValueError):
    """Raised when a safe analysis plan cannot be executed."""


@dataclass
class AnalysisResult:
    """Structured result produced by an approved analysis operation."""

    operation: str
    result_type: str
    title: str
    scalar_value: int | float | None = None
    table: pd.DataFrame | None = None


ALLOWED_OPERATIONS = {
    "dataset_shape",
    "missing_columns",
    "mean",
    "sum",
    "min",
    "max",
    "grouped_mean",
    "most_common",
}

MOST_COMMON_LIMIT = 10


def _require_existing_column(
    dataframe: pd.DataFrame,
    column_name: str | None,
) -> str:
    """Confirm that a required column exists in the DataFrame."""
    if column_name is None:
        raise AnalysisExecutionError(
            "The analysis plan is missing a required column."
        )

    if column_name not in dataframe.columns:
        raise AnalysisExecutionError(
            f"Column '{column_name}' does not exist in the dataset."
        )

    return column_name


def _require_numeric_column(
    dataframe: pd.DataFrame,
    column_name: str | None,
) -> str:
    """Confirm that a required column exists and is numeric."""
    validated_column = _require_existing_column(
        dataframe,
        column_name,
    )

    if not is_numeric_dtype(dataframe[validated_column]):
        raise AnalysisExecutionError(
            f"Column '{validated_column}' is not numeric."
        )

    return validated_column


def _convert_number(
    value: object,
    column_name: str,
) -> int | float:
    """
    Convert a Pandas or NumPy number into a standard Python number.

    Raises an error when the calculation produced no usable result.
    """
    if pd.isna(value):
        raise AnalysisExecutionError(
            f"Column '{column_name}' contains no usable "
            "numeric values for this calculation."
        )

    if hasattr(value, "item"):
        value = value.item()

    if isinstance(value, bool):
        raise AnalysisExecutionError(
            "Boolean results are not supported as numeric results."
        )

    if isinstance(value, int):
        return value

    return float(value)


def _execute_numeric_operation(
    plan: AnalysisPlan,
    dataframe: pd.DataFrame,
) -> AnalysisResult:
    """Execute an approved single-column numeric calculation."""
    target_column = _require_numeric_column(
        dataframe,
        plan.target_column,
    )

    series = dataframe[target_column]
    readable_name = humanize_column_name(target_column)

    if plan.operation == "mean":
        value = series.mean()
        title = f"Average {readable_name}"

    elif plan.operation == "sum":
        value = series.sum(min_count=1)
        title = f"Total {readable_name}"

    elif plan.operation == "min":
        value = series.min()
        title = f"Minimum {readable_name}"

    elif plan.operation == "max":
        value = series.max()
        title = f"Maximum {readable_name}"

    else:
        raise AnalysisExecutionError(
            f"Numeric operation '{plan.operation}' is not permitted."
        )

    return AnalysisResult(
        operation=plan.operation,
        result_type="scalar",
        title=title,
        scalar_value=_convert_number(
            value,
            target_column,
        ),
    )


def _execute_grouped_mean(
    plan: AnalysisPlan,
    dataframe: pd.DataFrame,
) -> AnalysisResult:
    """Calculate a numeric average for each categorical group."""
    target_column = _require_numeric_column(
        dataframe,
        plan.target_column,
    )

    group_by = _require_existing_column(
        dataframe,
        plan.group_by,
    )

    if is_numeric_dtype(dataframe[group_by]):
        raise AnalysisExecutionError(
            f"Grouping column '{group_by}' is numeric and is "
            "not currently permitted for categorical grouping."
        )

    result_table = (
        dataframe.groupby(
            group_by,
            dropna=False,
        )[target_column]
        .agg(["mean", "count"])
        .reset_index()
        .rename(
            columns={
                "mean": f"average_{target_column}",
                "count": "non_null_count",
            }
        )
    )

    if result_table.empty:
        raise AnalysisExecutionError(
            "The grouped analysis produced no results."
        )

    result_table[group_by] = (
        result_table[group_by]
        .astype("object")
        .where(
            result_table[group_by].notna(),
            "(Missing)",
        )
    )

    return AnalysisResult(
        operation=plan.operation,
        result_type="table",
        title=(
            f"Average {humanize_column_name(target_column)} "
            f"by {humanize_column_name(group_by)}"
        ),
        table=result_table,
    )


def _execute_most_common(
    plan: AnalysisPlan,
    dataframe: pd.DataFrame,
) -> AnalysisResult:
    """Return the most frequent values in a categorical column."""
    target_column = _require_existing_column(
        dataframe,
        plan.target_column,
    )

    if is_numeric_dtype(dataframe[target_column]):
        raise AnalysisExecutionError(
            f"Column '{target_column}' is numeric and cannot "
            "currently be used for categorical frequency analysis."
        )

    display_values = (
        dataframe[target_column]
        .astype("object")
        .where(
            dataframe[target_column].notna(),
            "(Missing)",
        )
    )

    result_table = (
        display_values.value_counts(dropna=False)
        .head(MOST_COMMON_LIMIT)
        .rename_axis(target_column)
        .reset_index(name="count")
    )

    total_rows = len(dataframe)

    if total_rows > 0:
        result_table["percentage"] = (
            result_table["count"] / total_rows * 100
        ).round(2)

    else:
        result_table["percentage"] = 0.0

    return AnalysisResult(
        operation=plan.operation,
        result_type="table",
        title=(
            f"Most common values in "
            f"{humanize_column_name(target_column)}"
        ),
        table=result_table,
    )


def _execute_dataset_shape(
    dataframe: pd.DataFrame,
) -> AnalysisResult:
    """Return the complete dataset's row and column counts."""
    result_table = pd.DataFrame(
        [
            {
                "metric": "Rows",
                "value": int(len(dataframe)),
            },
            {
                "metric": "Columns",
                "value": int(len(dataframe.columns)),
            },
        ]
    )

    return AnalysisResult(
        operation="dataset_shape",
        result_type="table",
        title="Dataset dimensions",
        table=result_table,
    )


def _execute_missing_columns(
    dataframe: pd.DataFrame,
) -> AnalysisResult:
    """Return columns containing one or more missing values."""
    missing_counts = dataframe.isna().sum()
    affected_columns = missing_counts[missing_counts > 0]

    result_table = pd.DataFrame(
        {
            "column_name": affected_columns.index.astype(str),
            "missing_count": affected_columns.astype(int).to_numpy(),
        }
    )

    if not result_table.empty:
        result_table["missing_percentage"] = (
            result_table["missing_count"]
            / len(dataframe)
            * 100
        ).round(2)

    else:
        result_table["missing_percentage"] = pd.Series(
            dtype=float
        )

    return AnalysisResult(
        operation="missing_columns",
        result_type="table",
        title="Columns with missing values",
        table=result_table,
    )


def execute_analysis_plan(
    plan: AnalysisPlan,
    dataframe: pd.DataFrame,
) -> AnalysisResult:
    """
    Execute a validated analysis plan using approved Pandas logic.

    No generated code, eval, or exec operations are used.
    """
    if plan.operation not in ALLOWED_OPERATIONS:
        raise AnalysisExecutionError(
            f"Operation '{plan.operation}' is not permitted."
        )

    if plan.operation in {"mean", "sum", "min", "max"}:
        return _execute_numeric_operation(
            plan,
            dataframe,
        )

    if plan.operation == "grouped_mean":
        return _execute_grouped_mean(
            plan,
            dataframe,
        )

    if plan.operation == "most_common":
        return _execute_most_common(
            plan,
            dataframe,
        )

    if plan.operation == "dataset_shape":
        return _execute_dataset_shape(dataframe)

    if plan.operation == "missing_columns":
        return _execute_missing_columns(dataframe)

    raise AnalysisExecutionError(
        f"Operation '{plan.operation}' could not be executed."
    )