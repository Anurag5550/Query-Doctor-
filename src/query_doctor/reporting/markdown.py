from __future__ import annotations

from ..models import Finding


def render_markdown(findings: list[Finding]) -> str:
    if not findings:
        return (
            "# Query Doctor\n\n"
            "✓ No major performance issues detected.\n\n"
            "No high-confidence optimization signals were found using the enabled "
            "Query Doctor heuristics.\n"
        )
    lines = ["# Query Doctor", "", f"Found {len(findings)} possible issues.", ""]
    for finding in findings:
        lines.append(f"## {finding.severity.value} — {finding.title}")
        lines.append("")
        lines.append(f"- Rule: `{finding.rule_id}`")
        if finding.relation:
            lines.append(f"- Relation: `{finding.relation}`")
        if finding.node_type:
            lines.append(f"- Node: `{finding.node_type}`")
        lines.append("")
        lines.append("### Evidence")
        for item in finding.evidence:
            lines.append(f"- {item}")
        lines.append("")
        lines.append("### Recommendation")
        lines.append(finding.recommendation)
        lines.append("")
    return "\n".join(lines)
