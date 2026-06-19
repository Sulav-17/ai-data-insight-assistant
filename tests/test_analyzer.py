from pathlib import Path

import pandas as pd
import pytest
from pandas.testing import assert_frame_equal

from src.analysis_planner import AnalysisPlan
from src.analyzer import (
    AnalysisExecutionError,
    execute_analysis_plan,
)
from src.data_loader import load_csv


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SAMPLE_CSV_PATH = (
    PROJECT_ROOT
    / "sample_data"
    / "sales_sample.csv"
)


@pytest.fixture
def sample_dataframe() -> pd.DataFrame:
    """Load the sample dataset for analyzer tests."""
    return load_csv(SAMPLE_CSV_PATH)


def test_execute_mean(
    sample_dataframe: pd.DataFrame,
) -> None:
    """Revenue mean should be calculated from the full dataset."""
    plan = AnalysisPlan(
        operation="mean",
        target_column="revenue",
        group_by=None,
        description="Calculate average revenue.",
    )

    result = execute_analysis_plan(
        plan,
        sample_dataframe,
    )

    assert result.result_type == "scalar"
    assert result.scalar_value == pytest.approx(309.955)


def test_execute_sum(
    sample_dataframe: pd.DataFrame,
) -> None:
    """Revenue total should include all dataset rows."""
    plan = AnalysisPlan(
        operation="sum",
        target_column="revenue",
        group_by=None,
        description="Calculate total revenue.",
    )

    result = execute_analysis_plan(
        plan,
        sample_dataframe,
    )

    assert result.scalar_value == pytest.approx(3719.46)


def test_execute_dataset_shape(
    sample_dataframe: pd.DataFrame,
) -> None:
    """Dataset shape should return twelve rows and nine columns."""
    plan = AnalysisPlan(
        operation="dataset_shape",
        target_column=None,
        group_by=None,
        description="Count rows and columns.",
    )

    result = execute_analysis_plan(
        plan,
        sample_dataframe,
    )

    assert result.table is not None

    values = dict(
        zip(
            result.table["metric"],
            result.table["value"],
        )
    )

    assert values["Rows"] == 12
    assert values["Columns"] == 9


def test_execute_missing_columns(
    sample_dataframe: pd.DataFrame,
) -> None:
    """Only affected columns should appear in the result."""
    plan = AnalysisPlan(
        operation="missing_columns",
        target_column=None,
        group_by=None,
        description="Find missing columns.",
    )

    result = execute_analysis_plan(
        plan,
        sample_dataframe,
    )

    assert result.table is not None

    missing_counts = dict(
        zip(
            result.table["column_name"],
            result.table["missing_count"],
        )
    )

    assert missing_counts == {
        "region": 2,
        "customer_rating": 1,
    }


def test_execute_grouped_mean(
    sample_dataframe: pd.DataFrame,
) -> None:
    """Average revenue should be calculated for each region."""
    plan = AnalysisPlan(
        operation="grouped_mean",
        target_column="revenue",
        group_by="region",
        description="Average revenue by region.",
    )

    result = execute_analysis_plan(
        plan,
        sample_dataframe,
    )

    assert result.table is not None

    north_average = result.table.loc[
        result.table["region"] == "North",
        "average_revenue",
    ].iloc[0]

    missing_average = result.table.loc[
        result.table["region"] == "(Missing)",
        "average_revenue",
    ].iloc[0]

    assert north_average == pytest.approx(359.95)
    assert missing_average == pytest.approx(249.99)


def test_execute_most_common(
    sample_dataframe: pd.DataFrame,
) -> None:
    """Accessories should be the most common category."""
    plan = AnalysisPlan(
        operation="most_common",
        target_column="category",
        group_by=None,
        description="Count category values.",
    )

    result = execute_analysis_plan(
        plan,
        sample_dataframe,
    )

    assert result.table is not None

    first_row = result.table.iloc[0]

    assert first_row["category"] == "Accessories"
    assert first_row["count"] == 7


def test_non_numeric_target_is_rejected(
    sample_dataframe: pd.DataFrame,
) -> None:
    """A forged numeric plan should be rejected by the executor."""
    plan = AnalysisPlan(
        operation="mean",
        target_column="region",
        group_by=None,
        description="Invalid average.",
    )

    with pytest.raises(
        AnalysisExecutionError,
        match="not numeric",
    ):
        execute_analysis_plan(
            plan,
            sample_dataframe,
        )


def test_unknown_operation_is_rejected(
    sample_dataframe: pd.DataFrame,
) -> None:
    """Operations outside the allowlist must be rejected."""
    plan = AnalysisPlan(
        operation="delete_rows",
        target_column=None,
        group_by=None,
        description="Unsafe operation.",
    )

    with pytest.raises(
        AnalysisExecutionError,
        match="not permitted",
    ):
        execute_analysis_plan(
            plan,
            sample_dataframe,
        )


def test_all_missing_numeric_column_is_rejected() -> None:
    """An empty numeric result should not be presented as meaningful."""
    dataframe = pd.DataFrame(
        {
            "revenue": pd.Series(
                [None, None],
                dtype="float64",
            ),
        }
    )

    plan = AnalysisPlan(
        operation="mean",
        target_column="revenue",
        group_by=None,
        description="Average revenue.",
    )

    with pytest.raises(
        AnalysisExecutionError,
        match="no usable numeric values",
    ):
        execute_analysis_plan(
            plan,
            dataframe,
        )


def test_analysis_does_not_modify_original_dataframe(
    sample_dataframe: pd.DataFrame,
) -> None:
    """Safe analysis should leave the source DataFrame unchanged."""
    original_copy = sample_dataframe.copy(deep=True)

    plan = AnalysisPlan(
        operation="grouped_mean",
        target_column="revenue",
        group_by="region",
        description="Average revenue by region.",
    )

    execute_analysis_plan(
        plan,
        sample_dataframe,
    )

    assert_frame_equal(
        sample_dataframe,
        original_copy,
    )