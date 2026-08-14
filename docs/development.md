# Development

## Setup

```bash
python -m pip install -e ".[dev]"
```

## Tests

```bash
pytest
```

## Linting

```bash
ruff check .
ruff format --check .
```

## Type checking

```bash
mypy src
```

## Adding rules

1. Add a new analyzer function in a relevant `analyzers/*.py` module.
2. Return a list of `Finding` objects from a normalized `QueryPlan`.
3. Keep the language conservative and evidence-based.
4. Export the analyzer through the package `analyzers/__init__.py`.
5. Add tests for the new rule.

## Adding fixtures

Fixtures live under `tests/fixtures/`. Add a realistic plan, ideally with multiple nodes and at least one clear signal.

## Contributing

- Open an issue before a large change.
- Keep changes focused.
- Add or update tests alongside implementation changes.
- Run lint, type checks, and test suites before finalizing a PR.

## Releases

Version numbers are defined in `pyproject.toml` and exposed via `query_doctor.__version__`.
