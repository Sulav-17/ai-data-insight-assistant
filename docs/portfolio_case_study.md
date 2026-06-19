# AI Data Insight Assistant

## Problem

Many business users receive CSV files containing useful operational or sales
data but do not know how to inspect, analyze, or visualize the information
using Python.

Existing conversational AI approaches may generate and execute arbitrary code,
which creates reliability, security, and explainability risks.

## Solution

I built a Streamlit-based data analysis assistant that allows users to upload a
CSV file, inspect its structure, profile data quality, ask supported
natural-language questions, generate charts, receive plain-English
explanations, and export analysis reports.

The system converts questions into structured analysis plans and executes only
approved Pandas operations. It does not run arbitrary model-generated Python
code.

## Technology Stack

- Python
- Streamlit
- Pandas
- Plotly
- Pytest
- Python-dotenv
- Pydantic
- Optional OpenAI integration
- Git and GitHub

## Architecture

```text
CSV Upload
    → Validation
    → Pandas DataFrame
    → Dataset Profiling
    → Schema-Aware Question Parsing
    → Validated Analysis Plan
    → Safe Pandas Execution
    → Result Table or Metric
    → Plotly Chart
    → Plain-English Insight
    → Markdown Export
Key Features
CSV validation and controlled error handling
Dataset preview and schema inspection
Missing-value and duplicate-row detection
Numeric descriptive statistics
Categorical frequency summaries
Schema-based question suggestions
Natural-language question parsing
Approved-operation analysis allowlist
Plotly chart generation
Grounded plain-English explanations
Downloadable Markdown reports
Optional structured LLM interpretation
Deterministic fallback when API access is unavailable
Comprehensive automated test coverage
Safety Design

The language model does not execute code or calculate metrics.

All questions are converted into structured operations and validated before
execution. The analyzer performs calculations through an explicit allowlist of
Pandas operations.

This design prevents arbitrary generated code from being passed to eval() or
exec().

Challenges

The hardest part was separating natural-language understanding from safe
execution.

A user may ask a reasonable-sounding question that is invalid for the
dataset—for example, requesting the average of a text column. The architecture
therefore uses separate parser, planner, and executor layers, each with its own
validation responsibilities.

Another challenge was handling Pandas-version differences in inferred text
data types while keeping tests reliable.

Results

The completed MVP:

Processes a validated CSV dataset
Reports dataset structure and quality
Produces repeatable analytical results
Generates charts from verified result tables
Explains results without inventing unsupported conclusions
Exports reusable Markdown reports
Passes 79 automated tests

Update the test count if the final number differs.

Limitations

The current MVP supports a controlled set of analytical operations.

It does not yet include:

Forecasting
Anomaly detection
Automated data cleaning
Advanced date analysis
SQL mode
Multiple-file joins
Saved user sessions
Future Improvements

Potential future additions include:

Date-column recognition and time-series analysis
Correlation analysis
Cleaning recommendations
Anomaly detection
Forecasting
Read-only SQL analysis
Saved analysis sessions
Multi-file support
Downloadable PDF reports