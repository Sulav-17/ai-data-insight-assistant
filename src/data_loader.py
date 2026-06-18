from pathlib import Path
from typing import IO

import pandas as pd

from src.validator import CSVValidationError


CSVSource = str | Path | IO[str] | IO[bytes]


def load_csv(source: CSVSource) -> pd.DataFrame:
    """
    Load a CSV source into a Pandas DataFrame.

    Args:
        source: A file path or file-like object containing CSV data.

    Returns:
        A populated Pandas DataFrame.

    Raises:
        CSVValidationError: If the CSV cannot be parsed or has no data rows.
    """
    if hasattr(source, "seek"):
        source.seek(0)

    try:
        dataframe = pd.read_csv(source)

    except pd.errors.EmptyDataError as error:
        raise CSVValidationError(
            "The CSV file does not contain any readable data."
        ) from error

    except pd.errors.ParserError as error:
        raise CSVValidationError(
            "The file contains malformed CSV content."
        ) from error

    except UnicodeDecodeError as error:
        raise CSVValidationError(
            "The CSV text encoding is not currently supported."
        ) from error

    except OSError as error:
        raise CSVValidationError(
            "The CSV file could not be accessed."
        ) from error

    if dataframe.empty:
        raise CSVValidationError(
            "The CSV contains column headers but no data rows."
        )

    return dataframe