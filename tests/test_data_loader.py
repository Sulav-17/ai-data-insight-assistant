from io import StringIO
from pathlib import Path

import pandas as pd
import pytest

from src.data_loader import load_csv
from src.validator import CSVValidationError


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SAMPLE_CSV_PATH = PROJECT_ROOT / "sample_data" / "sales_sample.csv"


def test_load_csv_returns_dataframe() -> None:
    """The sample CSV should load as a populated DataFrame."""
    dataframe = load_csv(SAMPLE_CSV_PATH)

    assert isinstance(dataframe, pd.DataFrame)
    assert not dataframe.empty


def test_load_csv_rejects_completely_empty_content() -> None:
    """CSV content containing no text should be rejected."""
    empty_csv = StringIO("")

    with pytest.raises(
        CSVValidationError,
        match="readable data",
    ):
        load_csv(empty_csv)


def test_load_csv_rejects_header_only_content() -> None:
    """A CSV with headers but no records should be rejected."""
    header_only_csv = StringIO("name,revenue\n")

    with pytest.raises(
        CSVValidationError,
        match="no data rows",
    ):
        load_csv(header_only_csv)


def test_load_csv_rejects_malformed_content() -> None:
    """Malformed quotation marks should produce a controlled error."""
    malformed_csv = StringIO(
        'name,revenue\n"Broken Product,100\n'
    )

    with pytest.raises(
        CSVValidationError,
        match="malformed CSV content",
    ):
        load_csv(malformed_csv)