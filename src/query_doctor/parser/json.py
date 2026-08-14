from __future__ import annotations

from typing import Any

from ..models import CostMetrics, PlanNode, QueryPlan, RuntimeMetrics


def parse_plan_json(text: str) -> QueryPlan:
    import json

    data = json.loads(text)
    if isinstance(data, list):
        payload = data[0] if data else {}
    elif isinstance(data, dict):
        payload = data
    else:
        raise ValueError("Unsupported JSON plan payload")
    plan_dict = (
        payload.get("Plan")
        if isinstance(payload, dict)
        else payload.get("Plan")
        if isinstance(payload, dict)
        else None
    )
    if plan_dict is None:
        raise ValueError("No PostgreSQL plan object found in JSON payload.")
    root = _parse_json_node(plan_dict)
    return QueryPlan(root=root, query=None)


def _parse_json_node(node_dict: dict[str, Any]) -> PlanNode:
    cost = CostMetrics(
        startup_cost=_to_float(node_dict.get("Startup Cost")),
        total_cost=_to_float(node_dict.get("Total Cost")),
        planned_rows=_to_int(node_dict.get("Plan Rows")),
        width=_to_int(node_dict.get("Plan Width")),
    )
    runtime = RuntimeMetrics(
        actual_startup_time=_to_float(node_dict.get("Actual Startup Time")),
        actual_total_time=_to_float(node_dict.get("Actual Total Time")),
        actual_rows=_to_int(node_dict.get("Actual Rows")),
        loops=_to_int(node_dict.get("Actual Loops")) or _to_int(node_dict.get(" loops")),
        planning_time=_to_float(node_dict.get("Planning Time")),
        execution_time=_to_float(node_dict.get("Execution Time")),
    )
    filter_expression = _as_str(node_dict.get("Filter"))
    if filter_expression:
        expression = filter_expression.strip()
        while expression.startswith("(") and expression.endswith(")"):
            inner = expression[1:-1].strip()
            if inner == expression:
                break
            expression = inner
        filter_expression = expression
    node = PlanNode(
        node_type=str(node_dict.get("Node Type", "Unknown")),
        relation=_as_str(node_dict.get("Relation Name")) or _as_str(node_dict.get("Table Name")),
        alias=_as_str(node_dict.get("Alias")),
        cost=cost,
        runtime=runtime,
        filter_expression=filter_expression,
        join_condition=_as_str(node_dict.get("Join Filter")),
        rows_removed_by_filter=_to_int(node_dict.get("Rows Removed by Filter")),
        sort_method=_as_str(node_dict.get("Sort Method")),
        memory=_as_str(node_dict.get("Memory")),
        disk=_as_str(node_dict.get("Disk")),
        actual_rows=runtime.actual_rows,
        planned_rows=cost.planned_rows,
        loops=runtime.loops,
    )
    children = node_dict.get("Plans") or []
    for child in children:
        child_node = _parse_json_node(child)
        child_node.parent = node
        node.children.append(child_node)
    return node


def _to_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _to_int(value: Any) -> int | None:
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _as_str(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, str):
        return value.strip()
    return str(value)


__all__ = ["parse_plan_json"]
