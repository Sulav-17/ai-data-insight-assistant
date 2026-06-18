import streamlit as st

from src.data_loader import load_csv
from src.validator import CSVValidationError, validate_csv_metadata


APP_TITLE = "AI Data Insight Assistant"


st.set_page_config(
    page_title=APP_TITLE,
    page_icon="📊",
    layout="wide",
)

st.title("📊 AI Data Insight Assistant")

st.write(
    "Upload a CSV dataset to begin a safe and explainable "
    "data-analysis workflow."
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

        _dataframe = load_csv(uploaded_file)

    except CSVValidationError as error:
        st.error(str(error))

    else:
        st.success(
            f"'{uploaded_file.name}' passed validation and loaded successfully."
        )

        st.write(
            "The file extension, size, CSV structure, and data rows "
            "were checked successfully."
        )

        st.caption(
            "Dataset preview, schema inspection, and profiling "
            "will be added in the next milestone."
        )