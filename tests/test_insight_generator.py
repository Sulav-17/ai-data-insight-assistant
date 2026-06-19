import pandas as pd

from src.analyzer import AnalysisResult
from src.insight_generator import (
    generate_business_insight,
)


def test_scalar_insight_uses_verified_value() -> None:
    result = AnalysisResult(
        operation="mean",
        result_type="scalar",
        title="Average revenue",
        scalar_value=309.955,
    )

    insight = generate_business_insight(result)

    assert "309.95" in insight
    assert "average revenue" in insight.lower()


def test_dataset_shape_insight() -> None:
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

    insight = generate_business_insight(result)

    assert "12 rows" in insight
    assert "9 columns" in insight


def test_grouped_insight_identifies_highest_and_lowest() -> None:
    result = AnalysisResult(
        operation="grouped_mean",
        result_type="table",
        title="Average revenue by region",
        table=pd.DataFrame(
            {
                "region": ["East", "West"],
                "average_revenue": [313.30, 294.93],
                "non_null_count": [3, 2],
            }
        ),
    )

    insight = generate_business_insight(result)

    assert "'East' has the highest" in insight
    assert "'West' has the lowest" in insight
    assert "does not establish why" in insight


def test_most_common_insight_uses_count_and_percentage() -> None:
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

    insight = generate_business_insight(result)

    assert "Accessories" in insight
    assert "7 times" in insight
    assert "58.33%" in insight