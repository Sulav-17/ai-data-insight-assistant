from types import SimpleNamespace

import pandas as pd
import pytest

from src.analyzer import AnalysisResult
from src.llm_service import (
    LLMAnalysisPlan,
    LLMInsight,
    LLMServiceError,
    build_schema_payload,
    generate_ai_insight,
    generate_insight_with_optional_llm,
    interpret_question_with_llm,
    parse_question_with_optional_llm,
)
from src.question_parser import QuestionParseError


class FakeResponses:
    """Fake Responses API used without network access."""

    def __init__(self, parsed_outputs: list[object | None]):
        self.parsed_outputs = iter(parsed_outputs)
        self.call_count = 0

    def parse(self, **_: object) -> SimpleNamespace:
        self.call_count += 1

        return SimpleNamespace(
            output_parsed=next(self.parsed_outputs)
        )


class FakeClient:
    """Fake OpenAI client containing a responses service."""

    def __init__(self, parsed_outputs: list[object | None]):
        self.responses = FakeResponses(parsed_outputs)


@pytest.fixture
def sample_dataframe() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "region": ["East", "West"],
            "revenue": [300.0, 250.0],
            "units_sold": [4, 3],
        }
    )


def test_schema_payload_contains_names_and_types(
    sample_dataframe: pd.DataFrame,
) -> None:
    """Schema payload should reflect the DataFrame's actual column types."""
    payload = build_schema_payload(sample_dataframe)

    assert payload == [
        {
            "column_name": "region",
            "data_type": str(
                sample_dataframe["region"].dtype
            ),
        },
        {
            "column_name": "revenue",
            "data_type": str(
                sample_dataframe["revenue"].dtype
            ),
        },
        {
            "column_name": "units_sold",
            "data_type": str(
                sample_dataframe["units_sold"].dtype
            ),
        },
    ]

def test_llm_interprets_broader_question(
    sample_dataframe: pd.DataFrame,
) -> None:
    fake_client = FakeClient(
        [
            LLMAnalysisPlan(
                operation="grouped_mean",
                target_column="revenue",
                group_by="region",
            )
        ]
    )

    parsed = interpret_question_with_llm(
        question="Show me average revenue for each region",
        dataframe=sample_dataframe,
        client=fake_client,
        model="test-model",
    )

    assert parsed.operation == "grouped_mean"
    assert parsed.target_column == "revenue"
    assert parsed.group_by == "region"


def test_unsupported_llm_question_is_rejected(
    sample_dataframe: pd.DataFrame,
) -> None:
    fake_client = FakeClient(
        [
            LLMAnalysisPlan(
                operation="unsupported",
                reason="Forecasting is not supported.",
            )
        ]
    )

    with pytest.raises(
        QuestionParseError,
        match="Forecasting is not supported",
    ):
        interpret_question_with_llm(
            question="Forecast next month's revenue",
            dataframe=sample_dataframe,
            client=fake_client,
            model="test-model",
        )


def test_deterministic_parser_is_used_first(
    sample_dataframe: pd.DataFrame,
) -> None:
    fake_client = FakeClient(
        [
            LLMAnalysisPlan(
                operation="unsupported",
            )
        ]
    )

    parsed, source = parse_question_with_optional_llm(
        question="What is the average revenue?",
        dataframe=sample_dataframe,
        use_llm=True,
        client=fake_client,
        model="test-model",
    )

    assert parsed.operation == "mean"
    assert source == "Deterministic parser"
    assert fake_client.responses.call_count == 0


def test_ai_insight_returns_structured_text() -> None:
    fake_client = FakeClient(
        [
            LLMInsight(
                insight=(
                    "Average revenue in the uploaded data "
                    "was 309.95."
                )
            )
        ]
    )

    result = AnalysisResult(
        operation="mean",
        result_type="scalar",
        title="Average revenue",
        scalar_value=309.955,
    )

    insight = generate_ai_insight(
        analysis_result=result,
        deterministic_insight=(
            "Average revenue is 309.95."
        ),
        client=fake_client,
        model="test-model",
    )

    assert "309.95" in insight


def test_missing_ai_output_uses_deterministic_fallback() -> None:
    fake_client = FakeClient([None])

    result = AnalysisResult(
        operation="mean",
        result_type="scalar",
        title="Average revenue",
        scalar_value=309.955,
    )

    insight, source = generate_insight_with_optional_llm(
        analysis_result=result,
        deterministic_insight=(
            "Average revenue is 309.95."
        ),
        use_llm=True,
        client=fake_client,
        model="test-model",
    )

    assert insight == "Average revenue is 309.95."
    assert source == "Deterministic fallback"


def test_missing_parsed_question_output_raises_error(
    sample_dataframe: pd.DataFrame,
) -> None:
    fake_client = FakeClient([None])

    with pytest.raises(
        LLMServiceError,
        match="returned no structured result",
    ):
        interpret_question_with_llm(
            question="Show revenue by region",
            dataframe=sample_dataframe,
            client=fake_client,
            model="test-model",
        )