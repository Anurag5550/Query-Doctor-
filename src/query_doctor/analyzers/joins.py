from __future__ import annotations

from ..models import Confidence, QueryPlan, Severity
from .base import make_finding


def analyze_nested_loop_risk(plan: QueryPlan) -> list:
    findings = []
    for node in plan.all_nodes:
        if node.node_type.lower() != "nested loop":
            continue
        loops = node.loops or 1
        actual_rows = node.actual_rows or 0
        runtime = node.runtime.actual_total_time or 0.0
        if runtime >= 30.0 and loops > 1 or actual_rows >= 1000 and runtime >= 20.0:
            findings.append(
                make_finding(
                    "QDOC-JOIN-001",
                    "Nested loop risk",
                    Severity.MEDIUM,
                    Confidence.MEDIUM,
                    node_type=node.node_type,
                    relation=node.relation,
                    evidence=[
                        f"Loops: {loops}",
                        f"Actual rows: {actual_rows}",
                        f"Actual time: {runtime:.2f} ms",
                    ],
                    explanation=(
                        "This nested loop is repeatedly executing a substantial amount "
                        "of work, which can become expensive when the inner side is "
                        "large or the join condition is not selective."
                    ),
                    recommendation=(
                        "Check whether the join predicate is selective, whether an "
                        "index is missing on the inner side, and whether the planner "
                        "is choosing a more efficient join type for this data "
                        "distribution."
                    ),
                    metrics={
                        "loops": loops,
                        "actual_rows": actual_rows,
                        "runtime_ms": round(runtime, 2),
                    },
                )
            )
    return findings


def analyze_join_efficiency(plan: QueryPlan) -> list:
    findings = []
    for node in plan.all_nodes:
        if node.node_type.lower() not in {"nested loop", "hash join", "merge join"}:
            continue
        actual_rows = node.actual_rows or 0
        runtime = node.runtime.actual_total_time or 0.0
        if actual_rows >= 5000 and runtime >= 50.0:
            findings.append(
                make_finding(
                    "QDOC-JOIN-002",
                    "Join efficiency",
                    Severity.LOW,
                    Confidence.MEDIUM,
                    node_type=node.node_type,
                    relation=node.relation,
                    evidence=[
                        f"Join rows: {actual_rows}",
                        f"Actual time: {runtime:.2f} ms",
                    ],
                    explanation=(
                        "This join is producing or processing a large number of rows, "
                        "which may indicate a suboptimal join order or a plan that is "
                        "expensive for the data distribution being tested."
                    ),
                    recommendation=(
                        "Review the join order, predicate selectivity, and whether a "
                        "different join strategy or supporting index could reduce work."
                    ),
                    metrics={
                        "actual_rows": actual_rows,
                        "runtime_ms": round(runtime, 2),
                    },
                )
            )
    return findings
