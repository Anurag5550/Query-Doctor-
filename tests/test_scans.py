from query_doctor.analyzers.scans import analyze_sequential_scan_risk
from query_doctor.models import PlanNode, QueryPlan


def test_sequential_scan_risk_is_flagged_when_expensive() -> None:
    plan = QueryPlan(
        root=PlanNode(
            node_type="Seq Scan",
            relation="orders",
            actual_rows=20000,
            rows_removed_by_filter=95000,
            filter_expression="status = 'open'",
            actual_total_time=150.0,
            loops=1,
            children=[],
        )
    )

    findings = analyze_sequential_scan_risk(plan)
    assert findings
    assert findings[0].rule_id == "QDOC-SCAN-001"


def test_small_table_sequential_scan_is_not_flagged() -> None:
    plan = QueryPlan(
        root=PlanNode(
            node_type="Seq Scan",
            relation="orders",
            actual_rows=150,
            rows_removed_by_filter=50,
            filter_expression="status = 'open'",
            actual_total_time=1.0,
            loops=1,
            children=[],
        )
    )

    findings = analyze_sequential_scan_risk(plan)
    assert findings == []
