from __future__ import annotations

import re
from typing import Any

from ..models import CostMetrics, PlanNode, QueryPlan, RuntimeMetrics

NODE_PATTERN = re.compile(
    r"^\s*(?:->\s*)?(?P<node>[A-Za-z][A-Za-z0-9 _-]*?)"
    r"(?:\s+using\s+(?P<index>\S+))?"
    r"(?:\s+on\s+(?P<relation>\S+))?"
    r"(?:\s*\(cost=(?P<cost>[^)]*)\))?\s*$"
)
ACTUAL_PATTERN = re.compile(
    r"^\s*\(actual\s+time=(?P<startup>[^.\s]+\.?\d*?)\.\.(?P<total>[^\s]+)\s+rows=(?P<rows>\d+)\s+loops=(?P<loops>\d+)\)\s*$"
)
ACTUAL_PATTERN_2 = re.compile(
    r"^\s*\(actual\s+time=(?P<startup>[^.\s]+\.?\d*?)\.\.(?P<total>[^\s]+)\s+rows=(?P<rows>\d+)\)\s*$"
)


def parse_plan_text(text: str) -> QueryPlan:
    lines = [line.rstrip() for line in text.splitlines()]
    nonempty = [line for line in lines if line.strip()]
    query_lines: list[str] = []
    for line in nonempty:
        stripped = line.strip()
        if not stripped:
            continue
        if (
            stripped.startswith("EXPLAIN")
            or stripped.startswith("SELECT")
            or stripped.startswith("WITH")
        ):
            query_lines.append(stripped)
        elif re.match(r"^[A-Z][A-Za-z ]+ Time: ", stripped):
            continue
        elif re.match(r"^[A-Za-z ]+: ", stripped) and "Time" in stripped:
            continue
    root: PlanNode | None = None
    stack: list[tuple[int, PlanNode]] = []
    plan: QueryPlan | None = None
    for raw_line in nonempty:
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("EXPLAIN") or line.startswith("SELECT") or line.startswith("WITH"):
            continue
        if line.startswith("Planning Time:"):
            if plan is not None:
                plan.planning_time = _parse_time_value(line.split(":", 1)[1])
            continue
        if line.startswith("Execution Time:"):
            if plan is not None:
                plan.execution_time = _parse_time_value(line.split(":", 1)[1])
            continue
        if "Time:" in line and line.split(":", 1)[0].strip() in {"Planning Time", "Execution Time"}:
            continue
        upper = line.upper()
        if upper.startswith(
            (
                "FROM ",
                "WHERE ",
                "GROUP BY ",
                "ORDER BY ",
                "HAVING ",
                "LIMIT ",
                "JOIN ",
                "LEFT ",
                "RIGHT ",
                "INNER ",
                "FULL ",
                "CROSS ",
                "UNION ",
                "INTERSECT ",
                "EXCEPT ",
                "VALUES ",
                "WINDOW ",
                "SELECT ",
                "WITH ",
            )
        ):
            continue
        if line.startswith("(") and "cost=" in line and stack:
            current = stack[-1][1]
            current.cost = _parse_cost(line.strip().strip("()"))
            continue
        if _looks_like_node_header(line):
            node = _parse_node_line(line)
            indent = len(raw_line) - len(raw_line.lstrip(" "))
            while stack and stack[-1][0] >= indent:
                stack.pop()
            node.parent = stack[-1][1] if stack else None
            if node.parent is not None:
                node.parent.children.append(node)
            elif root is None:
                root = node
            else:
                root.children.append(node)
            stack.append((indent, node))
            if plan is None:
                if root is None:
                    raise ValueError("No valid PostgreSQL plan node found in input.")
                plan = QueryPlan(root=root, query="\n".join(query_lines) if query_lines else None)
            continue

        if not stack:
            continue
        current = stack[-1][1]
        lower = line.lower()
        if lower.startswith("filter:"):
            current.filter_expression = _normalize_filter_expression(line.split(":", 1)[1].strip())
        elif lower.startswith("join filter:"):
            current.join_condition = line.split(":", 1)[1].strip()
        elif lower.startswith("rows removed by filter:"):
            match = re.search(r"(\d+)", line.split(":", 1)[1])
            if match:
                current.rows_removed_by_filter = int(match.group(1))
        elif lower.startswith("sort method:"):
            current.sort_method = line.split(":", 1)[1].strip()
        elif lower.startswith("memory:"):
            current.memory = line.split(":", 1)[1].strip()
        elif lower.startswith("disk:"):
            current.disk = line.split(":", 1)[1].strip()
        elif lower.startswith("actual time=") or "actual time=" in line:
            _apply_actual_time(current, line)
        elif lower.startswith("sort key:"):
            current.sort_method = current.sort_method or "Sort"
        elif lower.startswith("output:"):
            continue
        elif lower.startswith("one-time filter:"):
            current.filter_expression = line.split(":", 1)[1].strip()
        elif lower.startswith("inner unique:"):
            continue

    if root is None:
        raise ValueError("No valid PostgreSQL plan node found in input.")
    if root is None:
        raise ValueError("No valid PostgreSQL plan node found in input.")
    if plan is None:
        plan = QueryPlan(root=root, query="\n".join(query_lines) if query_lines else None)
    else:
        plan.root = root
    return plan


def _parse_node_line(line: str) -> PlanNode:
    text = line.strip()
    if text.startswith("->"):
        text = text[2:].strip()
    match = NODE_PATTERN.match(text)
    if not match:
        raise ValueError(f"Unsupported plan line: {line!r}")
    node_type = match.group("node").strip()
    relation = match.group("relation")
    index_name = match.group("index")
    cost_span = match.group("cost")
    cost = _parse_cost(cost_span) if cost_span else CostMetrics()
    node = PlanNode(
        node_type=node_type,
        relation=relation,
        index_name=index_name,
        cost=cost,
    )
    startup = _extract_actual_time_section(text)
    if startup:
        node.runtime = startup
        node.actual_rows = (
            startup.actual_rows if startup.actual_rows is not None else node.actual_rows
        )
        node.planned_rows = cost.planned_rows
        node.loops = startup.loops
    return node


def _looks_like_node_header(line: str) -> bool:
    stripped = line.strip()
    if not stripped or stripped.startswith("("):
        return False
    upper = stripped.upper()
    if any(
        upper.startswith(prefix)
        for prefix in (
            "FROM ",
            "WHERE ",
            "GROUP BY ",
            "ORDER BY ",
            "HAVING ",
            "LIMIT ",
            "JOIN ",
            "LEFT ",
            "RIGHT ",
            "INNER ",
            "FULL ",
            "CROSS ",
            "UNION ",
            "INTERSECT ",
            "EXCEPT ",
            "VALUES ",
            "WINDOW ",
            "SELECT ",
            "WITH ",
        )
    ):
        return False
    if any(
        stripped.lower().startswith(prefix)
        for prefix in (
            "filter:",
            "join filter:",
            "rows removed by filter:",
            "sort method:",
            "memory:",
            "disk:",
            "output:",
            "actual time=",
            "one-time filter:",
            "inner unique:",
            "planning time:",
            "execution time:",
        )
    ):
        return False
    return bool(NODE_PATTERN.match(stripped)) and (
        "cost=" in stripped
        or re.match(
            r"^(?:->\s*)?[A-Za-z][A-Za-z0-9 _-]*?(?:\s+using\s+\S+)?"
            r"(?:\s+on\s+\S+)?\s*$",
            stripped,
        )
        is not None
    )


def _parse_cost(fragment: str) -> CostMetrics:
    cost_match = re.search(r"(?P<startup>\d+(?:\.\d+)?)\.\.(?P<total>\d+(?:\.\d+)?)", fragment)
    startup_cost = _parse_float(cost_match.group("startup")) if cost_match else None
    total_cost = _parse_float(cost_match.group("total")) if cost_match else None
    planned_rows = None
    width = None
    rows_match = re.search(r"rows=(\d+)", fragment)
    if rows_match:
        planned_rows = int(rows_match.group(1))
    width_match = re.search(r"width=(\d+)", fragment)
    if width_match:
        width = int(width_match.group(1))
    return CostMetrics(
        startup_cost=startup_cost, total_cost=total_cost, planned_rows=planned_rows, width=width
    )


def _extract_actual_time_section(text: str) -> RuntimeMetrics | None:
    actual_match = re.search(r"\(actual\s+time=(.*?)\)", text)
    if not actual_match:
        return None
    snippet = actual_match.group(1)
    m = re.search(
        r"time=(?P<start>[^.\s]+\.?\d*?)\.\.(?P<total>[^\s]+)\s+rows=(?P<rows>\d+)(?:\s+loops=(?P<loops>\d+))?",
        snippet,
    )
    if not m:
        return None
    return RuntimeMetrics(
        actual_startup_time=_parse_float(m.group("start")),
        actual_total_time=_parse_float(m.group("total")),
        actual_rows=int(m.group("rows")),
        loops=int(m.group("loops")) if m.group("loops") else None,
    )


def _apply_actual_time(node: PlanNode, line: str) -> None:
    snippet = line.strip()
    if snippet.startswith("("):
        snippet = snippet[1:-1]
    match = re.search(
        r"time=(?P<start>[^.\s]+\.?\d*?)\.\.(?P<total>[^\s]+)\s+rows=(?P<rows>\d+)(?:\s+loops=(?P<loops>\d+))?",
        snippet,
    )
    if not match:
        return
    node.runtime.actual_startup_time = _parse_float(match.group("start"))
    node.runtime.actual_total_time = _parse_float(match.group("total"))
    node.actual_rows = int(match.group("rows"))
    node.runtime.actual_rows = int(match.group("rows"))
    node.loops = int(match.group("loops")) if match.group("loops") else None
    node.runtime.loops = node.loops


def _parse_time_value(value: str) -> float:
    text = value.strip().replace("ms", "").strip()
    parsed = _parse_float(text)
    if parsed is None:
        raise ValueError(f"Invalid PostgreSQL time value: {value!r}")
    return parsed


def _parse_float(value: str | Any) -> float | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def _normalize_filter_expression(value: str | None) -> str | None:
    if value is None:
        return None
    expression = value.strip()
    while expression.startswith("(") and expression.endswith(")"):
        inner = expression[1:-1].strip()
        if inner == expression:
            break
        expression = inner
    return expression.strip()


def _number_from_text(text: str) -> str:
    match = re.search(r"\d+", text or "")
    return match.group(0) if match else ""


__all__ = ["parse_plan_text"]
