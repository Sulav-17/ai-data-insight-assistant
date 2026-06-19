import json
import os
from pathlib import Path
from typing import Any, Literal

import pandas as pd
from openai import OpenAI, OpenAIError
from pydantic import BaseModel, Field

from src.analyzer import AnalysisResult
from src.question_parser import (
    ParsedQuestion,
    QuestionParseError,
    parse_question,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROMPTS_DIRECTORY = PROJECT_ROOT / "prompts"

DEFAULT_OPENAI_MODEL = "gpt-5.5"


class LLMServiceError(RuntimeError):
    """Raised when the optional LLM service cannot complete a request."""


class LLMAnalysisPlan(BaseModel):
    """Structured operation returned by the language model."""

    operation: Literal[
        "dataset_shape",
        "missing_columns",
        "mean",
        "sum",
        "min",
        "max",
        "grouped_mean",
        "most_common",
        "unsupported",
    ]

    target_column: str | None = None
    group_by: str | None = None
    reason: str | None = None


class LLMInsight(BaseModel):
    """Structured business explanation returned by the language model."""

    insight: str = Field(
        min_length=1,
        max_length=1_200,
    )


def load_prompt(file_name: str) -> str:
    """Load a reusable prompt template from the prompts directory."""
    prompt_path = PROMPTS_DIRECTORY / file_name

    if not prompt_path.exists():
        raise LLMServiceError(
            f"Prompt file '{file_name}' could not be found."
        )

    prompt_text = prompt_path.read_text(
        encoding="utf-8"
    ).strip()

    if not prompt_text:
        raise LLMServiceError(
            f"Prompt file '{file_name}' is empty."
        )

    return prompt_text


def is_llm_configured() -> bool:
    """Return whether an OpenAI API key is available."""
    return bool(os.getenv("OPENAI_API_KEY", "").strip())


def get_model_name() -> str:
    """Return the configured OpenAI model name."""
    return (
        os.getenv(
            "OPENAI_MODEL",
            DEFAULT_OPENAI_MODEL,
        ).strip()
        or DEFAULT_OPENAI_MODEL
    )


def create_openai_client() -> OpenAI:
    """Create an OpenAI client using the environment API key."""
    api_key = os.getenv("OPENAI_API_KEY", "").strip()

    if not api_key:
        raise LLMServiceError(
            "OPENAI_API_KEY is not configured."
        )

    return OpenAI(api_key=api_key)


def build_schema_payload(
    dataframe: pd.DataFrame,
) -> list[dict[str, str]]:
    """Create a small schema payload without sending dataset rows."""
    return [
        {
            "column_name": str(column_name),
            "data_type": str(dataframe[column_name].dtype),
        }
        for column_name in dataframe.columns
    ]


def interpret_question_with_llm(
    question: str,
    dataframe: pd.DataFrame,
    client: Any | None = None,
    model: str | None = None,
) -> ParsedQuestion:
    """
    Interpret a question using structured LLM output.

    The LLM returns only an approved operation and column names.
    It does not generate or execute code.
    """
    cleaned_question = question.strip()

    if not cleaned_question:
        raise QuestionParseError(
            "Enter a question before requesting AI interpretation."
        )

    service_client = client or create_openai_client()
    selected_model = model or get_model_name()
    system_prompt = load_prompt("analysis_plan.txt")

    request_payload = {
        "question": cleaned_question,
        "dataset_schema": build_schema_payload(dataframe),
    }

    try:
        response = service_client.responses.parse(
            model=selected_model,
            input=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": json.dumps(
                        request_payload,
                        indent=2,
                    ),
                },
            ],
            text_format=LLMAnalysisPlan,
        )

    except OpenAIError as error:
        raise LLMServiceError(
            "The AI question interpreter could not complete "
            "the request."
        ) from error

    parsed_output = response.output_parsed

    if parsed_output is None:
        raise LLMServiceError(
            "The AI question interpreter returned no "
            "structured result."
        )

    if parsed_output.operation == "unsupported":
        raise QuestionParseError(
            parsed_output.reason
            or (
                "The AI interpreter could not map this question "
                "to a supported analysis operation."
            )
        )

    return ParsedQuestion(
        operation=parsed_output.operation,
        target_column=parsed_output.target_column,
        group_by=parsed_output.group_by,
    )


def parse_question_with_optional_llm(
    question: str,
    dataframe: pd.DataFrame,
    use_llm: bool,
    client: Any | None = None,
    model: str | None = None,
) -> tuple[ParsedQuestion, str]:
    """
    Use deterministic parsing first and LLM interpretation only as fallback.
    """
    try:
        parsed_question = parse_question(
            question,
            dataframe,
        )

        return parsed_question, "Deterministic parser"

    except QuestionParseError:
        if not use_llm:
            raise

    parsed_question = interpret_question_with_llm(
        question=question,
        dataframe=dataframe,
        client=client,
        model=model,
    )

    return parsed_question, "Structured AI interpreter"


def serialize_analysis_result(
    analysis_result: AnalysisResult,
) -> dict[str, object]:
    """Serialize a verified result for safe LLM explanation."""
    if analysis_result.result_type == "scalar":
        return {
            "operation": analysis_result.operation,
            "title": analysis_result.title,
            "result_type": "scalar",
            "value": analysis_result.scalar_value,
        }

    if analysis_result.result_type == "table":
        result_table = analysis_result.table

        return {
            "operation": analysis_result.operation,
            "title": analysis_result.title,
            "result_type": "table",
            "rows": (
                []
                if result_table is None
                else result_table.head(20).to_dict(
                    orient="records"
                )
            ),
        }

    raise LLMServiceError(
        "The analysis result type cannot be serialized."
    )


def generate_ai_insight(
    analysis_result: AnalysisResult,
    deterministic_insight: str,
    client: Any | None = None,
    model: str | None = None,
) -> str:
    """
    Ask the LLM to rewrite an already verified explanation.

    The LLM does not receive the original DataFrame and does not
    perform the calculation.
    """
    service_client = client or create_openai_client()
    selected_model = model or get_model_name()
    system_prompt = load_prompt("business_insight.txt")

    request_payload = {
        "verified_result": serialize_analysis_result(
            analysis_result
        ),
        "deterministic_explanation": deterministic_insight,
    }

    try:
        response = service_client.responses.parse(
            model=selected_model,
            input=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": json.dumps(
                        request_payload,
                        indent=2,
                        default=str,
                    ),
                },
            ],
            text_format=LLMInsight,
        )

    except OpenAIError as error:
        raise LLMServiceError(
            "The AI insight generator could not complete "
            "the request."
        ) from error

    parsed_output = response.output_parsed

    if parsed_output is None:
        raise LLMServiceError(
            "The AI insight generator returned no "
            "structured result."
        )

    return parsed_output.insight.strip()


def generate_insight_with_optional_llm(
    analysis_result: AnalysisResult,
    deterministic_insight: str,
    use_llm: bool,
    client: Any | None = None,
    model: str | None = None,
) -> tuple[str, str]:
    """Generate an AI insight or safely fall back to deterministic text."""
    if not use_llm:
        return (
            deterministic_insight,
            "Deterministic explanation",
        )

    try:
        ai_insight = generate_ai_insight(
            analysis_result=analysis_result,
            deterministic_insight=deterministic_insight,
            client=client,
            model=model,
        )

    except LLMServiceError:
        return (
            deterministic_insight,
            "Deterministic fallback",
        )

    return ai_insight, "AI-enhanced explanation"