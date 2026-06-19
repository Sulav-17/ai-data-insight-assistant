from src.analysis_planner import AnalysisPlan
from src.analyzer import AnalysisResult


class ReportGenerationError(ValueError):
    """Raised when an analysis report cannot be generated."""


def generate_markdown_report(
    question: str,
    analysis_plan: AnalysisPlan,
    analysis_result: AnalysisResult,
    business_insight: str,
) -> str:
    """
    Generate a downloadable Markdown analysis summary.

    The report contains the user's question, validated plan,
    verified result, and deterministic interpretation.
    """
    cleaned_question = question.strip()

    if not cleaned_question:
        raise ReportGenerationError(
            "A question is required to generate a report."
        )

    report_lines = [
        "# AI Data Insight Assistant Report",
        "",
        "## Question",
        "",
        cleaned_question,
        "",
        "## Validated Analysis Plan",
        "",
        f"- **Operation:** `{analysis_plan.operation}`",
        (
            f"- **Target column:** "
            f"`{analysis_plan.target_column}`"
            if analysis_plan.target_column is not None
            else "- **Target column:** None"
        ),
        (
            f"- **Group by:** `{analysis_plan.group_by}`"
            if analysis_plan.group_by is not None
            else "- **Group by:** None"
        ),
        f"- **Description:** {analysis_plan.description}",
        "",
        "## Verified Result",
        "",
    ]

    if analysis_result.result_type == "scalar":
        if analysis_result.scalar_value is None:
            raise ReportGenerationError(
                "The scalar result does not contain a value."
            )

        if isinstance(analysis_result.scalar_value, float):
            formatted_value = (
                f"{analysis_result.scalar_value:,.2f}"
            )
        else:
            formatted_value = (
                f"{analysis_result.scalar_value:,}"
            )

        report_lines.extend(
            [
                f"**{analysis_result.title}:** "
                f"{formatted_value}",
                "",
            ]
        )

    elif analysis_result.result_type == "table":
        if analysis_result.table is None:
            raise ReportGenerationError(
                "The table result does not contain a table."
            )

        if analysis_result.table.empty:
            report_lines.extend(
                [
                    "The analysis completed but returned "
                    "no matching records.",
                    "",
                ]
            )

        else:
            report_lines.extend(
                [
                    f"**{analysis_result.title}**",
                    "",
                    "```csv",
                    analysis_result.table.to_csv(
                        index=False
                    ).strip(),
                    "```",
                    "",
                ]
            )

    else:
        raise ReportGenerationError(
            "The analysis result type is not supported."
        )

    report_lines.extend(
        [
            "## Plain-English Insight",
            "",
            business_insight,
            "",
            "## Method and Safety",
            "",
            (
                "The result was calculated from the complete "
                "uploaded dataset using approved Pandas "
                "operations."
            ),
            "",
            (
                "No arbitrary Python code was generated or "
                "executed."
            ),
            "",
            (
                "The explanation summarizes observed results "
                "and does not establish causation."
            ),
            "",
        ]
    )

    return "\n".join(report_lines)