import plotly.express as px
from plotly.graph_objects import Figure

from src.analyzer import AnalysisResult


class ChartBuildError(ValueError):
    """Raised when an analysis result cannot produce a safe chart."""


def build_result_chart(
    analysis_result: AnalysisResult,
) -> Figure | None:
    """
    Build a Plotly chart from a verified analysis result.

    Charts are only created for explicitly supported table results.
    Scalar results and unsuitable tables return None.
    """
    result_table = analysis_result.table

    if (
        analysis_result.result_type != "table"
        or result_table is None
        or result_table.empty
    ):
        return None

    if analysis_result.operation == "grouped_mean":
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
            raise ChartBuildError(
                "The grouped result does not contain the "
                "columns required for a chart."
            )

        return px.bar(
            result_table,
            x=grouping_columns[0],
            y=average_columns[0],
            title=analysis_result.title,
            labels={
                grouping_columns[0]: str(
                    grouping_columns[0]
                ).replace("_", " ").title(),
                average_columns[0]: str(
                    average_columns[0]
                ).replace("_", " ").title(),
            },
        )

    if analysis_result.operation == "most_common":
        category_columns = [
            column_name
            for column_name in result_table.columns
            if column_name not in {"count", "percentage"}
        ]

        if not category_columns or "count" not in result_table.columns:
            raise ChartBuildError(
                "The frequency result does not contain the "
                "columns required for a chart."
            )

        category_column = category_columns[0]

        return px.bar(
            result_table,
            x=category_column,
            y="count",
            title=analysis_result.title,
            labels={
                category_column: str(
                    category_column
                ).replace("_", " ").title(),
                "count": "Count",
            },
        )

    if analysis_result.operation == "missing_columns":
        required_columns = {
            "column_name",
            "missing_count",
        }

        if not required_columns.issubset(result_table.columns):
            raise ChartBuildError(
                "The missing-value result does not contain "
                "the columns required for a chart."
            )

        return px.bar(
            result_table,
            x="column_name",
            y="missing_count",
            title="Missing values by column",
            labels={
                "column_name": "Column",
                "missing_count": "Missing values",
            },
        )

    return None