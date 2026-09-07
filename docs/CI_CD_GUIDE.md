# CI/CD Pipeline Guide for Omnix 3.0

Omnix uses GitHub-hosted runners to validate the native PyQt6 Python package.
The active workflows are `.github/workflows/ci.yml` and
`.github/workflows/release.yml`. Tauri CI and releases are owned by the separate
[Omnix Tauri](https://github.com/shingoku2/Omnix-Tauri) repository; self-hosted
workflows are not release targets.

**Last reviewed:** 2026-09-07

## Continuous integration

CI runs on pushes to `main`, `staging`, and `dev`, and pull requests targeting
`main` or `staging`.

The test job is a Python 3.11 matrix:

| Runner | Purpose | Platform prerequisite |
| --- | --- | --- |
| `ubuntu-latest` | Linux package and headless GUI tests | Install `libegl1` before importing PyQt6 |
| `windows-latest` | Windows path, package, and GUI behavior | None beyond Python dependencies |
| `macos-latest` | macOS path, package, and GUI behavior | None beyond Python dependencies |

Every test runner sets:

```text
QT_QPA_PLATFORM=offscreen
OMNIX_MASTER_PASSWORD=ci-only-master-password
PYNPUT_BACKEND=dummy
```

The job then installs `setuptools>=83` and `.[dev,build]`, compiles and imports
the package, runs pytest with XML coverage, and runs Bandit at medium-or-higher
severity.

The separate Ubuntu lint job checks Black, isort, fatal flake8 errors, and the
active environment with `pip-audit --local --skip-editable`. It explicitly
upgrades `setuptools>=83` because `[build-system].requires` applies only to
pip's isolated build environment; it does not upgrade the environment that
pip-audit examines.

## Local reproduction

Install the same development inputs used by CI:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip "setuptools>=83" ".[dev,build]"
```

On Ubuntu/Debian, install the Qt runtime prerequisite:

```bash
sudo apt-get update
sudo apt-get install --yes libegl1
```

Run the CI-equivalent checks:

```bash
export QT_QPA_PLATFORM=offscreen
export OMNIX_MASTER_PASSWORD=ci-only-master-password
export PYNPUT_BACKEND=dummy

python -m compileall -q src
python -c "import omnix; print(omnix.__version__)"
pytest --cov=omnix --cov-report=xml
black --check src tests
isort --check-only src tests
flake8 src/omnix --count --select=E9,F63,F7,F82 --show-source --statistics
bandit -q -r src/omnix -ll
pip-audit --local --skip-editable
```

When changing UI, game, macro, or platform-sensitive code, also run:

```bash
pytest tests/ui/test_gui_minimal.py tests/unit/test_macro_runner_execution.py -v
```

## Cross-platform filesystem tests

Knowledge ingestion intentionally restricts local files to the user's allowed
directories. Containment checks must compare canonical paths on both sides:

- Resolve the candidate path.
- Resolve every allowed root.
- Use `Path.relative_to()` or an equivalent component-aware comparison; never
  use string prefixes.

This matters in CI because macOS can expose temporary paths as `/var/...` while
resolving them to `/private/var/...`; Windows can likewise normalize aliases or
path spellings. Tests should use disposable paths and cover a non-canonical
allowed-root alias. Never point tests at a real user directory.

## Troubleshooting

### `ImportError: libEGL.so.1`

The Ubuntu runner is missing the EGL runtime used by PyQt6. Confirm the
Linux-only `libegl1` installation step runs before Python imports or pytest.
`QT_QPA_PLATFORM=offscreen` controls display behavior but does not replace
native shared libraries.

### File ingestion says a temporary file is outside the allowed root

Compare the displayed path with `Path.home()` after calling `.resolve()` on
both. A resolved candidate and unresolved allowed root can refer to the same
location but fail a lexical `relative_to()` comparison.

### pip-audit reports vulnerable setuptools

Check the active environment, not only `pyproject.toml`:

```bash
python -m pip show setuptools
python -m pip install --upgrade "setuptools>=83"
pip-audit --local --skip-editable
```

The CI remediation was prompted by `setuptools 79.0.1` and
`PYSEC-2026-3447`, whose listed fix version was 83.0.0.

### A run stays queued with no steps and is canceled after 24 hours

Inspect `runs-on`. Historical Omnix workflows used `self-hosted`; without an
online matching runner GitHub queued the job until its timeout. The supported
CI workflow uses the hosted OS matrix. A no-step cancellation is a scheduling
problem, not a pytest failure.

### Inspecting runs

```bash
gh run list --workflow ci.yml --limit 10
gh run view RUN_ID --json conclusion,jobs,url
gh run view RUN_ID --log-failed
gh run rerun RUN_ID --failed
```

## Release workflow

Tag pushes matching `v*` and manual release dispatches build unsigned
PyInstaller artifacts for Windows, macOS, and Linux. Code signing and automatic
updates remain outside the Omnix 3.0 workflow. Review
`.github/workflows/release.yml` and `WINDOWS_BUILD_INSTRUCTIONS.md` before
changing packaging.

## 2026-09-07 remediation record

The following CI failures were diagnosed and fixed:

- Ubuntu pytest initialization: installed `libegl1` for PyQt6.
- macOS/Windows knowledge ingestion tests: resolved allowed roots before path
  containment comparisons and added an alias-path regression test.
- Ubuntu lint dependency audit: explicitly upgraded the audited environment to
  `setuptools>=83` and raised the package build-system floor.

Local verification after the changes produced 343 passed and 8 skipped tests;
the focused GUI/macro set passed 28 tests, the focused knowledge set passed 22,
and Black, isort, flake8, Bandit, `git diff --check`, and pip-audit passed.

## References

- [CI workflow](../.github/workflows/ci.yml)
- [Release workflow](../.github/workflows/release.yml)
- [Testing guide](../TESTING.md)
- [Quick CI reference](QUICK_START_CI.md)
- [GitHub Actions runs](https://github.com/shingoku2/Omnix-All-knowing-gaming-companion/actions)
