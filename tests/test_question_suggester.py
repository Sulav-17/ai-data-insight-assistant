from pathlib import Path

import pandas as pd
import pytest

from src.data_loader import load_csv
from src.question_suggester import (
    get_categorical_analysis_columns,
    get_numeric_analysis_columns,
    humanize_column_name,
    suggest_analysis_questions,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SAMPLE_CSV_PATH = (
    PROJECT_ROOT
    / "sample_data"
    / "sales_sample.csv"
)


@pytest.fixture
def sample_dataframe() -> pd.DataFrame:
    """Load the sample dataset for suggestion tests."""
    return load_csv(SAMPLE_CSV_PATH)


def test_humanize_column_name() -> None:
    """Underscores should become spaces."""
    result = humanize_column_name(
        "customer_rating"
    )

    assert result == "customer rating"


def test_numeric_columns_exclude_identifier(
    sample_dataframe: pd.DataFrame,
) -> None:
    """Identifier columns should not be analysis measurements."""
    numeric_columns = get_numeric_analysis_columns(
        sample_dataframe
    )

    assert "order_id" not in numeric_columns
    assert "units_sold" in numeric_columns
    assert "revenue" in numeric_columns


def test_categorical_columns_exclude_high_cardinality_values(
    sample_dataframe: pd.DataFrame,
) -> None:
    """Nearly unique text columns should not be grouping suggestions."""
    categorical_columns = (
        get_categorical_analysis_columns(
            sample_dataframe
        )
    )

    assert "region" in categorical_columns
    assert "product" in categorical_columns
    assert "category" in categorical_columns
    assert "order_date" not in categorical_columns


def test_suggestions_use_existing_columns(
    sample_dataframe: pd.DataFrame,
) -> None:
    """Suggestions should be based on columns in the dataset."""
    suggestions = suggest_analysis_questions(
        sample_dataframe
    )

    combined_text = " ".join(suggestions).lower()

    assert "units sold" in combined_text
    assert "region" in combined_text


def test_suggestions_do_not_use_identifier(
    sample_dataframe: pd.DataFrame,
) -> None:
    """Suggestions should not recommend analyzing order IDs."""
    suggestions = suggest_analysis_questions(
        sample_dataframe
    )

    combined_text = " ".join(suggestions).lower()

    assert "order id" not in combined_text


def test_suggestions_respect_maximum_count(
    sample_dataframe: pd.DataFrame,
) -> None:
    """The returned question count should respect the limit."""
    suggestions = suggest_analysis_questions(
        sample_dataframe,
        max_questions=3,
    )

    assert len(suggestions) == 3


def test_suggestions_are_unique(
    sample_dataframe: pd.DataFrame,
) -> None:
    """The suggestion list should not contain duplicates."""
    suggestions = suggest_analysis_questions(
        sample_dataframe
    )

    assert len(suggestions) == len(set(suggestions))


def test_invalid_maximum_count_is_rejected(
    sample_dataframe: pd.DataFrame,
) -> None:
    """Question limits must be greater than zero."""
    with pytest.raises(
        ValueError,
        match="at least 1",
    ):
        suggest_analysis_questions(
            sample_dataframe,
            max_questions=0,
        )


def test_identifier_only_dataset_uses_fallback() -> None:
    """A dataset with only an ID should receive safe fallbacks."""
    dataframe = pd.DataFrame(
        {
            "order_id": [1001, 1002, 1003],
        }
    )

    suggestions = suggest_analysis_questions(
        dataframe
    )

    assert suggestions == [
        "How many rows and columns are in the dataset?",
        "Which columns contain missing values?",
    ]