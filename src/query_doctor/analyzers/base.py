from __future__ import annotations

from ..models import Confidence, Finding, PlanNode, QueryPlan, Severity


def iter_nodes(plan: QueryPlan) -> list[PlanNode]:
    return plan.all_nodes


def make_finding(
    rule_id: str,
    title: str,
    severity: Severity,
    confidence: Confidence,
    *,
    node_type: str | None = None,
    relation: str | None = None,
    evidence: list[str] | None = None,
    explanation: str = "",
    recommendation: str = "",
    metrics: dict[str, float | int | str | None] | None = None,
) -> Finding:
    return Finding(
        rule_id=rule_id,
        title=title,
        severity=severity,
        confidence=confidence,
        node_type=node_type,
        relation=relation,
        evidence=evidence or [],
        explanation=explanation,
        recommendation=recommendation,
        metrics=metrics or {},
    )


def severity_rank(severity: Severity) -> int:
    order = {
        Severity.INFO: 0,
        Severity.LOW: 1,
        Severity.MEDIUM: 2,
        Severity.HIGH: 3,
        Severity.CRITICAL: 4,
    }
    return order.get(severity, 0)
