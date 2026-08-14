from query_doctor.parser.json import parse_plan_json


def test_parse_json_plan() -> None:
    text = """
[
  {
    "Plan": {
      "Node Type": "Seq Scan",
      "Relation Name": "orders",
      "Alias": "orders",
      "Actual Rows": 421,
      "Actual Total Time": 42.301,
      "Rows Removed by Filter": 184923,
      "Filter": "(customer_id = 42)",
      "Total Cost": 4312.0,
      "Plan Rows": 12,
      "Plan Width": 64,
      "Plans": []
    }
  }
]
""".strip()

    plan = parse_plan_json(text)
    assert plan.root.node_type == "Seq Scan"
    assert plan.root.relation == "orders"
    assert plan.root.actual_rows == 421
    assert plan.root.rows_removed_by_filter == 184923
    assert plan.root.filter_expression == "customer_id = 42"
