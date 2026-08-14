from query_doctor.models import Severity
from query_doctor.parser.text import parse_plan_text


def test_parse_simple_plan() -> None:
    text = """
EXPLAIN (ANALYZE, BUFFERS)
SELECT *
FROM orders
WHERE customer_id = 42;

Seq Scan on orders  (cost=0.00..4312.00 rows=12 width=64)
(actual time=0.020..42.301 rows=421 loops=1)
  Filter: (customer_id = 42)
  Rows Removed by Filter: 184923
""".strip()

    plan = parse_plan_text(text)

    assert plan.query is not None
    assert plan.root.node_type == "Seq Scan"
    assert plan.root.relation == "orders"
    assert plan.root.actual_rows == 421
    assert plan.root.rows_removed_by_filter == 184923
    assert plan.root.filter_expression == "customer_id = 42"
    assert plan.root.cost.total_cost == 4312.0
    assert plan.root.runtime.actual_total_time == 42.301


def test_parse_nested_plan() -> None:
    text = """
Nested Loop  (cost=0.00..241.29 rows=7 width=32)
(actual time=0.049..17.913 rows=12 loops=1)
  ->  Index Scan using idx_orders_customer_id on orders  (cost=0.00..5.41 rows=7 width=32)
        (actual time=0.024..0.381 rows=12 loops=1)
  ->  Index Scan using idx_order_items_order_id on order_items
        (cost=0.00..25.00 rows=1000 width=24)
        (actual time=0.010..0.889 rows=1000 loops=12)
""".strip()

    plan = parse_plan_text(text)
    assert plan.root.node_type == "Nested Loop"
    assert len(plan.root.children) == 2
    assert plan.root.children[0].relation == "orders"
    assert plan.root.children[1].relation == "order_items"


def test_parser_keeps_severity_metadata() -> None:
    assert Severity.HIGH.value == "HIGH"
    assert Severity.MEDIUM.value == "MEDIUM"
