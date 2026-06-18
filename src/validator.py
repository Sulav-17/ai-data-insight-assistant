from pathlib import Path


MAX_FILE_SIZE_MB = 10


class CSVValidationError(ValueError):
    """Raised when an uploaded CSV file fails validation."""


def validate_csv_metadata(
    file_name: str,
    file_size: int,
    max_size_mb: int = MAX_FILE_SIZE_MB,
) -> None:
    """
    Validate basic CSV file metadata.

    Args:
        file_name: Name of the uploaded file.
        file_size: Size of the uploaded file in bytes.
        max_size_mb: Maximum allowed file size in megabytes.

    Raises:
        CSVValidationError: If the file metadata is invalid.
    """
    if not file_name or not file_name.strip():
        raise CSVValidationError("The uploaded file must have a name.")

    file_extension = Path(file_name).suffix.lower()

    if file_extension != ".csv":
        raise CSVValidationError("Only CSV files are supported.")

    if file_size <= 0:
        raise CSVValidationError("The uploaded CSV file is empty.")

    max_size_bytes = max_size_mb * 1024 * 1024

    if file_size > max_size_bytes:
        raise CSVValidationError(
            f"The CSV file must be {max_size_mb} MB or smaller."
        )