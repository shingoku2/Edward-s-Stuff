# Test Quick Reference Guide — Omnix 3.0

Canonical setup: `python -m pip install --upgrade "setuptools>=83" ".[dev,build]"`.
**Last Updated:** 2026-09-07
**Quick access guide for testing the Omnix Gaming Companion**

---

## 🚀 Quick Start Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=omnix --cov-report=html

# Run specific test file
pytest tests/unit/test_game_detector.py -v

# Run tests matching pattern
pytest -k "test_game" -v

# Run only unit tests
pytest tests/unit/ -v

# Run only integration tests
pytest tests/integration/ -v
```

---

## 📊 Current Test Status (2026-09-07)

| Category | Tests | Status |
|----------|-------|--------|
| Automated suite | 343 passed, 8 skipped | ✅ Passing |
| UI/manual checks | Headless and manual | ⚠️ Environment-dependent |
| **TOTAL** | **351 collected** | **✅ Stable** |

---

## 🎯 Component Test Coverage

### ✅ Fully Tested (100% Pass)
- Game Detector (`tests/unit/test_game_detector.py`)
- Game Profiles (`tests/unit/test_game_profiles.py`)
- Macro System (`tests/unit/test_macro_system.py`)
- Credential Store (`tests/unit/test_credential_store.py`)
- Utilities (`tests/unit/test_utils.py`)
- AI Router (`tests/unit/test_ai_router.py`)

### ⚠️ Mostly Tested
- AI Assistant (`tests/unit/test_ai_assistant.py`)
- Knowledge System (`tests/unit/test_knowledge_system.py`)

---

## 🔍 Running Specific Test Suites

### By Component
```bash
# AI System
pytest tests/unit/test_ai_assistant.py tests/unit/test_ai_router.py tests/unit/test_providers.py -v

# Game System
pytest tests/unit/test_game_detector.py tests/unit/test_game_watcher.py tests/unit/test_game_profiles.py -v

# Macro System
pytest tests/unit/test_macro_system.py -v

# Knowledge System
pytest tests/test_knowledge.py tests/unit/test_knowledge_system.py -v

# Required GUI/macro regression checks
pytest tests/ui/test_gui_minimal.py tests/unit/test_macro_runner_execution.py -v

# Security & Config
pytest tests/unit/test_config.py tests/unit/test_credential_store.py -v
```

### By Test Type
```bash
# Fast tests only (skip slow)
pytest -m "not slow" -v

# Security tests only
pytest -m security -v

# Skip tests requiring API keys
pytest -m "not requires_api_key" -v

# Integration tests only
pytest -m integration -v
```

---

## 📈 Coverage Commands

```bash
# Generate HTML coverage report
pytest --cov=omnix --cov-report=html

# View in browser (Windows)
start htmlcov\index.html

# Generate terminal coverage report
pytest --cov=omnix --cov-report=term-missing

# Generate XML for CI/CD
pytest --cov=omnix --cov-report=xml

# Coverage for specific module
pytest tests/unit/test_game_detector.py --cov=omnix.game_detector --cov-report=term
```

---

## 🛡️ Security Testing

```bash
# Run Bandit security scanner
bandit -r src/omnix/ -f json -o bandit_report.json
bandit -r src/omnix/ -f txt

# Check the same active environment CI audits
python -m pip install --upgrade "setuptools>=83"
pip-audit --local --skip-editable

# Run with security tests only
pytest -m security -v
```

---

## 🐛 Debugging Failed Tests

```bash
# Show detailed failure info
pytest --tb=long

# Stop at first failure
pytest -x

# Show local variables in failure
pytest --tb=long --showlocals

# Run with print statements visible
pytest -s tests/unit/test_game_detector.py
```

---

## 🔧 Known Issues & Workarounds

### Issue 1: Qt Tests Require Display
**Error:** Tests fail without display  
**Workaround:** Set offscreen platform:
```bash
set QT_QPA_PLATFORM=offscreen
pytest tests/unit/test_game_watcher.py -v
```

---

## 📁 Test Reports Location

After running tests, find reports at:

```
├── htmlcov/
│   └── index.html              # Interactive coverage report
├── bandit_report.json          # Security scan results
└── TEST_QUICK_REFERENCE.md     # This file
```

---

## 🎨 Test Markers Reference

Use markers to run specific test categories:

| Marker | Description | Example |
|--------|-------------|---------|
| `unit` | Unit tests | `pytest -m unit` |
| `integration` | Integration tests | `pytest -m integration` |
| `slow` | Long-running tests | `pytest -m "not slow"` |
| `ui` | UI/GUI tests | `pytest -m ui` |
| `security` | Security tests | `pytest -m security` |
| `requires_api_key` | Needs API keys | `pytest -m "not requires_api_key"` |
| `windows` | Windows-only | `pytest -m windows` |

---

## ⚡ CI/CD Configuration

### Recommended pytest.ini settings (already configured):
```ini
[pytest]
pythonpath = src
minversion = 7.0
testpaths = tests .
addopts = -v --tb=short --strict-markers
markers =
    unit: Unit tests
    integration: Integration tests
    requires_api_key: Tests requiring API keys
timeout = 300
```

### GitHub Actions Example:
```yaml
- name: Run tests
  run: |
    pytest tests/ \
      --cov=omnix \
      --cov-report=xml \
      -m "not requires_api_key" \
      --maxfail=5
```

---

## 📊 Understanding Coverage Reports

### Coverage Thresholds:
- **Excellent:** 80%+ coverage
- **Good:** 60-80% coverage
- **Fair:** 40-60% coverage
- **Needs Work:** <40% coverage

### Current Status:
```
Core Modules:        60-88% ✅ Good to Excellent
GUI Modules:         0-10%  ⚠️  Expected (manual testing)
Provider Modules:    26-42% ⚠️  Needs API integration tests
Overall:             19.13% ⚠️  (Heavily weighted by GUI code)
```

---

## 🔄 Test Maintenance

### After Making Code Changes:
```bash
# 1. Run affected tests
pytest tests/unit/test_[your_module].py -v

# 2. Check coverage impact
pytest tests/unit/test_[your_module].py --cov=omnix.[your_module] --cov-report=term

# 3. Run full suite to ensure no breakage
pytest tests/ -v

# 4. Update security scan
bandit -r src/omnix/ -f json -o bandit_report.json
```

### Adding New Tests:
1. Create test file: `tests/unit/test_new_feature.py`
2. Follow naming convention: `test_*` functions
3. Use fixtures from `conftest.py`
4. Add appropriate markers
5. Run and verify: `pytest tests/unit/test_new_feature.py -v`

---

## 🚨 Emergency Test Commands

```bash
# Quick sanity check (fast tests only)
pytest tests/unit/ -k "not slow" --maxfail=1 -q

# Check if specific feature still works
pytest tests/unit/test_game_detector.py::TestGameDetector::test_detect_running_game -v

# Verify critical path
pytest tests/integration/ -v

# Full regression test
pytest tests/ --tb=short -v
```

---

## 📞 Getting Help

### Test Failures:
1. Check this guide for known issues
2. Run test with `-vv` for verbose output
3. Check test logs in console output

### Coverage Questions:
1. Open `htmlcov/index.html` in browser
2. Navigate to specific module
3. Lines in red are not covered by tests

### Security Scan:
1. Check `bandit_report.json`
2. Review severity levels (High/Medium/Low)

---

## 📝 Quick Tips

✅ **DO:**
- Run tests before committing
- Check coverage for new code
- Use meaningful test names
- Mock external dependencies
- Clean up temp files in tests

❌ **DON'T:**
- Skip failing tests without documenting
- Test implementation details
- Use hardcoded paths
- Leave debug prints in tests
- Test private methods directly

---

## 🎯 Test Quality Metrics

Current quality scores:

| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| Pass Rate | >95% | 96.4% | ✅ |
| Core Coverage | >60% | 60-88% | ✅ |
| Test Speed | <60s | 20s | ✅ |
| Security Issues (Critical) | 0 | 0 | ✅ |
| Flaky Tests | 0 | 0 | ✅ |

---

**Last Test Run:** 2025-11-19 03:30 UTC  
**Next Review:** After fixing known issues  
**Status:** ✅ Production Ready (with documented limitations)
