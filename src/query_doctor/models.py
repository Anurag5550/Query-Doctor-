from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class Severity(StrEnum):
    INFO = "INFO"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class Confidence(StrEnum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


@dataclass(slots=True)
class CostMetrics:
    startup_cost: float | None = None
    total_cost: float | None = None
    planned_rows: int | None = None
    width: int | None = None


@dataclass(slots=True)
class RuntimeMetrics:
    actual_startup_time: float | None = None
    actual_total_time: float | None = None
    actual_rows: int | None = None
    loops: int | None = None
    planning_time: float | None = None
    execution_time: float | None = None


@dataclass(slots=True)
class FilterCondition:
    expression: str | None = None
    column: str | None = None
    operator: str | None = None
    value: str | None = None


@dataclass(slots=True)
class Recommendation:
    summary: str
    details: str = ""


@dataclass(slots=True)
class Finding:
    rule_id: str
    title: str
    severity: Severity
    confidence: Confidence
    node_type: str | None = None
    relation: str | None = None
    evidence: list[str] = field(default_factory=list)
    explanation: str = ""
    recommendation: str = ""
    metrics: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class PlanNode:
    node_type: str = ""
    relation: str | None = None
    alias: str | None = None
    cost: CostMetrics = field(default_factory=CostMetrics)
    runtime: RuntimeMetrics = field(default_factory=RuntimeMetrics)
    filter_expression: str | None = None
    join_condition: str | None = None
    rows_removed_by_filter: int | None = None
    sort_method: str | None = None
    memory: str | None = None
    disk: str | None = None
    actual_rows: int | None = None
    planned_rows: int | None = None
    loops: int | None = None
    parent: PlanNode | None = None
    children: list[PlanNode] = field(default_factory=list)
    scan_method: str | None = None
    index_name: str | None = None

    def __init__(
        self,
        node_type: str = "",
        relation: str | None = None,
        alias: str | None = None,
        cost: CostMetrics | None = None,
        runtime: RuntimeMetrics | None = None,
        filter_expression: str | None = None,
        join_condition: str | None = None,
        rows_removed_by_filter: int | None = None,
        sort_method: str | None = None,
        memory: str | None = None,
        disk: str | None = None,
        actual_rows: int | None = None,
        planned_rows: int | None = None,
        loops: int | None = None,
        parent: PlanNode | None = None,
        children: list[PlanNode] | None = None,
        scan_method: str | None = None,
        index_name: str | None = None,
        actual_total_time: float | None = None,
        actual_startup_time: float | None = None,
        total_cost: float | None = None,
    ) -> None:
        self.node_type = node_type
        self.relation = relation
        self.alias = alias
        self.cost = cost or CostMetrics()
        if total_cost is not None:
            self.cost.total_cost = total_cost
        self.runtime = runtime or RuntimeMetrics()
        if actual_total_time is not None:
            self.runtime.actual_total_time = actual_total_time
        if actual_startup_time is not None:
            self.runtime.actual_startup_time = actual_startup_time
        self.filter_expression = filter_expression
        self.join_condition = join_condition
        self.rows_removed_by_filter = rows_removed_by_filter
        self.sort_method = sort_method
        self.memory = memory
        self.disk = disk
        self.actual_rows = actual_rows
        self.planned_rows = planned_rows
        self.loops = loops
        self.parent = parent
        self.children = children or []
        self.scan_method = scan_method
        self.index_name = index_name

    @property
    def actual_total_time(self) -> float | None:
        return self.runtime.actual_total_time

    @property
    def actual_startup_time(self) -> float | None:
        return self.runtime.actual_startup_time

    @property
    def total_cost(self) -> float | None:
        return self.cost.total_cost


@dataclass(slots=True)
class QueryPlan:
    root: PlanNode
    query: str | None = None
    planning_time: float | None = None
    execution_time: float | None = None

    @property
    def all_nodes(self) -> list[PlanNode]:
        nodes: list[PlanNode] = []

        def walk(node: PlanNode) -> None:
            nodes.append(node)
            for child in node.children:
                walk(child)

        walk(self.root)
        return nodes
