# CI/CD Quick Start — Omnix 3.0

CI runs Python 3.11 on GitHub-hosted Ubuntu, Windows, and macOS runners.

## Reproduce CI locally

```bash
python -m pip install --upgrade pip "setuptools>=83" ".[dev,build]"
export QT_QPA_PLATFORM=offscreen
export PYNPUT_BACKEND=dummy
export OMNIX_MASTER_PASSWORD=ci-only-master-password
pytest --cov=omnix --cov-report=xml
```

Ubuntu/Debian hosts need the PyQt6 runtime library:

```bash
sudo apt-get update
sudo apt-get install --yes libegl1
```

## Quality and security

```bash
black --check src tests
isort --check-only src tests
flake8 src/omnix --count --select=E9,F63,F7,F82 --show-source --statistics
bandit -q -r src/omnix -ll
pip-audit --local --skip-editable
```

## Required focused checks

```bash
pytest tests/ui/test_gui_minimal.py tests/unit/test_macro_runner_execution.py -v
pytest tests/test_knowledge.py tests/unit/test_knowledge_system.py -v
```

## Inspect GitHub Actions

```bash
gh run list --workflow ci.yml --limit 10
gh run view RUN_ID --json conclusion,jobs,url
gh run view RUN_ID --log-failed
gh run rerun RUN_ID --failed
```

## Current CI invariants

- Keep `runs-on` on the hosted three-OS matrix unless an online, maintained
  self-hosted pool is deliberately provisioned.
- Keep the Linux `libegl1` step before pytest imports PyQt6.
- Upgrade the active environment to `setuptools>=83` before pip-audit.
- Resolve both candidate and allowed filesystem roots before containment tests.
- Keep tests isolated from real user directories.

See [CI_CD_GUIDE.md](CI_CD_GUIDE.md) for failure explanations and maintenance
details.
