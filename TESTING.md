# Testing Guide for Omnix Gaming Companion

This document provides comprehensive information about testing the Omnix Gaming Companion application.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Test Infrastructure](#test-infrastructure)
3. [Running Tests](#running-tests)
4. [CI/CD Pipeline](#cicd-pipeline)
5. [Writing Tests](#writing-tests)
6. [Test Coverage](#test-coverage)
7. [Troubleshooting](#troubleshooting)

---

## Quick Start

### Install Test Dependencies

```bash
# Install development dependencies
pip install -r requirements-dev.txt
```

### Run All Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Open coverage report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

---

## Test Infrastructure

### Test Files

| File | Purpose | Coverage |
|------|---------|----------|
| `test_modules.py` | Module imports, basic integration | Core modules |
| `test_macro_system.py` | Macro creation, storage, execution | Macro system |
| `test_knowledge_system.py` | Knowledge packs, indexing | Knowledge system |
| `test_game_profiles.py` | Game profiles, overlay modes | Game detection |
| `test_edge_cases.py` | Error handling, edge cases | Error recovery |
| `test_gui_minimal.py` | GUI environment validation | PyQt6 GUI |
| `src/ui/test_design_system.py` | UI design system | UI components |

### Configuration Files

- **`pytest.ini`** - Pytest configuration and markers
- **`.coveragerc`** - Coverage.py settings
- **`conftest.py`** - Shared fixtures and utilities
- **`.pre-commit-config.yaml`** - Pre-commit hooks
- **`.github/workflows/tests.yml`** - CI/CD workflow

---

## Running Tests

### Basic Commands

```bash
# Run all tests
pytest

# Run specific test file
pytest test_modules.py

# Run specific test function
pytest test_modules.py::test_imports

# Run tests matching pattern
pytest -k "test_config"

# Run tests with specific marker
pytest -m unit
pytest -m "not slow"
```

### Verbose Output

```bash
# Verbose mode
pytest -v

# Very verbose (show test names)
pytest -vv

# Show local variables in traceback
pytest -l

# Show print statements
pytest -s
```

### Coverage Options

```bash
# Run with coverage
pytest --cov=src

# Coverage with HTML report
pytest --cov=src --cov-report=html

# Coverage with terminal report
pytest --cov=src --cov-report=term-missing

# Coverage with XML (for CI/CD)
pytest --cov=src --cov-report=xml
```

### Parallel Execution

```bash
# Run tests in parallel (faster)
pytest -n auto

# Run with 4 workers
pytest -n 4
```

### Test Selection

```bash
# Run unit tests only
pytest -m unit

# Run integration tests
pytest -m integration

# Skip slow tests
pytest -m "not slow"

# Skip GUI tests (if no display)
pytest -m "not ui"

# Run only failed tests from last run
pytest --lf

# Run failed tests first
pytest --ff
```

### Platform-Specific Tests

```bash
# Run Windows-only tests
pytest -m windows

# Run Linux-only tests
pytest -m linux

# Run macOS-only tests
pytest -m macos
```

---

## CI/CD Pipeline

### GitHub Actions Workflow

The CI/CD pipeline automatically runs on:
- **Push** to `main`, `develop`, or `claude/**` branches
- **Pull requests** to `main` or `develop`

### Workflow Jobs

#### 1. **Test Matrix** (Multi-OS, Multi-Python)

Tests run on:
- **Operating Systems:** Ubuntu, Windows, macOS
- **Python Versions:** 3.8, 3.9, 3.10, 3.11

```yaml
Strategy:
- Ubuntu: All Python versions (3.8-3.11)
- Windows: Python 3.8, 3.10, 3.11
- macOS: Python 3.8, 3.10, 3.11
```

#### 2. **Module Tests** (Ubuntu only)

Runs specific test files individually:
- `test_modules.py`
- `test_macro_system.py`
- `test_knowledge_system.py`
- `test_game_profiles.py`
- `test_edge_cases.py`
- `test_gui_minimal.py`

#### 3. **Build Validation** (Windows)

- Validates PyInstaller spec file
- Tests build dependencies
- Dry-run build process

#### 4. **Code Quality**

- **Flake8** - Linting and syntax checks
- **Bandit** - Security vulnerability scanning
- **Safety** - Dependency vulnerability checks

### Coverage Reporting

Coverage reports are:
1. Generated on Ubuntu with Python 3.11
2. Uploaded to Codecov
3. Available as build artifacts for 30 days

### Viewing CI/CD Results

- **GitHub Actions:** [View Workflow Runs](https://github.com/shingoku2/Omnix-All-knowing-gaming-companion/actions)
- **Codecov:** [View Coverage](https://codecov.io/gh/shingoku2/Omnix-All-knowing-gaming-companion)

---

## Writing Tests

### Using Fixtures

Fixtures are defined in `conftest.py` and automatically available to all tests.

#### Example: Testing with Temporary Directory

```python
def test_config_save(temp_config_dir):
    """Test configuration saving."""
    from src.config import Config

    config = Config(config_dir=str(temp_config_dir))
    config.ai_provider = "anthropic"
    config.save()

    # Verify saved
    config2 = Config(config_dir=str(temp_config_dir))
    assert config2.ai_provider == "anthropic"
```

#### Example: Testing with Mock AI Provider

```python
@pytest.mark.asyncio
async def test_ai_chat(mock_ai_provider):
    """Test AI provider chat."""
    response = await mock_ai_provider.chat([
        {"role": "user", "content": "Hello"}
    ])

    assert "content" in response
    assert response["content"] == "This is a test response."
```

#### Example: GUI Testing

```python
@pytest.mark.ui
def test_button_click(qtbot):
    """Test button click event."""
    from PyQt6.QtWidgets import QPushButton
    from PyQt6.QtCore import Qt

    button = QPushButton("Click me")
    qtbot.addWidget(button)

    clicked = False

    def on_click():
        nonlocal clicked
        clicked = True

    button.clicked.connect(on_click)

    # Simulate click
    qtbot.mouseClick(button, Qt.MouseButton.LeftButton)

    assert clicked
```

### UI Smoke Test Helper

Use the headless helper to exercise the chat widget and optionally capture a
PNG for manual review:

```bash
python scripts/ui_test_tool.py --message "Ping from smoke test" --screenshot /tmp/omnix-ui.png
```

- Runs with `QT_QPA_PLATFORM=offscreen` by default for CI/headless hosts.
- Stubs the AI assistant so the chat panel always returns an echo response.
- Reports bubble counts, response completion, and saves a screenshot when the
  `--screenshot` flag is provided.
- If you see `libGL.so.1` errors, install the system OpenGL runtime (e.g.
  `sudo apt-get install -y libgl1`).

### Using Markers

Mark tests to organize and selectively run them:

```python
import pytest

@pytest.mark.unit
def test_simple_function():
    """A simple unit test."""
    assert 1 + 1 == 2

@pytest.mark.integration
def test_module_integration():
    """An integration test."""
    # Test multiple modules working together
    pass

@pytest.mark.slow
def test_heavy_computation():
    """A slow test."""
    # Test that takes time
    pass

@pytest.mark.ui
def test_gui_widget(qtbot):
    """A GUI test."""
    # Test PyQt6 widgets
    pass

@pytest.mark.requires_api_key
def test_with_real_api():
    """Test requiring API key."""
    # Only runs if API key is available
    pass

@pytest.mark.skipif(sys.platform != "win32", reason="Windows only")
def test_windows_feature():
    """Test Windows-specific feature."""
    pass
```

### Test Naming Conventions

- **Test files:** `test_*.py` or `*_test.py`
- **Test functions:** `test_*()`
- **Test classes:** `Test*`

```python
# Good naming
def test_config_initialization():
    pass

def test_config_save_with_invalid_path():
    pass

class TestGameDetector:
    def test_detect_running_game(self):
        pass

    def test_add_custom_game(self):
        pass
```

---

## Test Coverage

### Current Coverage

View current coverage at: [![codecov](https://codecov.io/gh/shingoku2/Omnix-All-knowing-gaming-companion/branch/main/graph/badge.svg)](https://codecov.io/gh/shingoku2/Omnix-All-knowing-gaming-companion)

### Coverage Goals

| Component | Current | Target | Priority |
|-----------|---------|--------|----------|
| Security (Credentials) | 0% | 95%+ | 🔴 Critical |
| AI Providers | 20% | 90% | 🔴 High |
| Core Logic | 60% | 85% | 🟡 Medium |
| UI Components | 10% | 60% | 🟢 Low |
| **Overall** | **~45%** | **80%** | - |

### Generating Coverage Reports

```bash
# HTML report (most detailed)
pytest --cov=src --cov-report=html
open htmlcov/index.html

# Terminal report
pytest --cov=src --cov-report=term-missing

# XML report (for CI/CD)
pytest --cov=src --cov-report=xml

# JSON report
pytest --cov=src --cov-report=json
```

### Coverage Configuration

Coverage settings in `pytest.ini` and `.coveragerc`:

```ini
[coverage:run]
source = src
omit = */tests/*, */test_*.py

[coverage:report]
precision = 2
show_missing = true
exclude_lines =
    pragma: no cover
    def __repr__
    if __name__ == .__main__.:
```

---

## Troubleshooting

### Common Issues

#### 1. **Qt Platform Plugin Error**

```
qt.qpa.plugin: Could not load the Qt platform plugin
```

**Solution:**
```bash
export QT_QPA_PLATFORM=offscreen
pytest
```

#### 2. **Import Errors**

```
ModuleNotFoundError: No module named 'src'
```

**Solution:**
```bash
# Ensure src is in Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
pytest
```

Or use the pytest pythonpath setting (already in `pytest.ini`).

#### 3. **Tests Hanging**

**Solution:**
```bash
# Use timeout
pytest --timeout=60
```

#### 4. **GUI Tests Failing on Headless Server**

**Solution:**
```bash
# Use virtual display (Linux)
Xvfb :99 -screen 0 1920x1080x24 &
export DISPLAY=:99
pytest
```

#### 5. **Coverage Not Working**

**Solution:**
```bash
# Install coverage plugin
pip install pytest-cov

# Verify installation
pytest --version
# Should show: plugins: cov-4.x.x
```

### Debug Mode

```bash
# Run with debugging
pytest --pdb

# Drop into debugger on failure
pytest -x --pdb

# Show all local variables
pytest -l

# Verbose traceback
pytest --tb=long
```

### Test Output

```bash
# Capture none (show all output)
pytest -s

# Show print statements
pytest --capture=no

# Log to file
pytest --log-file=test.log --log-file-level=DEBUG
```

---

## Pre-commit Hooks

### Install

```bash
# Install pre-commit
pip install pre-commit

# Install git hooks
pre-commit install
```

### Run Manually

```bash
# Run on all files
pre-commit run --all-files

# Run specific hook
pre-commit run black --all-files
pre-commit run flake8 --all-files
```

### Skip Hooks (Emergency)

```bash
# Skip pre-commit hooks for a single commit
git commit --no-verify -m "Emergency fix"
```

---

## Best Practices

### 1. **Write Tests First (TDD)**

```python
# Write test
def test_new_feature():
    result = new_feature()
    assert result == expected_value

# Then implement
def new_feature():
    return expected_value
```

### 2. **Keep Tests Isolated**

```python
# Good - uses fixture
def test_config(temp_config_dir):
    config = Config(config_dir=temp_config_dir)
    # Test doesn't affect real config

# Bad - modifies global state
def test_config_bad():
    config = Config()  # Uses real config dir
    config.ai_provider = "test"  # Modifies real config!
```

### 3. **Use Descriptive Names**

```python
# Good
def test_config_saves_ai_provider_setting():
    pass

# Bad
def test1():
    pass
```

### 4. **Test Edge Cases**

```python
def test_division():
    assert divide(10, 2) == 5  # Normal case
    assert divide(10, 3) == 3.333  # Decimal case

    with pytest.raises(ZeroDivisionError):
        divide(10, 0)  # Error case
```

### 5. **Mock External Dependencies**

```python
@pytest.fixture
def mock_api_call(monkeypatch):
    def fake_api(*args, **kwargs):
        return {"data": "test"}

    monkeypatch.setattr("src.providers.OpenAIProvider.chat", fake_api)
```

---

## Additional Resources

- **Pytest Documentation:** https://docs.pytest.org/
- **Coverage.py Documentation:** https://coverage.readthedocs.io/
- **pytest-qt Documentation:** https://pytest-qt.readthedocs.io/
- **GitHub Actions Documentation:** https://docs.github.com/en/actions

---

**Last Updated:** 2025-11-18
**Maintained by:** Omnix Development Team
