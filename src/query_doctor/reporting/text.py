from __future__ import annotations

from collections.abc import Iterable

from ..models import Finding


def render_text(findings: Iterable[Finding], *, no_color: bool = False) -> str:
    items = list(findings)
    if not items:
        return "\n".join(
            [
                "Query Doctor 0.1.0",
                "────────────────────────────────────────",
                "",
                "Analysis complete",
                "",
                "0 findings",
                "",
                "✓ No major performance issues detected.",
                "",
                "No high-confidence optimization signals were found",
                "using the enabled Query Doctor heuristics.",
            ]
        )

    summary = _summarize(items)
    lines = [
        "Query Doctor 0.1.0",
        "────────────────────────────────────────",
        "",
        "Analysis complete",
        "",
        f"{len(items)} findings",
        f"{summary['HIGH']} HIGH",
        f"{summary['MEDIUM']} MEDIUM",
        f"{summary['LOW']} LOW",
        "",
    ]
    for finding in items:
        lines.extend(_render_finding(finding))
    return "\n".join(lines)


def _render_finding(finding: Finding) -> list[str]:
    lines = [
        f"{finding.severity.value} — {finding.title}",
        "────────────────────────────────────────",
        f"Rule: {finding.rule_id}",
    ]
    if finding.relation:
        lines.append(f"Relation: {finding.relation}")
    if finding.node_type:
        lines.append(f"Node: {finding.node_type}")
    if finding.evidence:
        lines.append("")
        lines.append("Evidence")
        for item in finding.evidence:
            lines.append(f"• {item}")
    if finding.explanation:
        lines.append("")
        lines.append("Explanation")
        lines.append(finding.explanation)
    if finding.recommendation:
        lines.append("")
        lines.append("Recommendation")
        lines.append(finding.recommendation)
    lines.append(f"Confidence: {finding.confidence.value}")
    lines.append("")
    return lines


def _summarize(findings: list[Finding]) -> dict[str, int]:
    summary = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}
    for finding in findings:
        summary[finding.severity.value] = summary.get(finding.severity.value, 0) + 1
    return summary
