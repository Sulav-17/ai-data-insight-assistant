
from dataclasses import asdict

import streamlit as st
from dotenv import load_dotenv

from src.analysis_planner import (
    AnalysisPlanError,
    build_analysis_plan,
)
from src.analyzer import (
    AnalysisExecutionError,
    execute_analysis_plan,
)
from src.charts import (
    ChartBuildError,
    build_result_chart,
)
from src.data_loader import load_csv
from src.insight_generator import (
    InsightGenerationError,
    generate_business_insight,
)
from src.llm_service import (
    LLMServiceError,
    generate_insight_with_optional_llm,
    is_llm_configured,
    parse_question_with_optional_llm,
)
from src.profiler import (
    build_categorical_summary,
    build_missing_value_summary,
    build_numeric_summary,
    count_duplicate_rows,
)
from src.question_parser import QuestionParseError
from src.question_suggester import suggest_analysis_questions
from src.report_generator import (
    ReportGenerationError,
    generate_markdown_report,
)
from src.schema import (
    build_schema_summary,
    get_dataset_dimensions,
    get_dataset_preview,
)
from src.validator import (
    CSVValidationError,
    validate_csv_metadata,
)


load_dotenv()


APP_TITLE = "AI Data Insight Assistant"


st.set_page_config(
    page_title=APP_TITLE,
    page_icon="📊",
    layout="wide",
)


st.title("📊 AI Data Insight Assistant")

st.write(
    "Upload a CSV dataset to inspect its structure, profile its contents, "
    "ask data questions, generate visualizations, and receive clear insights."
)

st.caption(
    "All calculations are performed through approved Pandas operations. "
    "The AI layer cannot execute arbitrary Python code."
)


uploaded_file = st.file_uploader(
    "Choose a CSV file",
    type=["csv"],
    help="The CSV file must be 10 MB or smaller.",
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
        dataset_key = (
            f"{uploaded_file.name}:{uploaded_file.size}"
        )

        if st.session_state.get("dataset_key") != dataset_key:
            st.session_state["dataset_key"] = dataset_key
            st.session_state.pop(
                "analysis_output",
                None,
            )

        st.success(
            f"'{uploaded_file.name}' passed validation "
            "and loaded successfully."
        )

        row_count, column_count = get_dataset_dimensions(
            dataframe
        )

        # ---------------------------------------------------------
        # Dataset overview
        # ---------------------------------------------------------

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

        # ---------------------------------------------------------
        # Dataset preview
        # ---------------------------------------------------------

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
            "The preview displays the first five rows. "
            "All analysis uses the complete uploaded dataset."
        )

        # ---------------------------------------------------------
        # Schema summary
        # ---------------------------------------------------------

        st.subheader("Schema summary")

        schema_summary = build_schema_summary(dataframe)

        st.dataframe(
            schema_summary,
            hide_index=True,
            use_container_width=True,
        )

        st.info(
            "Data types are inferred by Pandas from the CSV content. "
            "An object column may contain text, dates, or mixed values."
        )

        # ---------------------------------------------------------
        # Data quality overview
        # ---------------------------------------------------------

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

        # ---------------------------------------------------------
        # Missing-value summary
        # ---------------------------------------------------------

        st.subheader("Missing-value summary")

        st.dataframe(
            missing_summary,
            hide_index=True,
            use_container_width=True,
            column_config={
                "missing_percentage": (
                    st.column_config.NumberColumn(
                        "Missing percentage",
                        format="%.2f%%",
                    )
                ),
            },
        )

        # ---------------------------------------------------------
        # Numeric summary
        # ---------------------------------------------------------

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
                "Missing numeric values are excluded from "
                "descriptive-statistic calculations."
            )

        # ---------------------------------------------------------
        # Categorical summary
        # ---------------------------------------------------------

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
            "The application reports missing values and duplicate "
            "rows but does not automatically remove or replace them."
        )

        # ---------------------------------------------------------
        # Suggested questions
        # ---------------------------------------------------------

        st.subheader("Suggested analysis questions")

        suggested_questions = suggest_analysis_questions(
            dataframe,
            max_questions=6,
        )

        st.write(
            "These questions were generated from the dataset "
            "schema using deterministic rules."
        )

        for position, question in enumerate(
            suggested_questions,
            start=1,
        ):
            st.markdown(
                f"**{position}.** {question}"
            )

        # ---------------------------------------------------------
        # Natural-language analysis
        # ---------------------------------------------------------

        st.subheader("Ask a data question")

        llm_available = is_llm_configured()

        if llm_available:
            st.success(
                "Optional AI interpretation is available."
            )
        else:
            st.info(
                "AI interpretation is not configured. "
                "The deterministic question formats will "
                "continue to work normally."
            )

        with st.form("analysis_question_form"):
            user_question = st.text_input(
                "Enter your analysis question",
                placeholder=(
                    "Show me average revenue for each region"
                ),
            )

            use_llm = st.checkbox(
                (
                    "Use AI for broader wording and "
                    "enhanced explanation"
                ),
                value=False,
                disabled=not llm_available,
                help=(
                    "The deterministic parser is always attempted "
                    "first. AI is used only when necessary and "
                    "never executes code."
                ),
            )

            analyze_question = st.form_submit_button(
                "Analyze safely",
                type="primary",
            )

        if analyze_question:
            st.session_state.pop(
                "analysis_output",
                None,
            )

            try:
                (
                    parsed_question,
                    interpretation_source,
                ) = parse_question_with_optional_llm(
                    question=user_question,
                    dataframe=dataframe,
                    use_llm=use_llm,
                )

                analysis_plan = build_analysis_plan(
                    parsed_question,
                    dataframe,
                )

                analysis_result = execute_analysis_plan(
                    analysis_plan,
                    dataframe,
                )

                deterministic_insight = (
                    generate_business_insight(
                        analysis_result
                    )
                )

                (
                    business_insight,
                    insight_source,
                ) = generate_insight_with_optional_llm(
                    analysis_result=analysis_result,
                    deterministic_insight=(
                        deterministic_insight
                    ),
                    use_llm=use_llm,
                )

                markdown_report = generate_markdown_report(
                    question=user_question,
                    analysis_plan=analysis_plan,
                    analysis_result=analysis_result,
                    business_insight=business_insight,
                )

            except (
                QuestionParseError,
                AnalysisPlanError,
                AnalysisExecutionError,
                InsightGenerationError,
                ReportGenerationError,
                LLMServiceError,
            ) as error:
                st.error(str(error))

            else:
                st.session_state["analysis_output"] = {
                    "question": user_question,
                    "plan": analysis_plan,
                    "result": analysis_result,
                    "insight": business_insight,
                    "interpretation_source": (
                        interpretation_source
                    ),
                    "insight_source": insight_source,
                    "report": markdown_report,
                }

        # ---------------------------------------------------------
        # Render saved analysis output
        # ---------------------------------------------------------

        analysis_output = st.session_state.get(
            "analysis_output"
        )

        if analysis_output is not None:
            analysis_plan = analysis_output["plan"]
            analysis_result = analysis_output["result"]
            business_insight = analysis_output["insight"]

            st.divider()

            st.subheader("Validated analysis plan")

            st.write(analysis_plan.description)

            st.json(
                asdict(analysis_plan)
            )

            st.caption(
                "Question interpretation: "
                f"{analysis_output['interpretation_source']}"
            )

            # -----------------------------------------------------
            # Analysis result
            # -----------------------------------------------------

            st.subheader("Analysis result")

            if analysis_result.result_type == "scalar":
                scalar_value = analysis_result.scalar_value

                if scalar_value is None:
                    st.error(
                        "The analysis returned no scalar value."
                    )

                else:
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
                        "The analysis completed but returned "
                        "no matching records."
                    )

                else:
                    st.dataframe(
                        result_table,
                        hide_index=True,
                        use_container_width=True,
                    )

            else:
                st.error(
                    "The analysis returned an unsupported "
                    "result type."
                )

            # -----------------------------------------------------
            # Plotly chart
            # -----------------------------------------------------

            try:
                result_chart = build_result_chart(
                    analysis_result
                )

            except ChartBuildError as error:
                st.warning(
                    f"A chart could not be created: {error}"
                )

            else:
                if result_chart is not None:
                    st.subheader("Result visualization")

                    st.plotly_chart(
                        result_chart,
                        use_container_width=True,
                    )

                else:
                    st.caption(
                        "A chart is not necessary for this "
                        "type of result."
                    )

            # -----------------------------------------------------
            # Plain-English insight
            # -----------------------------------------------------

            st.subheader("Plain-English insight")

            st.write(business_insight)

            st.caption(
                "Insight source: "
                f"{analysis_output['insight_source']}"
            )

            # -----------------------------------------------------
            # Report export
            # -----------------------------------------------------

            st.download_button(
                label="Download analysis report",
                data=analysis_output["report"],
                file_name="data_insight_report.md",
                mime="text/markdown",
            )

            st.success(
                "The calculation was performed through "
                "approved Pandas operations."
            )

            st.caption(
                "AI may interpret the question or rewrite the "
                "verified explanation, but it does not execute "
                "code or calculate dataset metrics."
            )
            
