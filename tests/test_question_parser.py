from pathlib import Path

import pandas as pd
import pytest

from src.data_loader import load_csv
from src.question_parser import (
    QuestionParseError,
    parse_question,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SAMPLE_CSV_PATH = (
    PROJECT_ROOT
    / "sample_data"
    / "sales_sample.csv"
)


@pytest.fixture
def sample_dataframe() -> pd.DataFrame:
    """Load the sample dataset for parser tests."""
    return load_csv(SAMPLE_CSV_PATH)


def test_parse_average_question(
    sample_dataframe: pd.DataFrame,
) -> None:
    parsed = parse_question(
        "What is the average revenue?",
        sample_dataframe,
    )

    assert parsed.operation == "mean"
    assert parsed.target_column == "revenue"
    assert parsed.group_by is None


def test_parse_humanized_column_name(
    sample_dataframe: pd.DataFrame,
) -> None:
    parsed = parse_question(
        "What is the total units sold?",
        sample_dataframe,
    )

    assert parsed.operation == "sum"
    assert parsed.target_column == "units_sold"


def test_parse_grouped_average(
    sample_dataframe: pd.DataFrame,
) -> None:
    parsed = parse_question(
        "How does average revenue compare across region?",
        sample_dataframe,
    )

    assert parsed.operation == "grouped_mean"
    assert parsed.target_column == "revenue"
    assert parsed.group_by == "region"


def test_parse_most_common_question(
    sample_dataframe: pd.DataFrame,
) -> None:
    parsed = parse_question(
        "What are the most common values in category?",
        sample_dataframe,
    )

    assert parsed.operation == "most_common"
    assert parsed.target_column == "category"


def test_parse_dataset_shape_question(
    sample_dataframe: pd.DataFrame,
) -> None:
    parsed = parse_question(
        "How many rows and columns are in the dataset?",
        sample_dataframe,
    )

    assert parsed.operation == "dataset_shape"


def test_unknown_column_is_rejected(
    sample_dataframe: pd.DataFrame,
) -> None:
    with pytest.raises(
        QuestionParseError,
        match="was not found",
    ):
        parse_question(
            "What is the average profit?",
            sample_dataframe,
        )


def test_unsupported_question_is_rejected(
    sample_dataframe: pd.DataFrame,
) -> None:
    with pytest.raises(
        QuestionParseError,
        match="not currently supported",
    ):
        parse_question(
            "Why did revenue decline last year?",
            sample_dataframe,
        )


def test_empty_question_is_rejected(
    sample_dataframe: pd.DataFrame,
) -> None:
    with pytest.raises(
        QuestionParseError,
        match="Enter a question",
    ):
        parse_question(
            "   ",
            sample_dataframe,
        )