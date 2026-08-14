# Contributing

Thank you for helping improve Query Doctor.

## Development setup

```bash
python -m pip install -e ".[dev]"
```

## Workflow

1. Fork the repository and create a feature branch.
2. Add tests for the bug fix or new behavior.
3. Implement the change.
4. Run the relevant checks.
5. Open a pull request with a concise summary.

## Code standards

- Use Python 3.11+ syntax.
- Prefer standard-library solutions over heavy dependencies.
- Keep type annotations throughout the codebase.
- Maintain conservative PostgreSQL heuristics.
- Do not claim certainty where the plan alone does not prove it.

## Checks

```bash
pytest
ruff check .
ruff format --check .
mypy src
```

## Pull request guidance

- Explain the bug or improvement clearly.
- Show relevant tests.
- Keep behavior changes scoped.
- Describe any heuristic tradeoffs.
