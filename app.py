import streamlit as st

from src.data_loader import load_csv
from src.schema import (
    build_schema_summary,
    get_dataset_dimensions,
    get_dataset_preview,
)
from src.validator import CSVValidationError, validate_csv_metadata


APP_TITLE = "AI Data Insight Assistant"


st.set_page_config(
    page_title=APP_TITLE,
    page_icon="📊",
    layout="wide",
)

st.title("📊 AI Data Insight Assistant")

st.write(
    "Upload a CSV dataset to inspect its structure through "
    "a safe and explainable data workflow."
)

uploaded_file = st.file_uploader(
    "Choose a CSV file",
    type=["csv"],
    help="The CSV must be 10 MB or smaller.",
)

if uploaded_file is None:
    st.info("Upload a CSV file to begin.")

else:
    try:
        validate_csv_metadata(
            file_name=uploaded_file.name,
            file_size=uploaded_file.size,
        )

        dataframe = load_csv(uploaded_file)

    except CSVValidationError as error:
        st.error(str(error))

    else:
        st.success(
            f"'{uploaded_file.name}' passed validation and loaded successfully."
        )

        row_count, column_count = get_dataset_dimensions(dataframe)

        st.subheader("Dataset overview")

        row_metric, column_metric = st.columns(2)

        with row_metric:
            st.metric(
                label="Rows",
                value=f"{row_count:,}",
            )

        with column_metric:
            st.metric(
                label="Columns",
                value=f"{column_count:,}",
            )

        st.subheader("Dataset preview")

        preview = get_dataset_preview(
            dataframe,
            row_count=5,
        )

        st.dataframe(
            preview,
            use_container_width=True,
        )

        st.caption(
            "The preview displays only the first five rows. "
            "The complete dataset remains loaded in memory."
        )

        st.subheader("Schema summary")

        schema_summary = build_schema_summary(dataframe)

        st.dataframe(
            schema_summary,
            hide_index=True,
            use_container_width=True,
        )

        st.info(
            "Data types are inferred by Pandas from the CSV content. "
            "Controlled type conversion will be handled in a later milestone."
        )

        st.caption(
            "Missing-value analysis, duplicate detection, statistics, "
            "charts, and AI questions have not been added yet."
        )