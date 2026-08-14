from __future__ import annotations

import sys
from collections.abc import Iterable
from pathlib import Path

import typer

from .analyzers import (
    analyze_disk_spill,
    analyze_estimation_mismatch,
    analyze_expensive_nodes,
    analyze_expensive_sort,
    analyze_filter_waste,
    analyze_join_efficiency,
    analyze_missing_index,
    analyze_nested_loop_risk,
    analyze_sequential_scan_risk,
)
from .config import DEFAULT_CONFIG
from .models import Finding, Severity
from .parser.json import parse_plan_json
from .parser.text import parse_plan_text
from .reporting.json import render_json
from .reporting.markdown import render_markdown
from .reporting.text import render_text

app = typer.Typer(
    add_completion=False, help="Analyze PostgreSQL EXPLAIN ANALYZE output for likely bottlenecks."
)


@app.callback()
def main() -> None:
    """Query Doctor command line."""


@app.command("analyze")
def analyze_command(
    file: str = typer.Argument(
        ..., help="Path to a PostgreSQL EXPLAIN ANALYZE plan file, or '-' for stdin."
    ),
    format: str = typer.Option("text", "--format", help="Output format: text, json, markdown"),
    no_color: bool = typer.Option(
        False, "--no-color", help="Disable ANSI colors in terminal output."
    ),
    slow_node_ms: float = typer.Option(
        DEFAULT_CONFIG.slow_node_ms,
        "--slow-node-ms",
        help="Threshold in milliseconds for expensive-node detection.",
    ),
    debug: bool = typer.Option(
        False, "--debug", help="Print additional debugging information on failure."
    ),
) -> None:
    """Analyze a PostgreSQL plan file or stdin content."""
    try:
        plan_text = _read_input(file)
        if not plan_text.strip():
            raise ValueError("Input is empty.")

        try:
            plan = parse_plan_text(plan_text)
        except ValueError:
            try:
                plan = parse_plan_json(plan_text)
            except ValueError as exc:
                raise ValueError(
                    "Input does not match a recognized PostgreSQL plan format."
                ) from exc

        findings = _run_analysis(plan, slow_node_ms=slow_node_ms)
        output = _render_output(findings, format=format, no_color=no_color)
        typer.echo(output)
        raise typer.Exit(_exit_code(findings))
    except typer.Exit:
        raise
    except ValueError as exc:
        if debug:
            typer.echo(f"debug: {exc}", err=True)
        typer.echo(f"Query Doctor: {exc}", err=True)
        raise typer.Exit(2) from exc
    except Exception as exc:  # pragma: no cover
        if debug:
            typer.echo(f"debug: {exc}", err=True)
        typer.echo("Query Doctor: unexpected internal error.", err=True)
        raise typer.Exit(3) from exc


@app.command("rules")
def rules() -> None:
    """List the built-in rules."""
    from .rules import RULES

    typer.echo("Available rules:")
    for rule in RULES:
        typer.echo(f"- {rule['rule_id']}: {rule['title']} ({rule['severity']})")


@app.command("version")
def version() -> None:
    """Print the Query Doctor version."""
    from . import __version__

    typer.echo(f"Query Doctor {__version__}")


def _read_input(path: str) -> str:
    if path == "-":
        return sys.stdin.read()
    file_path = Path(path)
    if not file_path.exists():
        raise ValueError(f"Input file not found: {path}")
    return file_path.read_text(encoding="utf-8")


def _run_analysis(plan, slow_node_ms: float) -> list[Finding]:
    findings: list[Finding] = []
    for analyzer in (
        analyze_missing_index,
        analyze_sequential_scan_risk,
        analyze_nested_loop_risk,
        analyze_join_efficiency,
        analyze_estimation_mismatch,
        analyze_filter_waste,
        analyze_expensive_sort,
        analyze_disk_spill,
        lambda p: analyze_expensive_nodes(p, slow_node_ms=slow_node_ms),
    ):
        findings.extend(analyzer(plan))
    findings.sort(
        key=lambda item: (Severity[item.severity.name].value if False else 0, item.rule_id)
    )
    return findings


def _render_output(findings: Iterable[Finding], *, format: str, no_color: bool) -> str:
    items = list(findings)
    if format == "json":
        return render_json(items)
    if format == "markdown":
        return render_markdown(items)
    return render_text(items, no_color=no_color)


def _exit_code(findings: list[Finding]) -> int:
    severities = {"HIGH": 3, "MEDIUM": 2, "LOW": 1}
    max_severity = 0
    for item in findings:
        max_severity = max(max_severity, severities.get(item.severity.value, 0))
    if max_severity >= 3:
        return 1
    if max_severity >= 2:
        return 1
    if findings:
        return 1
    return 0


if __name__ == "__main__":
    app()
