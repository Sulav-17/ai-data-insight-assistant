# Lessons Learned

## 1. File uploads must be treated as untrusted input

A CSV extension does not guarantee valid CSV content. Metadata validation and
content parsing must be handled separately.

## 2. Pandas data types are not business meanings

A numeric column such as `order_id` can technically be averaged, but that
calculation is not useful. Analytical systems need both technical type checks
and semantic rules.

## 3. Parsing and execution should be separate

Understanding a question is different from performing an analysis.

Separating the parser, planner, and executor made the workflow safer and easier
to test.

## 4. LLMs should not directly execute generated code

The safer architecture is:

```text
Natural language
    → structured operation
    → validation
    → approved deterministic execution

This avoids arbitrary code execution and improves repeatability.

5. Charts must come from verified results

The chart generator should visualize the analyzer's result rather than
recalculate data independently.

This keeps one source of truth.

6. Explanations must remain grounded

A dataset may show that one group has a higher average than another, but it
does not automatically explain why.

The insight generator reports observed values without claiming causation.

7. Missing values and duplicates should not be silently removed

Data-quality problems can have different business meanings. The application
reports them but leaves cleaning decisions to the user.

8. Tests should verify real analytical values

Checking only that a function returns a DataFrame is not enough.

Tests should verify known results such as:

Average revenue
Total revenue
Missing-value counts
Category frequencies
Grouped averages
9. Optional AI should fail gracefully

The deterministic system remains functional when API credentials, quota, or
network access are unavailable.

This makes the AI layer an enhancement instead of a single point of failure.

10. Pandas versions can change inferred data types

Pandas 3 may report string columns as str instead of the older object
representation.

Tests should verify actual behavior rather than unnecessarily hard-coding
version-specific details.