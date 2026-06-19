from pathlib import Path

import pandas as pd
import pytest

from src.data_loader import load_csv
from src.profiler import (
    build_categorical_summary,
    build_missing_value_summary,
    build_numeric_summary,
    count_duplicate_rows,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SAMPLE_CSV_PATH = PROJECT_ROOT / "sample_data" / "sales_sample.csv"


@pytest.fixture
def sample_dataframe() -> pd.DataFrame:
    """Load the sample dataset for profiling tests."""
    return load_csv(SAMPLE_CSV_PATH)


def test_missing_summary_contains_every_column(
    sample_dataframe: pd.DataFrame,
) -> None:
    """Every dataset column should appear in the missing summary."""
    summary = build_missing_value_summary(sample_dataframe)

    assert len(summary) == len(sample_dataframe.columns)

    assert list(summary.columns) == [
        "column_name",
        "missing_count",
        "missing_percentage",
    ]


def test_missing_summary_counts_region_values(
    sample_dataframe: pd.DataFrame,
) -> None:
    """The sample region column should have two missing values."""
    summary = build_missing_value_summary(sample_dataframe)

    region_row = summary.loc[
        summary["column_name"] == "region"
    ].iloc[0]

    assert region_row["missing_count"] == 2
    assert region_row["missing_percentage"] == 16.67


def test_missing_summary_counts_customer_rating(
    sample_dataframe: pd.DataFrame,
) -> None:
    """Customer rating should contain one missing value."""
    summary = build_missing_value_summary(sample_dataframe)

    rating_row = summary.loc[
        summary["column_name"] == "customer_rating"
    ].iloc[0]

    assert rating_row["missing_count"] == 1
    assert rating_row["missing_percentage"] == 8.33


def test_duplicate_row_count(
    sample_dataframe: pd.DataFrame,
) -> None:
    """The sample dataset should contain one duplicate row."""
    duplicate_count = count_duplicate_rows(sample_dataframe)

    assert duplicate_count == 1


def test_numeric_summary_contains_numeric_columns(
    sample_dataframe: pd.DataFrame,
) -> None:
    """Numeric columns should appear in the numeric summary."""
    summary = build_numeric_summary(sample_dataframe)

    assert "revenue" in summary["column_name"].tolist()
    assert "units_sold" in summary["column_name"].tolist()
    assert "region" not in summary["column_name"].tolist()


def test_numeric_summary_calculates_revenue_mean(
    sample_dataframe: pd.DataFrame,
) -> None:
    """Revenue mean should be calculated from the full dataset."""
    summary = build_numeric_summary(sample_dataframe)

    revenue_mean = summary.loc[
        summary["column_name"] == "revenue",
        "mean",
    ].iloc[0]

    assert revenue_mean == pytest.approx(309.955)


def test_categorical_summary_contains_text_columns(
    sample_dataframe: pd.DataFrame,
) -> None:
    """Text-style columns should appear in the categorical summary."""
    summary = build_categorical_summary(sample_dataframe)

    categorical_columns = summary["column_name"].tolist()

    assert "region" in categorical_columns
    assert "product" in categorical_columns
    assert "category" in categorical_columns
    assert "revenue" not in categorical_columns


def test_categorical_summary_finds_most_common_category(
    sample_dataframe: pd.DataFrame,
) -> None:
    """Accessories should be the most common category."""
    summary = build_categorical_summary(sample_dataframe)

    category_row = summary.loc[
        summary["column_name"] == "category"
    ].iloc[0]

    assert category_row["most_common_value"] == "Accessories"
    assert category_row["most_common_count"] == 7