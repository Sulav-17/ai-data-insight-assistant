from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SAMPLE_CSV_PATH = PROJECT_ROOT / "sample_data" / "sales_sample.csv"


def test_sample_csv_exists() -> None:
    """Confirm that the project includes its sample dataset."""
    assert SAMPLE_CSV_PATH.exists()


def test_sample_csv_contains_expected_columns() -> None:
    """Confirm that the sample dataset has the required starter columns."""
    dataframe = pd.read_csv(SAMPLE_CSV_PATH)

    expected_columns = {
        "order_id",
        "order_date",
        "region",
        "product",
        "category",
        "units_sold",
        "unit_price",
        "revenue",
        "customer_rating",
    }

    assert expected_columns.issubset(dataframe.columns)