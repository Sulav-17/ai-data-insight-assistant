import pandas as pd

from src.analysis_planner import AnalysisPlan
from src.analyzer import AnalysisResult
from src.report_generator import generate_markdown_report


def test_scalar_report_contains_question_plan_and_result() -> None:
    plan = AnalysisPlan(
        operation="mean",
        target_column="revenue",
        group_by=None,
        description="Calculate average revenue.",
    )

    result = AnalysisResult(
        operation="mean",
        result_type="scalar",
        title="Average revenue",
        scalar_value=309.955,
    )

    report = generate_markdown_report(
        question="What is the average revenue?",
        analysis_plan=plan,
        analysis_result=result,
        business_insight="Average revenue is 309.95.",
    )

    assert "# AI Data Insight Assistant Report" in report
    assert "What is the average revenue?" in report
    assert "`mean`" in report
    assert "309.95" in report
    assert "Average revenue is 309.95." in report


def test_table_report_contains_csv_result() -> None:
    plan = AnalysisPlan(
        operation="grouped_mean",
        target_column="revenue",
        group_by="region",
        description="Average revenue by region.",
    )

    result = AnalysisResult(
        operation="grouped_mean",
        result_type="table",
        title="Average revenue by region",
        table=pd.DataFrame(
            {
                "region": ["East", "West"],
                "average_revenue": [313.30, 294.93],
            }
        ),
    )

    report = generate_markdown_report(
        question=(
            "How does average revenue compare across region?"
        ),
        analysis_plan=plan,
        analysis_result=result,
        business_insight="East has the highest average.",
    )

    assert "```csv" in report
    assert "East" in report
    assert "313.3" in report
    assert "No arbitrary Python code" in report