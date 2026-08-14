from __future__ import annotations

import json

from ..models import Finding


def render_json(findings: list[Finding]) -> str:
    payload = {
        "summary": {
            "findings": len(findings),
            "high": sum(1 for f in findings if f.severity.value == "HIGH"),
            "medium": sum(1 for f in findings if f.severity.value == "MEDIUM"),
            "low": sum(1 for f in findings if f.severity.value == "LOW"),
        },
        "findings": [
            {
                "rule_id": item.rule_id,
                "title": item.title,
                "severity": item.severity.value,
                "confidence": item.confidence.value,
                "node_type": item.node_type,
                "relation": item.relation,
                "evidence": item.evidence,
                "explanation": item.explanation,
                "recommendation": item.recommendation,
                "metrics": item.metrics,
            }
            for item in findings
        ],
    }
    return json.dumps(payload, indent=2)
