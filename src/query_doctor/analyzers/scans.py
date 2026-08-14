from __future__ import annotations

from ..models import Confidence, QueryPlan, Severity
from .base import make_finding


def analyze_sequential_scan_risk(plan: QueryPlan) -> list:
    findings = []
    for node in plan.all_nodes:
        if node.node_type.lower() != "seq scan":
            continue
        actual_rows = node.actual_rows or 0
        removed = node.rows_removed_by_filter or 0
        total_rows = actual_rows + removed
        if total_rows <= 0:
            continue
        runtime = node.runtime.actual_total_time or 0.0
        if actual_rows < 150 and removed < 150 and runtime < 5.0:
            continue
        if actual_rows >= 150 and (removed >= 500 or runtime >= 20.0):
            findings.append(
                make_finding(
                    "QDOC-SCAN-001",
                    "Sequential scan risk",
                    Severity.MEDIUM,
                    Confidence.MEDIUM,
                    node_type=node.node_type,
                    relation=node.relation,
                    evidence=[
                        f"Actual rows returned: {actual_rows}",
                        f"Rows removed by filter: {removed}",
                        f"Actual time: {runtime:.2f} ms",
                    ],
                    explanation=(
                        "This sequential scan is returning a relatively small subset "
                        "of rows from a larger dataset, so the cost may be driven by "
                        "the amount of data touched rather than the final output size."
                    ),
                    recommendation=(
                        "Review whether the predicate is selective enough to deserve "
                        "an index or whether the table is small enough that a scan is "
                        "still reasonable."
                    ),
                    metrics={
                        "actual_rows": actual_rows,
                        "rows_removed": removed,
                        "runtime_ms": round(runtime, 2),
                    },
                )
            )
    return findings
