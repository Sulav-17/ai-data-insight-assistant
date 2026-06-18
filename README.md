# AI Data Insight Assistant

An AI-powered data analysis assistant that will allow users to upload CSV
datasets, inspect their structure, ask natural-language questions, generate
charts, and receive plain-English business insights.

## Project Status

Milestone 1: Project foundation and initial Streamlit application.

The CSV upload, profiling, analysis, visualization, and AI features have not
been implemented yet.

## Problem

Many business users have spreadsheet or CSV data but do not know how to inspect,
analyze, or visualize it with Python.

## Planned Solution

The completed application will provide a controlled workflow for:

- CSV ingestion and validation
- Dataset preview and schema inspection
- Missing-value and duplicate summaries
- Numeric and categorical summaries
- Natural-language analysis questions
- Safe Pandas-based analysis
- Plotly chart generation
- Plain-English business explanations
- Exportable analysis summaries

## Safety Principle

The language model will not be permitted to execute arbitrary Python code.

Pandas will perform deterministic calculations using approved analysis
operations. The language model will only help interpret questions, create
structured plans, and explain verified results.

## Initial Technology Stack

- Python
- Streamlit
- Pandas
- python-dotenv
- pytest

Additional libraries will be introduced only when required.

## Project Structure

```text
ai-data-insight-assistant/
├── app.py
├── src/
│   └── __init__.py
├── prompts/
├── sample_data/
│   └── sales_sample.csv
├── tests/
│   └── test_project_setup.py
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md