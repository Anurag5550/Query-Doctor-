from __future__ import annotations

from ..models import Confidence, QueryPlan, Severity
from .base import make_finding


def analyze_filter_waste(plan: QueryPlan) -> list:
    findings = []
    for node in plan.all_nodes:
        removed = node.rows_removed_by_filter or 0
        actual = node.actual_rows or 0
        if removed <= 0 or actual <= 0:
            continue
        if removed >= 10000 and actual <= 1000:
            findings.append(
                make_finding(
                    "QDOC-FILTER-001",
                    "Rows removed by filter",
                    Severity.LOW,
                    Confidence.MEDIUM,
                    node_type=node.node_type,
                    relation=node.relation,
                    evidence=[
                        f"Rows removed by filter: {removed}",
                        f"Rows returned: {actual}",
                    ],
                    explanation=(
                        "A large share of rows were filtered out after scanning the "
                        "data. That can be a useful clue that a predicate is not "
                        "selective or that an index could help."
                    ),
                    recommendation=(
                        "Consider whether the predicate is sufficiently selective "
                        "and whether a smaller, more targeted access path would "
                        "reduce wasted work."
                    ),
                    metrics={"rows_removed": removed, "rows_returned": actual},
                )
            )
    return findings
