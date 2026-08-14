from __future__ import annotations

from ..config import DEFAULT_CONFIG
from ..models import Confidence, QueryPlan, Severity
from .base import make_finding


def analyze_expensive_nodes(
    plan: QueryPlan,
    slow_node_ms: float = DEFAULT_CONFIG.slow_node_ms,
) -> list:
    findings = []
    for node in plan.all_nodes:
        runtime = node.runtime.actual_total_time or 0.0
        if runtime >= slow_node_ms:
            findings.append(
                make_finding(
                    "QDOC-PERF-001",
                    "Expensive node",
                    Severity.LOW,
                    Confidence.MEDIUM,
                    node_type=node.node_type,
                    relation=node.relation,
                    evidence=[
                        f"Node type: {node.node_type}",
                        f"Actual time: {runtime:.2f} ms",
                    ],
                    explanation=(
                        "This plan node is consuming a large amount of execution time "
                        "compared with the configured threshold. It may be a useful "
                        "place to focus further investigation."
                    ),
                    recommendation=(
                        "Inspect the node in context to see whether its cost comes "
                        "from row count, expensive predicates, or a missing index."
                    ),
                    metrics={
                        "runtime_ms": round(runtime, 2),
                        "threshold_ms": slow_node_ms,
                    },
                )
            )
    return findings
