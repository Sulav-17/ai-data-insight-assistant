from pathlib import Path

import pandas as pd
import pytest

from src.data_loader import load_csv
from src.schema import (
    build_schema_summary,
    get_dataset_dimensions,
    get_dataset_preview,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SAMPLE_CSV_PATH = PROJECT_ROOT / "sample_data" / "sales_sample.csv"


@pytest.fixture
def sample_dataframe() -> pd.DataFrame:
    """Load the sample dataset for schema tests."""
    return load_csv(SAMPLE_CSV_PATH)


def test_get_dataset_dimensions(
    sample_dataframe: pd.DataFrame,
) -> None:
    """The sample dataset should report the correct dimensions."""
    row_count, column_count = get_dataset_dimensions(sample_dataframe)

    assert row_count == 12
    assert column_count == 9


def test_get_dataset_preview_returns_requested_rows(
    sample_dataframe: pd.DataFrame,
) -> None:
    """The preview should contain the requested number of rows."""
    preview = get_dataset_preview(
        sample_dataframe,
        row_count=3,
    )

    assert len(preview) == 3
    assert list(preview.columns) == list(sample_dataframe.columns)


def test_get_dataset_preview_does_not_return_original_object(
    sample_dataframe: pd.DataFrame,
) -> None:
    """The preview should be a separate DataFrame object."""
    preview = get_dataset_preview(sample_dataframe)

    assert preview is not sample_dataframe


def test_get_dataset_preview_rejects_invalid_row_count(
    sample_dataframe: pd.DataFrame,
) -> None:
    """Preview row counts must be greater than zero."""
    with pytest.raises(
        ValueError,
        match="at least 1",
    ):
        get_dataset_preview(
            sample_dataframe,
            row_count=0,
        )


def test_build_schema_summary_contains_all_columns(
    sample_dataframe: pd.DataFrame,
) -> None:
    """The schema summary should contain every dataset column."""
    schema_summary = build_schema_summary(sample_dataframe)

    assert len(schema_summary) == len(sample_dataframe.columns)

    assert list(schema_summary.columns) == [
        "position",
        "column_name",
        "data_type",
    ]

    assert list(schema_summary["column_name"]) == list(
        sample_dataframe.columns
    )


def test_schema_identifies_numeric_column(
    sample_dataframe: pd.DataFrame,
) -> None:
    """The revenue column should be recognized as numeric."""
    schema_summary = build_schema_summary(sample_dataframe)

    revenue_type = schema_summary.loc[
        schema_summary["column_name"] == "revenue",
        "data_type",
    ].iloc[0]

    assert revenue_type == "float64"