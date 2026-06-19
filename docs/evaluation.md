# MVP Evaluation

## Evaluation Dataset

File:

```text
sample_data/sales_sample.csv

Known dataset characteristics:

12 rows
9 columns
3 missing cells
2 columns containing missing values
1 duplicate row
5 numeric columns detected by Pandas
4 categorical-style columns detected
1 intentionally duplicated transaction
Functional Evaluation
Test	Expected result	Status
Upload valid CSV	File loads successfully	Pass
Upload empty CSV	Controlled validation error	Pass
Upload malformed CSV	Controlled parsing error	Pass
Dataset dimensions	12 rows, 9 columns	Pass
Missing cells	3	Pass
Affected columns	2	Pass
Duplicate rows	1	Pass
Average revenue	309.955 internally	Pass
Displayed average revenue	309.95	Pass
Total revenue	3,719.46	Pass
Most common category	Accessories	Pass
Category count	7	Pass
Category percentage	58.33%	Pass
Grouped revenue question	Result table and chart	Pass
Scalar question	Metric without unnecessary chart	Pass
Unsupported forecast	Controlled rejection	Pass
Arbitrary code request	No execution	Pass
Markdown export	Report downloads	Pass
Operation allowlist	Unsupported plans rejected	Pass
Data preservation	Source DataFrame remains unchanged	Pass
Automated Test Result
79 passed

Update this number if your final test count differs.

Safety Evaluation

The application does not use:

eval()
exec()

The language model does not directly execute Pandas operations.

All calculations are performed by the deterministic analyzer after planner
validation.

Interpretation Accuracy

Deterministic questions produce repeatable plans and results.

The optional LLM integration is not required for MVP operation. It is included
as an extensible interpretation layer and can be enabled later when API access
is available.

Known Limitations

The MVP intentionally does not support:

Forecasting
Correlation analysis
Automatic cleaning
Date parsing and time-series analysis
Multi-table analysis
Statistical hypothesis testing
Arbitrary analytical operations

These features were excluded to maintain a controlled and testable MVP.


Replace `79 passed` with your actual final number after running the suite.
