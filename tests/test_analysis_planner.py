from pathlib import Path

import pandas as pd
import pytest

from src.analysis_planner import (
    AnalysisPlanError,
    build_analysis_plan,
)
from src.data_loader import load_csv
from src.question_parser import ParsedQuestion


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SAMPLE_CSV_PATH = (
    PROJECT_ROOT
    / "sample_data"
    / "sales_sample.csv"
)


@pytest.fixture
def sample_dataframe() -> pd.DataFrame:
    """Load the sample dataset for planner tests."""
    return load_csv(SAMPLE_CSV_PATH)


def test_build_numeric_mean_plan(
    sample_dataframe: pd.DataFrame,
) -> None:
    parsed = ParsedQuestion(
        operation="mean",
        target_column="revenue",
    )

    plan = build_analysis_plan(
        parsed,
        sample_dataframe,
    )

    assert plan.operation == "mean"
    assert plan.target_column == "revenue"
    assert plan.group_by is None


def test_non_numeric_mean_is_rejected(
    sample_dataframe: pd.DataFrame,
) -> None:
    parsed = ParsedQuestion(
        operation="mean",
        target_column="region",
    )

    with pytest.raises(
        AnalysisPlanError,
        match="not numeric",
    ):
        build_analysis_plan(
            parsed,
            sample_dataframe,
        )


def test_build_grouped_mean_plan(
    sample_dataframe: pd.DataFrame,
) -> None:
    parsed = ParsedQuestion(
        operation="grouped_mean",
        target_column="revenue",
        group_by="region",
    )

    plan = build_analysis_plan(
        parsed,
        sample_dataframe,
    )

    assert plan.operation == "grouped_mean"
    assert plan.target_column == "revenue"
    assert plan.group_by == "region"


def test_numeric_grouping_column_is_rejected(
    sample_dataframe: pd.DataFrame,
) -> None:
    parsed = ParsedQuestion(
        operation="grouped_mean",
        target_column="revenue",
        group_by="units_sold",
    )

    with pytest.raises(
        AnalysisPlanError,
        match="numeric",
    ):
        build_analysis_plan(
            parsed,
            sample_dataframe,
        )


def test_build_most_common_plan(
    sample_dataframe: pd.DataFrame,
) -> None:
    parsed = ParsedQuestion(
        operation="most_common",
        target_column="category",
    )

    plan = build_analysis_plan(
        parsed,
        sample_dataframe,
    )

    assert plan.operation == "most_common"
    assert plan.target_column == "category"


def test_unknown_operation_is_rejected(
    sample_dataframe: pd.DataFrame,
) -> None:
    parsed = ParsedQuestion(
        operation="delete_everything",
    )

    with pytest.raises(
        AnalysisPlanError,
        match="not permitted",
    ):
        build_analysis_plan(
            parsed,
            sample_dataframe,
        )


def test_build_dataset_shape_plan(
    sample_dataframe: pd.DataFrame,
) -> None:
    parsed = ParsedQuestion(
        operation="dataset_shape",
    )

    plan = build_analysis_plan(
        parsed,
        sample_dataframe,
    )

    assert plan.operation == "dataset_shape"
    assert plan.target_column is None