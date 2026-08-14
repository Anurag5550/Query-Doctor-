from __future__ import annotations

from ..config import DEFAULT_CONFIG
from ..models import Confidence, QueryPlan, Severity
from .base import make_finding


def analyze_missing_index(plan: QueryPlan, config=DEFAULT_CONFIG) -> list:
    findings = []
    for node in plan.all_nodes:
        if node.node_type.lower() != "seq scan":
            continue
        relation = node.relation or "unknown"
        actual_rows = node.actual_rows or 0
        removed = node.rows_removed_by_filter or 0
        total_rows = actual_rows + removed
        if total_rows <= 0:
            continue
        selectivity = removed / total_rows
        if actual_rows >= 100 and removed >= 2000 and selectivity >= 0.5:
            candidate = _candidate_from_filter(node.filter_expression, relation)
            evidence = [
                f"Rows removed by filter: {removed}",
                f"Actual rows returned: {actual_rows}",
                f"Filter: {node.filter_expression or 'unavailable'}",
            ]
            findings.append(
                make_finding(
                    "QDOC-INDEX-001",
                    "Possible missing index",
                    Severity.HIGH,
                    Confidence.HIGH,
                    node_type=node.node_type,
                    relation=relation,
                    evidence=evidence,
                    explanation=(
                        "This sequential scan is rejecting a large share of rows "
                        "before returning a small subset. That pattern can "
                        "indicate a missing supporting index for the predicate."
                    ),
                    recommendation=(
                        f"Consider evaluating an index supporting this predicate if "
                        f"the query is frequent and the table is sufficiently large. "
                        f"Potential index candidate: {candidate}"
                    ),
                    metrics={
                        "rows_removed": removed,
                        "actual_rows": actual_rows,
                        "selectivity": round(selectivity, 3),
                    },
                )
            )
    return findings


def _candidate_from_filter(filter_expression: str | None, relation: str) -> str:
    if not filter_expression:
        return f"{relation}(?)"
    expression = filter_expression.strip().strip("()")
    parts = [part.strip() for part in expression.split("AND")]
    column = None
    for part in parts:
        if "=" in part or "IN" in part or "LIKE" in part:
            left, _ = part.split("=", 1) if "=" in part else (part.split()[0], "")
            column = left.strip().strip("() ")
            if column:
                break
    if not column:
        return f"{relation}(?)"
    return f"{relation}({column})"
