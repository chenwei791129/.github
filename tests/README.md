# Workflow regression checks

From the repository root, using Python 3:

```sh
python -m venv .venv
.venv/bin/pip install PyYAML==6.0.3
.venv/bin/python -m unittest discover -s tests -v
```

The tests inspect the reusable workflow's input contract, category expression,
SARIF upload guard and gating scan. They do not execute GitHub Actions or prove
Security-tab behavior. Validate that separately after a scheduled/manual caller
run. Workflow syntax can also be checked with `actionlint`.
