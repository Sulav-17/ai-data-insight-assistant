import pandas as pd

from src.analyzer import AnalysisResult
from src.question_suggester import humanize_column_name


class InsightGenerationError(ValueError):
    """Raised when a verified result cannot be summarized safely."""


def format_number(value: int | float) -> str:
    """Format a numeric result for readable business text."""
    if isinstance(value, int):
        return f"{value:,}"

    return f"{value:,.2f}"


def generate_business_insight(
    analysis_result: AnalysisResult,
) -> str:
    """
    Generate a deterministic explanation from a verified result.

    The function summarizes observed values only. It does not
    make causal claims or invent business context.
    """
    if analysis_result.result_type == "scalar":
        if analysis_result.scalar_value is None:
            raise InsightGenerationError(
                "The scalar result does not contain a value."
            )

        return (
            f"Based on the complete uploaded dataset, "
            f"{analysis_result.title.lower()} is "
            f"{format_number(analysis_result.scalar_value)}."
        )

    result_table = analysis_result.table

    if result_table is None:
        raise InsightGenerationError(
            "The table result does not contain a table."
        )

    if analysis_result.operation == "dataset_shape":
        values = dict(
            zip(
                result_table["metric"],
                result_table["value"],
            )
        )

        return (
            f"The uploaded dataset contains "
            f"{int(values['Rows']):,} rows and "
            f"{int(values['Columns']):,} columns."
        )

    if analysis_result.operation == "missing_columns":
        if result_table.empty:
            return (
                "No missing values were detected in the "
                "uploaded dataset."
            )

        total_missing = int(
            result_table["missing_count"].sum()
        )

        most_affected_row = result_table.sort_values(
            "missing_count",
            ascending=False,
        ).iloc[0]

        affected_column = humanize_column_name(
            str(most_affected_row["column_name"])
        )

        affected_count = int(
            most_affected_row["missing_count"]
        )

        return (
            f"The dataset contains {total_missing:,} missing "
            f"cells across {len(result_table):,} columns. "
            f"The most affected column is '{affected_column}' "
            f"with {affected_count:,} missing values."
        )

    if analysis_result.operation == "grouped_mean":
        if result_table.empty:
            return (
                "The grouped analysis did not return "
                "any usable groups."
            )

        average_columns = [
            column_name
            for column_name in result_table.columns
            if str(column_name).startswith("average_")
        ]

        grouping_columns = [
            column_name
            for column_name in result_table.columns
            if column_name not in average_columns
            and column_name != "non_null_count"
        ]

        if not average_columns or not grouping_columns:
            raise InsightGenerationError(
                "The grouped result does not contain "
                "the expected columns."
            )

        average_column = average_columns[0]
        grouping_column = grouping_columns[0]

        usable_rows = result_table.dropna(
            subset=[average_column]
        )

        if usable_rows.empty:
            return (
                "The grouped analysis did not contain "
                "usable numeric averages."
            )

        highest_row = usable_rows.loc[
            usable_rows[average_column].idxmax()
        ]

        lowest_row = usable_rows.loc[
            usable_rows[average_column].idxmin()
        ]

        highest_value = float(
            highest_row[average_column]
        )

        lowest_value = float(
            lowest_row[average_column]
        )

        difference = highest_value - lowest_value

        return (
            f"'{highest_row[grouping_column]}' has the highest "
            f"group average at {highest_value:,.2f}, while "
            f"'{lowest_row[grouping_column]}' has the lowest "
            f"at {lowest_value:,.2f}. The observed difference "
            f"between them is {difference:,.2f}. This comparison "
            f"describes the dataset but does not establish why "
            f"the groups differ."
        )

    if analysis_result.operation == "most_common":
        if result_table.empty:
            return (
                "No categorical values were available "
                "for frequency analysis."
            )

        top_row = result_table.iloc[0]

        category_columns = [
            column_name
            for column_name in result_table.columns
            if column_name not in {"count", "percentage"}
        ]

        if not category_columns:
            raise InsightGenerationError(
                "The frequency result does not contain "
                "a category column."
            )

        category_column = category_columns[0]
        category_value = top_row[category_column]
        category_count = int(top_row["count"])
        percentage = float(top_row["percentage"])

        return (
            f"The most common value in "
            f"'{humanize_column_name(str(category_column))}' is "
            f"'{category_value}', appearing {category_count:,} "
            f"times and representing {percentage:,.2f}% of "
            f"the dataset rows."
        )

    raise InsightGenerationError(
        f"Operation '{analysis_result.operation}' does not "
        "currently support business insight generation."
    )