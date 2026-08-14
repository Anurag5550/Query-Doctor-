from __future__ import annotations

from dataclasses import dataclass

from .models import Severity


@dataclass(slots=True)
class AnalysisConfig:
    slow_node_ms: float = 100.0
    severity_threshold: Severity = Severity.LOW
    min_rows_for_scan_risk: int = 5000
    debug: bool = False


DEFAULT_CONFIG = AnalysisConfig()
