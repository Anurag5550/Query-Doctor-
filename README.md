# Query Doctor

> PostgreSQL EXPLAIN ANALYZE diagnostics from the command line.

Query Doctor is a Python CLI that inspects PostgreSQL query plans and highlights the patterns most worth investigating: missing-index candidates, suspicious scans, expensive joins, row-estimation mismatches, high filter waste, sort pain, and plan nodes that dominate execution time.

## Overview

When a query is slow, the plan is usually the fastest place to start. Query Doctor parses PostgreSQL `EXPLAIN ANALYZE` output (plain text and JSON) and converts it into a normalized model, then applies a small set of evidence-based heuristics to identify likely performance concerns.

This tool is deliberately conservative. It focuses on patterns that are often meaningful in PostgreSQL and avoids diagnosing certainty where the plan alone cannot establish it.

## Why Query Doctor exists

PostgreSQL plans can be hard to read without a quick pass over the relevant signals:

- a `Seq Scan` on a large table with a highly selective predicate,
- nested loops repeating expensive work,
- large discrepancies between estimated and actual rows,
- sorts spilling to disk,
- expensive filters that reject a large share of rows.

Query Doctor exists to make these clues easier to spot quickly from the command line.

## Features

- Parse PostgreSQL text explain plans and JSON explain plans
- Normalize nested plan trees into a typed internal model
- Detect likely missing-index opportunities
- Flag suspicious sequential scans
- Identify nested loop and join efficiency concerns
- Highlight large estimation mismatches
- Surface filter waste and expensive sorts
- Report plan nodes above a configured cost threshold
- Emit text, JSON, and Markdown output
- Support CLI usage with a simple `query-doctor analyze` flow

## Installation

```bash
python -m pip install -e .
```

For development dependencies:

```bash
python -m pip install -e ".[dev]"
```

## Quick start

```bash
query-doctor analyze tests/fixtures/suspicious_scan.txt
query-doctor analyze tests/fixtures/healthy_plan.txt
query-doctor analyze tests/fixtures/plan.json --format json
query-doctor rules
query-doctor version
```

## Example input

```sql
EXPLAIN (ANALYZE, BUFFERS)
SELECT *
FROM orders
WHERE customer_id = 42;
```

## Example output

```text
Query Doctor 0.1.0
────────────────────────────────────────

Analysis complete

1 findings
0 HIGH
1 MEDIUM
0 LOW

MEDIUM — Sequential scan risk
────────────────────────────────────────
Rule: QDOC-SCAN-001
Relation: orders
Node: Seq Scan

Evidence
• Actual rows returned: 421
• Rows removed by filter: 184923
• Actual time: 42.30 ms

Recommendation
Review whether the predicate is selective enough to deserve an index or whether the table is small enough that a scan is still reasonable.
Confidence: MEDIUM
```

## Supported rules

- QDOC-INDEX-001 — Possible missing index
- QDOC-SCAN-001 — Sequential scan risk
- QDOC-JOIN-001 — Nested loop risk
- QDOC-JOIN-002 — Join efficiency
- QDOC-ESTIMATE-001 — Cardinality estimation mismatch
- QDOC-FILTER-001 — Rows removed by filter
- QDOC-SORT-001 — Expensive sort
- QDOC-SPILL-001 — Disk spill observed
- QDOC-PERF-001 — Expensive node

## CLI reference

```bash
query-doctor --help
query-doctor analyze plan.txt
query-doctor analyze --file plan.txt
cat plan.txt | query-doctor analyze -
query-doctor analyze plan.json --format json
query-doctor analyze plan.txt --format markdown
query-doctor analyze plan.txt --no-color
query-doctor analyze plan.txt --slow-node-ms 100
query-doctor rules
query-doctor version
```

## JSON output

```json
{
  "summary": {
    "findings": 1,
    "high": 0,
    "medium": 1,
    "low": 0
  },
  "findings": []
}
```

## Markdown output

The Markdown renderer is useful for issues, PRs, and docs. It emits a readable summary plus one section per finding.

## Limitations

- Query Doctor is static analysis only.
- It does not execute SQL.
- It does not connect to PostgreSQL.
- It does not prove that a specific index is required.
- It relies on reasoning from observed plan shapes and heuristics.

## Development

```bash
python -m pip install -e ".[dev]"
ruff check .
ruff format --check .
mypy src
pytest
```

## Testing

```bash
pytest
```

## Contributing

Contributions are welcome. Please see [CONTRIBUTING.md](CONTRIBUTING.md) for development setup and the contribution workflow.

## Roadmap

- Expand rule coverage for PostgreSQL-specific patterns
- Improve heuristics based on real-world plan review
- Add richer JSON and Markdown output options
- Support more structured detail in rule explanations

## License

This project is licensed under the MIT License.
