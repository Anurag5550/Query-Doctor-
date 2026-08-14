# Architecture

Query Doctor follows a straightforward pipeline:

1. A plan is read from text or JSON.
2. The parser produces a normalized plan tree.
3. Heuristic analyzers inspect that normalized model.
4. Findings are rendered as text, JSON, or Markdown.

## Parser layer

The parser package is intentionally limited to understanding input formats. It should not contain reporting decisions or policy-specific recommendations.

- `parser/text.py` handles PostgreSQL `EXPLAIN ANALYZE` text output.
- `parser/json.py` handles `EXPLAIN (ANALYZE, FORMAT JSON)` output.

Both produce the same `QueryPlan` and `PlanNode` model.

## Model layer

Typed dataclasses in `models.py` represent the plan structure and findings. This keeps the rest of the project decoupled from raw text parsing and output formatting.

The main model objects are:

- `QueryPlan`
- `PlanNode`
- `CostMetrics`
- `RuntimeMetrics`
- `Finding`
- `Recommendation`

## Analyzer layer

The analyzer modules read normalized nodes and apply cognitively useful heuristics.

These rules intentionally avoid certainty claims. Instead, they explain that a pattern may indicate a likely issue and recommend an area to investigate.

## Reporting layer

The reporting package converts structured findings to user-facing output:

- text output for terminal usage,
- JSON for automation,
- Markdown for docs, issues, and PR descriptions.

This separation keeps rendering logic independent from parsing and analysis.
