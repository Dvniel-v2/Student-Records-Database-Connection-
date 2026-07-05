# Contributing

## Branch naming

Use short descriptive branch names such as `feature/add-search` or `fix/form-validation`.

## Commit messages

Write clear commit messages that explain the change, for example:

```text
git commit -m "Add record creation form"
```

## Pull requests

- Open a pull request with a summary of the change.
- Include testing details and any relevant screenshots.
- Keep the scope focused.

## Code formatting

Run Ruff and Black before submitting:

```bash
ruff check .
black .
```

## Testing requirements

Please add or update tests for any new behavior. The project expects all tests to pass before merging.

## Issue usage

Use the issue templates in `.github/ISSUE_TEMPLATE/` for bug reports and feature requests.
