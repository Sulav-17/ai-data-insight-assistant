# AI Data Insight Assistant Architecture

## Overview

The AI Data Insight Assistant converts uploaded CSV datasets into validated,
explainable analysis results.

The application separates file handling, data profiling, question
interpretation, analysis planning, execution, visualization, explanation, and
report generation into independent components.

## Data Flow

```text
CSV Upload
    ↓
File Metadata Validation
    ↓
Pandas CSV Loader
    ↓
Dataset Preview and Schema Inspection
    ↓
Automated Dataset Profiling
    ↓
Suggested Analysis Questions
    ↓
Natural-Language Question
    ↓
Deterministic Parser
    ↓
Optional Structured LLM Interpreter
    ↓
Validated Analysis Plan
    ↓
Approved Pandas Executor
    ↓
Verified Scalar or Tabular Result
    ├── Plotly Chart
    ├── Plain-English Insight
    └── Markdown Report

Components
validator.py

Validates file metadata before Pandas attempts to load the file.

Checks include:

CSV file extension
Empty-file detection
Maximum file size
data_loader.py

Loads valid CSV content into a Pandas DataFrame.

It handles:

Empty content
Malformed CSV content
Unsupported encoding
Header-only files
schema.py

Provides:

Row count
Column count
Dataset preview
Column names
Pandas data types
profiler.py

Calculates deterministic exploratory summaries:

Missing-value counts and percentages
Duplicate-row counts
Numeric descriptive statistics
Categorical frequency summaries
question_suggester.py

Generates suggested questions from the actual dataset schema.

It excludes:

Obvious identifier columns
High-cardinality categorical columns
Metrics that do not exist in the dataset
question_parser.py

Converts supported natural-language patterns into structured questions.

Example:

What is the average revenue?

becomes:

operation: mean
target_column: revenue
llm_service.py

Provides an optional structured LLM interpretation layer.

The LLM may suggest an approved operation and column names, but it cannot
execute code or directly calculate metrics.

The application remains functional without an API key.

analysis_planner.py

Validates whether a parsed request is permitted for the uploaded dataset.

Examples:

Mean requires a numeric target column.
Grouped mean requires a numeric target and categorical grouping column.
Unsupported operations are rejected.
analyzer.py

Executes an explicit allowlist of Pandas operations:

Mean
Sum
Minimum
Maximum
Grouped mean
Most-common values
Dataset dimensions
Missing-column summary

No eval() or exec() operations are used.

charts.py

Creates Plotly charts only for supported tabular results.

Scalar results do not receive decorative or misleading charts.

insight_generator.py

Creates deterministic plain-English summaries from verified analysis results.

It does not:

Invent metrics
Claim causation
Make predictions
Generate unsupported recommendations
report_generator.py

Exports:

User question
Validated plan
Verified result
Plain-English explanation
Safety methodology

as a Markdown report.

Safety Model

The system follows defence in depth:

The parser recognizes supported language.
The planner validates analytical intent.
The executor validates columns and operations again.
Calculations are performed only through approved Pandas functions.
Charts use verified result tables.
Insights summarize verified results.
The optional LLM cannot execute code.
Data Privacy

The deterministic workflow runs locally.

When optional AI interpretation is enabled:

The question interpreter receives schema information.
The explanation layer receives the verified analysis result.
The full uploaded DataFrame is not required for question interpretation.
Current Limitations
Limited deterministic question patterns
No automatic data cleaning
No date-series analysis
No forecasting
No anomaly detection
No SQL mode
No multi-file support
No saved analysis sessions