# AI Data Insight Assistant

A safe, explainable CSV analysis application built with Python, Streamlit,
Pandas, and Plotly.

Users can upload a CSV file, inspect its structure, profile data quality, ask
supported natural-language questions, generate charts, receive grounded
plain-English explanations, and export analysis reports.

## Project Status

MVP complete.

The deterministic application works without an AI subscription or API key.

An optional structured LLM layer is included for broader question
interpretation and enhanced wording. The language model never executes Python
code or directly calculates dataset metrics.

## Problem

Non-technical users often receive CSV datasets but do not know how to inspect,
analyze, or visualize them.

Allowing an LLM to freely generate and execute Python creates safety,
correctness, and explainability risks.

## Solution

The application converts supported natural-language questions into validated
analysis plans and executes them through an explicit allowlist of Pandas
operations.

```text
CSV Upload
    ↓
File Validation
    ↓
Pandas Data Loader
    ↓
Dataset Profiling
    ↓
Schema Summary
    ↓
Natural-Language Question
    ↓
Deterministic or Optional AI Interpretation
    ↓
Validated Analysis Plan
    ↓
Safe Pandas Execution
    ↓
Verified Result
    ├── Plotly Chart
    ├── Plain-English Insight
    └── Markdown Report

Features
CSV ingestion
CSV extension validation
Maximum file-size validation
Empty-file detection
Malformed CSV handling
Encoding error handling
Header-only file rejection
Dataset inspection
Dataset preview
Row and column counts
Column names
Pandas data types
Schema summary
Automated profiling
Missing-value counts
Missing-value percentages
Duplicate-row detection
Numeric descriptive statistics
Categorical frequency summaries
Analysis workflow
Suggested analysis questions
Natural-language question parsing
Column-name resolution
Numeric and categorical validation
Structured analysis plans
Approved Pandas operation allowlist
Scalar and tabular results
Supported operations
Mean
Sum
Minimum
Maximum
Grouped mean
Most-common values
Dataset dimensions
Missing-column analysis
Output
Plotly bar charts
Plain-English explanations
Downloadable Markdown reports
Transparent analysis-plan display
Safety
No eval()
No exec()
No arbitrary generated code
Planner validation before execution
Executor validation before calculation
Charts based on verified results
Explanations based on verified results
Optional AI with deterministic fallback
Technology Stack
Python
Streamlit
Pandas
Plotly
Pytest
Python-dotenv
Pydantic
Optional OpenAI SDK
Git and GitHub
Repository Structure
ai-data-insight-assistant/
├── app.py
├── src/
│   ├── analysis_planner.py
│   ├── analyzer.py
│   ├── charts.py
│   ├── data_loader.py
│   ├── insight_generator.py
│   ├── llm_service.py
│   ├── profiler.py
│   ├── question_parser.py
│   ├── question_suggester.py
│   ├── report_generator.py
│   ├── schema.py
│   └── validator.py
├── prompts/
│   ├── analysis_plan.txt
│   └── business_insight.txt
├── sample_data/
│   └── sales_sample.csv
├── tests/
├── docs/
│   ├── architecture.md
│   ├── evaluation.md
│   ├── lessons_learned.md
│   └── portfolio_case_study.md
├── assets/
│   └── screenshots/
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md

Local Installation

Clone the repository:

git clone https://github.com/Sulav-17/ai-data-insight-assistant.git
cd ai-data-insight-assistant

Create a virtual environment:

py -m venv .venv
.\.venv\Scripts\Activate.ps1

Install dependencies:

python -m pip install -r requirements.txt

Run the tests:

python -m pytest -v

Launch the application:

python -m streamlit run app.py
Example Questions
What is the average revenue?
What is the total revenue?
What is the minimum revenue?
What is the maximum revenue?
How does average revenue compare across region?
What are the most common values in category?
How many rows and columns are in the dataset?
Which columns contain missing values?
Optional AI Configuration

The MVP works without an API key.

To enable optional structured AI interpretation, copy .env.example to .env
and add an API key:

OPENAI_API_KEY=your_api_key
OPENAI_MODEL=gpt-5.5

Never commit .env.

Testing

The project includes tests for:

File validation
CSV loading
Schema inspection
Dataset profiling
Question suggestions
Natural-language parsing
Analysis planning
Safe execution
Chart generation
Insight generation
Report generation
Optional LLM integration
End-to-end workflows

Final result:

79 passed

Update this number if your final total differs.

Documentation
Architecture
Evaluation
Lessons Learned
Portfolio Case Study
Current Limitations
Controlled question patterns only
No automatic data cleaning
No forecasting
No anomaly detection
No advanced date analysis
No SQL mode
No multiple-file support
No saved analysis sessions
Future Improvements
Date recognition and time-series analysis
Correlation analysis
Data-cleaning suggestions
Anomaly detection
Forecasting
Read-only SQL mode
PDF report export
Saved analysis sessions
Multiple-file support
Author

Built by Sulav Baral.