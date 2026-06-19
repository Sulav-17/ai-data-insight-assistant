import re
from dataclasses import dataclass

import pandas as pd

from src.question_suggester import humanize_column_name


class QuestionParseError(ValueError):
    """Raised when a natural-language question cannot be parsed."""


@dataclass(frozen=True)
class ParsedQuestion:
    """Structured representation of a supported user question."""

    operation: str
    target_column: str | None = None
    group_by: str | None = None


def normalize_text(value: str) -> str:
    """
    Normalize user-entered text for predictable matching.

    The function:
    - converts text to lowercase
    - removes surrounding whitespace
    - removes ending punctuation
    - collapses repeated spaces
    """
    normalized = str(value).strip().lower()
    normalized = normalized.rstrip("?.!")
    normalized = re.sub(r"\s+", " ", normalized)

    return normalized


def build_column_aliases(
    dataframe: pd.DataFrame,
) -> dict[str, str]:
    """
    Build readable aliases for every DataFrame column.

    Example:
        "units_sold" and "units sold" both map to "units_sold".
    """
    aliases: dict[str, str] = {}

    for column_name in dataframe.columns:
        original_name = str(column_name)
        readable_name = humanize_column_name(original_name)

        aliases[normalize_text(original_name)] = original_name
        aliases[normalize_text(readable_name)] = original_name

    return aliases


def resolve_column_name(
    column_text: str,
    dataframe: pd.DataFrame,
) -> str:
    """
    Resolve user-entered column text to an actual DataFrame column.

    Raises:
        QuestionParseError: If the column cannot be found.
    """
    aliases = build_column_aliases(dataframe)
    normalized_column = normalize_text(column_text)

    if normalized_column not in aliases:
        raise QuestionParseError(
            f"Column '{column_text.strip()}' was not found "
            "in the uploaded dataset."
        )

    return aliases[normalized_column]


def parse_question(
    question: str,
    dataframe: pd.DataFrame,
) -> ParsedQuestion:
    """
    Parse a supported natural-language question.

    Args:
        question: Question entered by the user.
        dataframe: Dataset whose column names are available.

    Returns:
        A structured ParsedQuestion.

    Raises:
        QuestionParseError: If the question is empty or unsupported.
    """
    normalized_question = normalize_text(question)

    if not normalized_question:
        raise QuestionParseError(
            "Enter a question before creating an analysis plan."
        )

    if normalized_question == (
        "how many rows and columns are in the dataset"
    ):
        return ParsedQuestion(
            operation="dataset_shape",
        )

    if normalized_question == (
        "which columns contain missing values"
    ):
        return ParsedQuestion(
            operation="missing_columns",
        )

    grouped_average_match = re.fullmatch(
        r"how does average (.+?) compare across (.+)",
        normalized_question,
    )

    if grouped_average_match:
        target_text = grouped_average_match.group(1)
        group_text = grouped_average_match.group(2)

        return ParsedQuestion(
            operation="grouped_mean",
            target_column=resolve_column_name(
                target_text,
                dataframe,
            ),
            group_by=resolve_column_name(
                group_text,
                dataframe,
            ),
        )

    most_common_match = re.fullmatch(
        r"what are the most common values in (.+)",
        normalized_question,
    )

    if most_common_match:
        target_text = most_common_match.group(1)

        return ParsedQuestion(
            operation="most_common",
            target_column=resolve_column_name(
                target_text,
                dataframe,
            ),
        )

    numeric_match = re.fullmatch(
        (
            r"what is the "
            r"(average|mean|total|sum|minimum|min|maximum|max) "
            r"(?:of )?(.+)"
        ),
        normalized_question,
    )

    if numeric_match:
        requested_operation = numeric_match.group(1)
        target_text = numeric_match.group(2)

        operation_aliases = {
            "average": "mean",
            "mean": "mean",
            "total": "sum",
            "sum": "sum",
            "minimum": "min",
            "min": "min",
            "maximum": "max",
            "max": "max",
        }

        return ParsedQuestion(
            operation=operation_aliases[requested_operation],
            target_column=resolve_column_name(
                target_text,
                dataframe,
            ),
        )

    raise QuestionParseError(
        "This question format is not currently supported. "
        "Try one of the suggested analysis questions."
    )