import pytest

from src.validator import CSVValidationError, validate_csv_metadata


def test_valid_csv_metadata_passes() -> None:
    """A normal CSV file should pass metadata validation."""
    validate_csv_metadata(
        file_name="sales.csv",
        file_size=1024,
    )


def test_non_csv_extension_is_rejected() -> None:
    """Files without a CSV extension should be rejected."""
    with pytest.raises(
        CSVValidationError,
        match="Only CSV files are supported",
    ):
        validate_csv_metadata(
            file_name="sales.xlsx",
            file_size=1024,
        )


def test_empty_file_is_rejected() -> None:
    """A zero-byte CSV file should be rejected."""
    with pytest.raises(
        CSVValidationError,
        match="empty",
    ):
        validate_csv_metadata(
            file_name="sales.csv",
            file_size=0,
        )


def test_oversized_file_is_rejected() -> None:
    """A file larger than the allowed limit should be rejected."""
    eleven_megabytes = 11 * 1024 * 1024

    with pytest.raises(
        CSVValidationError,
        match="10 MB or smaller",
    ):
        validate_csv_metadata(
            file_name="sales.csv",
            file_size=eleven_megabytes,
        )