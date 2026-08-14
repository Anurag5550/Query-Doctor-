from query_doctor.analyzers.indexes import analyze_missing_index
from query_doctor.models import PlanNode, QueryPlan


def test_strong_missing_index_candidate() -> None:
    plan = QueryPlan(
        root=PlanNode(
            node_type="Seq Scan",
            relation="orders",
            actual_rows=421,
            rows_removed_by_filter=184923,
            filter_expression="customer_id = 42",
            children=[],
        )
    )

    findings = analyze_missing_index(plan)
    assert findings
    assert findings[0].rule_id == "QDOC-INDEX-001"
    assert "orders(customer_id)" in findings[0].recommendation


def test_small_table_does_not_trigger_index_warning() -> None:
    plan = QueryPlan(
        root=PlanNode(
            node_type="Seq Scan",
            relation="orders",
            actual_rows=120,
            rows_removed_by_filter=200,
            filter_expression="customer_id = 42",
            children=[],
        )
    )

    findings = analyze_missing_index(plan)
    assert findings == []
