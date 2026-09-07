# Agent Guidelines - Omnix Gaming Companion

## Build & Test Commands
**Setup:** `python -m venv .venv; .\.venv\Scripts\activate; python -m pip install --upgrade pip "setuptools>=83" ".[dev,build]"`
**Run app:** `python -m omnix` (compatibility: `python main.py`)
**Single test:** `pytest tests/unit/test_game_detector.py -v` or `pytest -k game_detector`  
**All tests:** `pytest` | **Coverage:** `pytest --cov=omnix --cov-report=html`
**Lint/format:** `pre-commit run --all-files` (Black 100cols, isort, flake8, bandit)  
**Package run:** `python -m omnix` | **Desktop build:** `pyinstaller GamingAIAssistant.spec --clean --noconfirm`

## Code Style & Architecture
**Python 3.11+:** 4-space indent, type hints preferred, Black (100 chars), isort (profile=black), flake8 (127 chars, ignore E203)
**Imports:** `from omnix.module import X` (never circular imports)
**Architecture:** Strict layered design - GUI (PyQt6) → Business Logic → Data/Integration → Persistence  
**UI Components:** Use `src/omnix/ui/tokens.py` colors/spacing, reusable components in `src/omnix/ui/components/`
**Testing:** `test_*.py` / `*_test.py`, classes `Test*`, functions `test_*`, use markers `@pytest.mark.unit` etc.

## Security & Configuration
**Secrets:** Store in keyring/`.env` (never commit), use `CredentialStore.get_key()`  
**Local data:** `~/.gaming_ai_assistant/`, never alter user dirs in tests  
**API Keys:** Via secure keyring, test with `CredentialStore.validate_key()`  
**Cross-platform:** Windows (pywin32), Linux/macOS (keyring), use `QT_QPA_PLATFORM=offscreen` for headless

## Key Patterns & Files
**AI Providers:** Implement `AIProvider` protocol in `providers.py`, use factory `create_provider()`  
**Game Detection:** Passive polling via `GameWatcher` (5s), match against `game_profiles.json`  
**Macros:** `MacroRunner.execute_macro()` in background, `pynput` for input simulation  
**Knowledge:** TF-IDF semantic search in `knowledge_index.py`, augment prompts via `KnowledgeIntegration`  
**Error Handling:** Log all failures, never silent fallbacks, use Qt signals for GUI updates

## Essential Testing
**Unit tests:** Mock everything external (providers, processes, files)  
**Integration tests:** Real file I/O, fake API responses  
**UI tests:** Set `QT_QPA_PLATFORM=offscreen` before importing PyQt6  
**Headless CI:** Set `OMNIX_MASTER_PASSWORD` env var for credential testing  
**Focus:** When changing UI/game code, explicitly run `test_gui_minimal.py`, `test_macro_runner_execution.py`

## CI Guardrails
**Hosted matrix:** `.github/workflows/ci.yml` runs Python 3.11 on Ubuntu, Windows, and macOS; do not change it back to an unavailable `self-hosted` runner.
**Linux Qt:** Install `libegl1` before importing PyQt6 on hosted Ubuntu runners.
**Dependency audit:** Keep the active environment on `setuptools>=83`; build-system isolation alone does not upgrade the environment inspected by `pip-audit`.
**Path tests:** Resolve both candidate files and allowed roots before containment checks; macOS and Windows temporary paths may have different canonical spellings.
