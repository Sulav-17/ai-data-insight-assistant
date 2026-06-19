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

from src.question_suggester import (
    suggest_analysis_questions,
)

from dataclasses import asdict

from src.analysis_planner import (
    AnalysisPlanError,
    build_analysis_plan,
)
from src.question_parser import (
    QuestionParseError,
    parse_question,
)

from src.analyzer import (
    AnalysisExecutionError,
    execute_analysis_plan,
)

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

        st.subheader("Suggested analysis questions")
        
        user_question = st.text_input(
            "Enter your analysis question",
            placeholder="What is the average revenue?",
            help=(
                "Use one of the suggested question formats. "
                "The analysis will not be executed yet."
            ),
        )

        if user_question:
            try:
                parsed_question = parse_question(
                    user_question,
                    dataframe,
                )

                analysis_plan = build_analysis_plan(
                    parsed_question,
                    dataframe,
                )

            except (
                QuestionParseError,
                AnalysisPlanError,
            ) as error:
                st.error(str(error))

            else:
                st.success(
                    "The question was converted into "
                    "a safe analysis plan."
                )

                st.write("**Plan description**")

                st.write(
                    analysis_plan.description
                )

                st.write("**Structured plan**")

                st.json(
                    asdict(analysis_plan)
                )

                st.info(
                    "The plan has been validated. "
                    "Run it to calculate a deterministic result "
                    "from the complete uploaded dataset."
                )

                run_analysis = st.button(
                    "Run safe analysis",
                    type="primary",
                )

                if run_analysis:
                    try:
                        analysis_result = execute_analysis_plan(
                            analysis_plan,
                            dataframe,
                        )

                    except AnalysisExecutionError as error:
                        st.error(str(error))

                    else:
                        st.subheader("Analysis result")

                        if analysis_result.result_type == "scalar":
                            scalar_value = (
                                analysis_result.scalar_value
                            )

                            if isinstance(scalar_value, float):
                                display_value = (
                                    f"{scalar_value:,.2f}"
                                )
                            else:
                                display_value = (
                                    f"{scalar_value:,}"
                                )

                            st.metric(
                                label=analysis_result.title,
                                value=display_value,
                            )

                        elif analysis_result.result_type == "table":
                            result_table = analysis_result.table

                            st.write(
                                f"**{analysis_result.title}**"
                            )

                            if (
                                result_table is None
                                or result_table.empty
                            ):
                                st.info(
                                    "The analysis completed, but no "
                                    "matching records were found."
                                )

                            else:
                                st.dataframe(
                                    result_table,
                                    hide_index=True,
                                    use_container_width=True,
                                )

                        else:
                            st.error(
                                "The analysis returned an "
                                "unsupported result type."
                            )

                        st.success(
                            "The result was calculated using "
                            "approved Pandas operations."
                        )

                        st.caption(
                            "The complete uploaded dataset was used. "
                            "No LLM-generated code was executed."
                        )

        suggested_questions = (
            suggest_analysis_questions(
                dataframe,
                max_questions=6,
            )
        )



        st.write(
            "These questions were generated from the "
            "dataset schema using deterministic rules."
        )

        for position, question in enumerate(
            suggested_questions,
            start=1,
        ):
            st.markdown(
                f"**{position}.** {question}"
            )

        st.caption(
            "The application cannot answer these questions "
            "yet. Natural-language interpretation and safe "
            "analysis execution will be added next."
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