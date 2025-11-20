# AI Context - Omnix Gaming Companion

**Quick Reference for AI Assistants**
**Last Updated:** 2025-11-20

---

## Project Summary

**Omnix** is a desktop AI gaming companion built with Python and PyQt6 that provides real-time assistance for gamers using multiple AI providers (OpenAI, Anthropic, Google Gemini).

**Tech Stack:** Python 3.8+, PyQt6, psutil, OpenAI/Anthropic/Gemini APIs
**LOC:** ~14,700 lines
**Test Coverage:** 272 test functions, 3,196 lines of test code

---

## Key Architecture Components

### Core Systems
1. **Game Detection** - `game_detector.py`, `game_watcher.py` - Process monitoring
2. **AI Integration** - `ai_router.py`, `providers.py` - Multi-provider support
3. **Knowledge System** - `knowledge_index.py` - TF-IDF semantic search
4. **Macro System** - `macro_manager.py`, `macro_runner.py` - Automation
5. **Session Management** - `session_logger.py` - Event tracking
6. **UI Design System** - `ui/design_system.py` - Token-based theming

### Directory Structure
```
src/                     # 14,700 LOC main source
├── config.py            # Configuration management
├── game_*.py            # Game detection and profiles
├── ai_*.py              # AI integration
├── knowledge_*.py       # Knowledge system
├── macro_*.py           # Macro system
├── session_*.py         # Session management
└── ui/                  # UI components and design system

tests/                   # 3,196 LOC test code
├── unit/                # Component tests
├── integration/         # Integration tests
├── edge_cases/          # Edge case tests
└── conftest.py          # Shared fixtures

scripts/                 # Automation scripts
├── verify_ci.py         # CI/CD verification
└── deploy_staging.sh    # Staging deployment

.github/workflows/       # CI/CD workflows
├── ci.yml               # Main CI pipeline
└── staging-deploy.yml   # Staging deployment
```

---

## CI/CD Infrastructure (NEW - 2025-11-20)

### Self-Hosted Setup
- **Host:** Proxmox LXC Container (omnix-staging, ID 200)
- **OS:** Ubuntu 24.04
- **Runner:** `/opt/actions-runner/` (systemd service)
- **Repo:** `/opt/omnix/`
- **Staging:** `/opt/omnix/staging/`

### Workflows
1. **CI Pipeline** (`.github/workflows/ci.yml`)
   - Triggers: Push to main/staging/dev, PRs
   - Steps: Lint (flake8) → Test (pytest with xvfb)
   - Uses: self-hosted runner

2. **Staging Deploy** (`.github/workflows/staging-deploy.yml`)
   - Triggers: Push to staging, manual dispatch
   - Steps: Deploy → Test → Verify
   - Creates deployment markers

### Key Scripts
- `scripts/verify_ci.py` - Pipeline health checks
- `scripts/deploy_staging.sh` - Manual deployment with backups

### Testing
- **Headless Qt:** `QT_QPA_PLATFORM=offscreen` for CI
- **CI Tests:** `tests/integration/test_ci_pipeline.py`
- **Markers:** `@pytest.mark.unit`, `@pytest.mark.integration`, `@pytest.mark.skip_ci`

---

## Recent Changes

### 2025-11-20: CI/CD Pipeline Enhancement
- ✅ Added CI/CD verification tool
- ✅ Added automated staging deployment workflow
- ✅ Added 20+ CI-specific integration tests
- ✅ Added comprehensive CI/CD documentation
- ✅ Added manual deployment script with backups

### 2025-11-19: Search Index Fix
- ✅ Fixed TF-IDF model persistence bug
- ✅ Search results now consistent after restart

### 2025-11-18: Circular Import Resolution
- ✅ Fixed import patterns in `ai_assistant.py`
- ✅ Renamed `types.py` to `type_definitions.py`

### 2025-11-17: Theme System Unification
- ✅ Unified token-based design system
- ✅ Backward compatibility layer

---

## Common Commands

### Development
```bash
# Run application
python main.py

# Run tests
pytest                              # All tests
pytest -m unit                      # Unit tests only
pytest -m integration               # Integration tests

# Simulate CI environment
export QT_QPA_PLATFORM=offscreen
xvfb-run -a pytest tests/ -v

# Verify CI/CD pipeline
python scripts/verify_ci.py
```

### Deployment
```bash
# Automatic staging deployment
git checkout staging
git merge main
git push origin staging

# Manual staging deployment
./scripts/deploy_staging.sh

# Check deployment
cat /opt/omnix/staging/.deployment_info
```

### Testing
```bash
# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/unit/test_config.py -v

# Run CI-specific tests
pytest tests/integration/test_ci_pipeline.py -v
```

---

## Important Conventions

### Code Style
- PEP 8 compliance
- Type hints for function signatures
- Docstrings (Google style)
- 4 spaces indentation

### Import Pattern
**CRITICAL:** Always use `from src.module import X` for consistency
```python
# GOOD
from src.knowledge_integration import get_knowledge_integration
from src.config import Config

# BAD (causes circular imports)
from knowledge_integration import get_knowledge_integration
```

### Testing Patterns
```python
# Use markers
@pytest.mark.unit
@pytest.mark.integration
@pytest.mark.skip_ci        # For tests that can't run in CI

# Use fixtures from conftest.py
def test_something(temp_dir, config, game_detector):
    pass
```

### Qt Patterns
```python
# Always use worker threads for long operations
worker = AIWorkerThread(ai_assistant, question)
worker.response_ready.connect(self.display_response)
worker.start()

# Never block GUI thread
# BAD: response = ai_assistant.ask_question(question)
```

---

## Quick Reference Links

### Documentation
- [CLAUDE.md](CLAUDE.md) - Comprehensive guide (69KB)
- [CI_CD_GUIDE.md](docs/CI_CD_GUIDE.md) - CI/CD documentation
- [QUICK_START_CI.md](docs/QUICK_START_CI.md) - CI quick reference
- [README.md](README.md) - User documentation

### Testing
- [pytest.ini](pytest.ini) - Test configuration
- [tests/conftest.py](tests/conftest.py) - Shared fixtures
- [TESTING.md](TESTING.md) - Testing guide

### CI/CD
- [.github/workflows/ci.yml](.github/workflows/ci.yml) - Main CI
- [.github/workflows/staging-deploy.yml](.github/workflows/staging-deploy.yml) - Staging deploy
- [scripts/README.md](scripts/README.md) - Scripts documentation

---

## Known Issues & Fixes

### Fixed Issues
- ✅ **Search Index Corruption** (2025-11-19) - TF-IDF persistence fixed
- ✅ **Circular Import** (2025-11-18) - Import patterns standardized
- ✅ **Theme System** (2025-11-17) - Unified design system

### Active Considerations
- Self-hosted runner requires manual maintenance
- Headless testing requires `QT_QPA_PLATFORM=offscreen`
- API keys stored in system keyring (encrypted)

---

## For AI Assistants

### When Working on This Codebase

**DO:**
- ✅ Use design system components from `ui/components/`
- ✅ Use worker threads for long operations (Qt)
- ✅ Follow `from src.module` import pattern
- ✅ Add tests for new features
- ✅ Use type hints and docstrings
- ✅ Run `python scripts/verify_ci.py` before committing
- ✅ Check CLAUDE.md for detailed information

**DON'T:**
- ❌ Block the GUI thread with long operations
- ❌ Hardcode styles (use design tokens)
- ❌ Store API keys in .env (use credential_store)
- ❌ Use inconsistent import patterns
- ❌ Modify built-in game profiles
- ❌ Commit sensitive data

### Common Tasks

**Add a new game:**
1. Update `game_detector.py` with exe names
2. Create profile in `game_profile.py` or via UI

**Add AI provider:**
1. Implement in `providers.py`
2. Register in `ai_router.py`
3. Add UI in `providers_tab.py`

**Add tests:**
1. Unit tests → `tests/unit/`
2. Integration tests → `tests/integration/`
3. Use fixtures from `conftest.py`
4. Add markers (`@pytest.mark.unit`)

**Deploy to staging:**
1. Merge to staging branch
2. Push (triggers workflow)
3. Or run `./scripts/deploy_staging.sh`

---

## Quick Stats

- **Total LOC:** ~14,700 (src) + 3,196 (tests)
- **Test Functions:** 272
- **Test Files:** 20
- **CI Workflows:** 2
- **Supported Games:** 15 built-in + custom
- **AI Providers:** 3 (OpenAI, Anthropic, Gemini)
- **Platforms:** Windows, macOS, Linux

---

## Contact & Resources

- **Repository:** https://github.com/shingoku2/Omnix-All-knowing-gaming-companion
- **Issues:** GitHub Issues
- **Actions:** https://github.com/shingoku2/Omnix-All-knowing-gaming-companion/actions

---

**This file provides quick context for AI assistants. For comprehensive information, see CLAUDE.md**

## 2025-01-17 Agent Update
- Added new pytest suites for core config/credential handling, AI routing and assistant context trimming, knowledge ingestion/indexing, macro runner safety, and GUI interaction flows.
- Resolved PyQt6 libGL import failure during GUI test collection by adding a module-level skip guard to handle headless environments.
- Tests executed: `pytest tests/test_core.py tests/test_ai.py tests/test_knowledge.py tests/test_macro.py tests/test_gui.py -q` (16 passed, 1 skipped for PyQt6 availability).

## 2025-??-?? Update (UI Redesign)
- Refactored `src/gui.py` with new neon HUD layout matching OMNIX reference: added NeonButton/Toggle/Card widgets, chat bubble UI with animations, game status hex display, settings and AI provider panels, and bottom overlay bar.
- Added custom stylesheet `src/ui/omnix.qss` for cyberpunk gradients, neon outlines, and chat bubble styling.
- Updated game watcher UI hooks to reflect detected/idle games in the central hex module.
- Applied entry animations and custom QSS loading in theme pipeline; resolved indentation error discovered via `python -m compileall src/gui.py`.
