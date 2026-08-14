from __future__ import annotations

from ..models import Confidence, QueryPlan, Severity
from .base import make_finding


def analyze_estimation_mismatch(plan: QueryPlan) -> list:
    findings = []
    for node in plan.all_nodes:
        planned = node.planned_rows or node.cost.planned_rows
        actual = node.actual_rows or node.runtime.actual_rows
        if planned is None or actual is None or planned <= 0:
            continue
        ratio = actual / planned if planned else 0.0
        if ratio >= 5.0:
            findings.append(
                make_finding(
                    "QDOC-ESTIMATE-001",
                    "Cardinality estimation mismatch",
                    Severity.MEDIUM,
                    Confidence.MEDIUM,
                    node_type=node.node_type,
                    relation=node.relation,
                    evidence=[
                        f"Planned rows: {planned}",
                        f"Actual rows: {actual}",
                        f"Mismatch: {ratio:.1f}x",
                    ],
                    explanation=(
                        "The planner estimated a much smaller row count than what "
                        "actually occurred. This can reflect stale statistics, "
                        "skewed data, correlated predicates, or the limits of "
                        "PostgreSQL's estimate for the shape of the query."
                    ),
                    recommendation=(
                        "Investigate whether statistics are stale, whether the data "
                        "distribution is highly skewed, or whether the predicate "
                        "pattern is creating poor estimates."
                    ),
                    metrics={
                        "planned_rows": planned,
                        "actual_rows": actual,
                        "ratio": round(ratio, 2),
                    },
                )
            )
    return findings
