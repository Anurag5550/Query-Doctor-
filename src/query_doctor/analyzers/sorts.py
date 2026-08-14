from __future__ import annotations

from ..models import Confidence, QueryPlan, Severity
from .base import make_finding


def analyze_expensive_sort(plan: QueryPlan) -> list:
    findings = []
    for node in plan.all_nodes:
        if node.node_type.lower() != "sort":
            continue
        runtime = node.runtime.actual_total_time or 0.0
        rows = node.actual_rows or 0
        if runtime >= 30.0 and rows >= 1000:
            findings.append(
                make_finding(
                    "QDOC-SORT-001",
                    "Expensive sort",
                    Severity.MEDIUM,
                    Confidence.MEDIUM,
                    node_type=node.node_type,
                    relation=node.relation,
                    evidence=[
                        f"Rows sorted: {rows}",
                        f"Actual time: {runtime:.2f} ms",
                        f"Sort method: {node.sort_method or 'unknown'}",
                    ],
                    explanation=(
                        "This sort is taking a meaningful portion of total execution "
                        "time, which suggests it may be driving a substantial amount "
                        "of query work."
                    ),
                    recommendation=(
                        "Review the sort key, whether the sort can be avoided with an "
                        "index, and whether the query shape is causing an "
                        "unexpectedly large sort."
                    ),
                    metrics={"rows": rows, "runtime_ms": round(runtime, 2)},
                )
            )
    return findings


def analyze_disk_spill(plan: QueryPlan) -> list:
    findings = []
    for node in plan.all_nodes:
        if node.node_type.lower() != "sort":
            continue
        disk = node.disk or ""
        sort_method = node.sort_method or ""
        if (
            "external merge" in sort_method.lower()
            or "disk" in disk.lower()
            or "temp" in disk.lower()
        ):
            findings.append(
                make_finding(
                    "QDOC-SPILL-001",
                    "Disk spill observed",
                    Severity.MEDIUM,
                    Confidence.HIGH,
                    node_type=node.node_type,
                    relation=node.relation,
                    evidence=[
                        f"Sort method: {sort_method or 'unknown'}",
                        f"Disk information: {disk or 'not reported'}",
                    ],
                    explanation=(
                        "The sort is spilling to disk, which often means the sorted "
                        "data exceeds memory available to the node. This can become a "
                        "bottleneck when the query is large."
                    ),
                    recommendation=(
                        "Investigate sort size, query shape, index support, and "
                        "memory settings. A wide sort or a large working set can "
                        "produce spill even when the plan is otherwise reasonable."
                    ),
                    metrics={
                        "sort_method": sort_method or "unknown",
                        "disk": disk or "not reported",
                    },
                )
            )
    return findings
