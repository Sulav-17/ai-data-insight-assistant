import pandas as pd

from src.analyzer import AnalysisResult
from src.charts import build_result_chart


def test_grouped_mean_builds_bar_chart() -> None:
    result = AnalysisResult(
        operation="grouped_mean",
        result_type="table",
        title="Average revenue by region",
        table=pd.DataFrame(
            {
                "region": ["East", "West"],
                "average_revenue": [300.0, 250.0],
                "non_null_count": [3, 2],
            }
        ),
    )

    figure = build_result_chart(result)

    assert figure is not None
    assert figure.data[0].type == "bar"


def test_most_common_builds_bar_chart() -> None:
    result = AnalysisResult(
        operation="most_common",
        result_type="table",
        title="Most common categories",
        table=pd.DataFrame(
            {
                "category": ["Accessories", "Electronics"],
                "count": [7, 5],
                "percentage": [58.33, 41.67],
            }
        ),
    )

    figure = build_result_chart(result)

    assert figure is not None
    assert figure.data[0].type == "bar"


def test_scalar_result_does_not_build_chart() -> None:
    result = AnalysisResult(
        operation="mean",
        result_type="scalar",
        title="Average revenue",
        scalar_value=309.955,
    )

    figure = build_result_chart(result)

    assert figure is None


def test_dataset_shape_does_not_build_chart() -> None:
    result = AnalysisResult(
        operation="dataset_shape",
        result_type="table",
        title="Dataset dimensions",
        table=pd.DataFrame(
            {
                "metric": ["Rows", "Columns"],
                "value": [12, 9],
            }
        ),
    )

    figure = build_result_chart(result)

    assert figure is None