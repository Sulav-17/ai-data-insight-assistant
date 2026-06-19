import streamlit as st

from src.data_loader import load_csv
from src.profiler import (
    build_categorical_summary,
    build_missing_value_summary,
    build_numeric_summary,
    count_duplicate_rows,
)
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
    "Upload a CSV dataset to inspect its structure and "
    "automatically profile its contents."
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
            f"'{uploaded_file.name}' passed validation "
            "and loaded successfully."
        )

        row_count, column_count = get_dataset_dimensions(
            dataframe
        )

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
            hide_index=True,
            use_container_width=True,
        )

        st.caption(
            "The preview displays only the first five rows. "
            "Profiling uses the complete dataset."
        )

        st.subheader("Schema summary")

        schema_summary = build_schema_summary(dataframe)

        st.dataframe(
            schema_summary,
            hide_index=True,
            use_container_width=True,
        )

        st.subheader("Data quality overview")

        missing_summary = build_missing_value_summary(
            dataframe
        )

        duplicate_row_count = count_duplicate_rows(
            dataframe
        )

        total_missing_values = int(
            missing_summary["missing_count"].sum()
        )

        columns_with_missing_values = int(
            (
                missing_summary["missing_count"] > 0
            ).sum()
        )

        missing_metric, affected_metric, duplicate_metric = (
            st.columns(3)
        )

        with missing_metric:
            st.metric(
                label="Missing cells",
                value=f"{total_missing_values:,}",
            )

        with affected_metric:
            st.metric(
                label="Columns with missing values",
                value=f"{columns_with_missing_values:,}",
            )

        with duplicate_metric:
            st.metric(
                label="Duplicate rows",
                value=f"{duplicate_row_count:,}",
            )

        st.subheader("Missing-value summary")

        st.dataframe(
            missing_summary,
            hide_index=True,
            use_container_width=True,
            column_config={
                "missing_percentage": st.column_config.NumberColumn(
                    "Missing percentage",
                    format="%.2f%%",
                ),
            },
        )

        st.subheader("Numeric summary")

        numeric_summary = build_numeric_summary(dataframe)

        if numeric_summary.empty:
            st.info(
                "No numeric columns were detected in this dataset."
            )

        else:
            st.dataframe(
                numeric_summary.round(2),
                hide_index=True,
                use_container_width=True,
            )

            st.caption(
                "Numeric statistics are calculated from the "
                "complete dataset. Missing numeric values are "
                "excluded by Pandas."
            )

        st.subheader("Categorical summary")

        categorical_summary = build_categorical_summary(
            dataframe
        )

        if categorical_summary.empty:
            st.info(
                "No categorical columns were detected "
                "in this dataset."
            )

        else:
            st.dataframe(
                categorical_summary,
                hide_index=True,
                use_container_width=True,
            )

        st.warning(
            "This milestone profiles the data but does not "
            "clean or modify it. Missing values and duplicate "
            "rows remain in the dataset."
        )

        st.caption(
            "Charts, suggested questions, natural-language "
            "analysis, and AI-generated insights will be "
            "added in later milestones."
        )