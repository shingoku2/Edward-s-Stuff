# AI Context - Omnix Gaming Companion

**Quick Reference for AI Assistants**
**Last Updated:** 2026-05-11

---

### 2026-05-11: V2 Full Build — All Phases Complete

**Branch:** `version-2`

**What was built:**
- ✅ Phase 0: V2 repo structure — `backend/`, `src-tauri/`, `frontend/` (overhauled)
- ✅ Phase 1: `backend/server.py` — FastAPI sidecar exposing all V1 modules via REST + WebSocket on port 7432
- ✅ Phase 2: `src-tauri/` — Tauri v2 shell (adapted plan's v1 API to Tauri v2 `tray::TrayIconBuilder`, `menu::Menu`); launches Python backend as subprocess
- ✅ Phase 3: `frontend/src/lib/api.ts`, `hooks/useOmnixWS.ts`, `stores/appStore.ts` — API client, WebSocket streaming hook, Zustand store
- ✅ Phase 4: All UI components — `Panel`, `NeonButton`, `TitleBar`, `ParticleField`, `ScanLine`, `ChatBubble`, `ChatPanel`, `GamePanel`, `StatsPanel`, `OverlayPanel`
- ✅ Phase 5: Settings modal — `AIConfigTab`, `KnowledgeTab`, `MacrosTab`, `LicenseTab`, `SettingsModal`
- ✅ Phase 6: Voice input hook (`useVoiceInput.ts`); streaming already built in Phase 1/3
- ✅ Phase 8: `tests/v2/test_api.py` — async httpx tests for all API endpoints
- ✅ Phase 9: CI updated — added `backend-v2-tests` and `frontend-typecheck` jobs
- ✅ Phase 10: This aicontext.md update

**Deviations from plan:**
- Tauri `main.rs` rewritten for Tauri v2 API (plan used v1 `SystemTray` etc.)
- `asyncio.to_thread()` used in backend for all blocking V1 calls (plan had some missing)
- Settings stubs (Knowledge, Macros, License tabs) fully implemented
- `useVoiceInput.ts` typed safely without `any` where avoidable

**New files created:**
```
backend/__init__.py
backend/server.py
src-tauri/Cargo.toml
src-tauri/build.rs
src-tauri/tauri.conf.json
src-tauri/src/main.rs
src-tauri/capabilities/default.json
frontend/src/lib/api.ts
frontend/src/hooks/useOmnixWS.ts
frontend/src/hooks/useVoiceInput.ts
frontend/src/stores/appStore.ts
frontend/src/styles/globals.css
frontend/src/components/shared/Panel.tsx
frontend/src/components/shared/NeonButton.tsx
frontend/src/components/shared/TitleBar.tsx
frontend/src/components/FX/ParticleField.tsx
frontend/src/components/FX/ScanLine.tsx
frontend/src/components/Chat/ChatBubble.tsx
frontend/src/components/Chat/ChatPanel.tsx
frontend/src/components/Dashboard/GamePanel.tsx
frontend/src/components/Dashboard/StatsPanel.tsx
frontend/src/components/Overlay/OverlayPanel.tsx
frontend/src/components/Settings/SettingsModal.tsx
frontend/src/components/Settings/AIConfigTab.tsx
frontend/src/components/Settings/KnowledgeTab.tsx
frontend/src/components/Settings/MacrosTab.tsx
frontend/src/components/Settings/LicenseTab.tsx
tests/v2/__init__.py
tests/v2/test_api.py
```

**Modified files:**
```
frontend/package.json   — V2 deps (Tauri, Three.js, Zustand, Recharts, etc.)
frontend/vite.config.ts — path alias @/, port 5173
frontend/tailwind.config.js — Omnix V2 design tokens
frontend/tsconfig.json — path alias support
frontend/index.html     — Google Fonts (Orbitron, Rajdhani, JetBrains Mono)
frontend/src/App.tsx    — Full V2 App
frontend/src/main.tsx   — Updated entry point
requirements.txt        — Added FastAPI/uvicorn/websockets
.github/workflows/ci.yml — Added V2 backend and frontend typecheck jobs
```

**Known issues for next phase:**
- `src-tauri/` Cargo.lock not generated yet (needs `cargo build` on a machine with Rust)
- `frontend/package-lock.json` will need `npm install` to regenerate against new deps
- Screenshot AI analysis endpoint (Phase 6 Feature 4) not yet implemented — requires llava model
- Session coaching chart component (Phase 6 Feature 2) not yet wired into Dashboard

---

## Project Summary

**Omnix** is a desktop AI gaming companion built with Python and PyQt6 that provides real-time assistance for gamers using Ollama for local/remote LLM inference. Features include automatic game detection, AI-powered assistance, knowledge system integration, macro automation, and modern overlay UI.

**Backend Tech Stack:** Python 3.8+, PyQt6, psutil, Ollama API, cryptography, keyring
**LOC:** ~14,700 lines (backend) + 3,196 lines (tests)
**Test Coverage:** 272 test functions across unit, integration, and UI test suites
**Architecture:** Layered design with GUI → Business Logic → Data/Integration → Persistence

## Repository Guidelines (from AGENTS.md)
- Structure: `src/` core app (AI routing, credentials, game detection, PyQt6 UI/design system), `frontend/` web dashboard/overlay assets, `tests/` pytest suite, `scripts/` and root `*.bat` for builds; build artifacts in `build/` and `dist/`.
- Commands: create venv `python -m venv .venv; .\.venv\Scripts\activate`; install deps `pip install -r requirements.txt` (or `requirements-dev.txt`); run app `python main.py`; tests `pytest` or `pytest --cov=src --cov-report=html`; lint/format/security `pre-commit run --all-files`; Windows build `python build_windows_exe.py` or `pyinstaller GamingAIAssistant.spec`.
- Style: Python 3.8+, 4-space indentation, prefer type hints; Black 100 cols and isort (profile=black); Flake8 max line length 127 with E203 ignored; test naming `test_*.py`/`*_test.py`, classes `Test*`, functions `test_*`.
- Testing: run `pytest` before PRs (use `-n auto` if needed); focus runs `pytest tests/game` or `pytest -k game_detector`; review coverage via `htmlcov/index.html`; explicitly run skipped UI/game tests like `test_gui_minimal.py`, `test_macro_runner_execution.py` when touching related code.
- Commits/PRs: short imperative commit summaries; before pushing run `pre-commit run --all-files` and relevant tests; PRs should include problem/solution, impacted modules, test commands/output, config/env prereqs (e.g., `.env`, keyring), and link issues when available.
- Security: secrets stay in keyring/`.env` (never commit keys; `.env.example` lists required vars); keep user data in `~/.gaming_ai_assistant/` and avoid altering user dirs in tests (use temp paths/fixtures from `conftest.py`).

---

## Key Architecture Components

### Core Systems
1. **Game Detection** - `game_detector.py`, `game_watcher.py` - Process monitoring with performance optimization
### 1. AI System (5,000 LOC)
Handles multi-provider LLM integration with provider abstraction

**Files:**
- `src/ai_assistant.py` - High-level Q&A interface
- `src/ai_router.py` - Provider routing logic (Legacy/Wrapper)
- `src/providers.py` - `LLMProvider` interface, `OllamaProvider`, `OpenAIProvider`, `get_provider` factory
- `src/api_keys/` - Key management

**Key Functions:**
```python
ai_assistant.ask_question(question: str) -> str  # Main interface
ai_assistant.provider_instance.generate_response(system_prompt, user_prompt) -> str
get_provider(config) -> LLMProvider  # Factory
```

**Critical Files for Code Changes:**
- Add new provider: Implement `LLMProvider` in `src/providers.py` and update `get_provider`
- Change AI logic: Modify `ai_assistant.py` methods
- Provider issues: Check `.env` credentials + provider rate limits
3. **Knowledge System** - `knowledge_index.py` - TF-IDF semantic search with persistence
4. **Macro System** - `macro_manager.py`, `macro_runner.py` - Automation with safety limits
5. **Session Management** - `session_logger.py` - Event tracking with AI coaching
6. **UI Design System** - `ui/design_system.py` - Token-based theming with component library
7. **Security** - `credential_store.py`, `security.py` - Enhanced encryption with OWASP compliance
8. **HRM Integration** - `hrm_integration.py` - Structured reasoning for complex queries

### Directory Structure
```
src/                     # 14,700 LOC main source (Python/PyQt6)
├── config.py            # Configuration management with constants
├── credential_store.py  # Secure storage (AES-256, system keyring)
├── game_*.py            # Game detection and profiles
├── ai_*.py              # AI integration with HRM support
├── knowledge_*.py       # Knowledge system with TF-IDF
├── macro_*.py           # Macro system with safety
├── session_*.py         # Session management
├── hrm_*.py             # Hierarchical Reasoning Model
├── security.py          # File system hardening
├── utils.py             # Logging and utilities
├── gui.py               # Main PyQt6 interface
├── omnix_hud.py         # Legacy HUD components (deprecated)
├── overlay_modes.py     # UI mode configurations
└── ui/                  # Design system and components
    ├── design_system.py # Token-based styling
    ├── tokens.py        # Design tokens
    ├── components/      # Reusable UI components
    ├── theme_manager.py # Theme management
    └── omnix.qss        # Legacy QSS styles

tests/                   # 3,196 LOC test code
├── unit/                # Component tests (16 test files)
├── integration/         # Integration tests (5 test files)
├── edge_cases/          # Edge case tests
└── conftest.py          # Shared fixtures

frontend/                # React/TypeScript web UI (optional)
├── src/                 # Web components
├── package.json         # Node dependencies
└── vite.config.ts       # Build configuration

scripts/                 # Automation scripts
├── verify_ci.py         # CI/CD verification
├── deploy_staging.sh    # Staging deployment
└── ui_test_tool.py      # UI smoke testing

.github/workflows/       # CI/CD workflows
├── ci.yml               # Main CI pipeline
└── staging-deploy.yml   # Staging deployment
```

---

## CI/CD Infrastructure (Updated 2025-12-10)

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
- `scripts/ui_test_tool.py` - Headless UI validation with screenshots

### Testing
- **Headless Qt:** `QT_QPA_PLATFORM=offscreen` for CI
- **CI Tests:** `tests/integration/test_ci_pipeline.py`
- **Markers:** `@pytest.mark.unit`, `@pytest.mark.integration`, `@pytest.mark.skip_ci`

---

## Recent Changes

### 2026-01-13: Modular AI & Cleanup (MAJOR)
- ✅ **Modular LLM Support** - Refactored AI system to support multiple providers via `LLMProvider` interface
- ✅ **OpenAI-Compatible Support** - Added generic `OpenAIProvider` for LM Studio, AnythingLLM, etc.
- ✅ **Codebase Standardization** - Standardized all internal imports to `from src.module import X` pattern
- ✅ **Configuration Update** - Extended Config to handle API keys and base URLs for generic providers
- ✅ **Testing** - Added unit tests for provider factory, config, and modular AI assistant

### 2025-12-10: Comprehensive Code Audit & Security Enhancement (MAJOR)
- ✅ **Import Standardization** - Fixed circular dependency risks with consistent import patterns
- ✅ **Configuration Constants** - Replaced hardcoded values with centralized constants in config.py
- ✅ **Enhanced Security** - Strengthened credential storage with 600K PBKDF2 iterations (OWASP 2024), secure temp directory storage
- ✅ **Performance Optimization** - Implemented caching and background scanning for game detection (2s cache, background threads)
- ✅ **UI Consolidation** - Deprecated legacy HUD components in favor of unified component system with migration path
- ✅ **Test Coverage** - Restored 7 previously ignored unit tests by removing from pytest ignore list
- ✅ **Dependency Cleanup** - Removed commented HRM dependencies from requirements.txt
- ✅ **Critical Regression Fix** - Resolved executable packaging issue with proper import compatibility

**Security Improvements:**
- Increased PBKDF2 iterations from 480K to 600K (OWASP 2024 compliance)
- Enhanced fallback key storage to use secure temporary directory
- Improved encryption key file naming with secure extensions
- Added backward compatibility for legacy key files
- Strengthened security warnings and error handling

**Performance Optimizations:**
- Implemented caching system with 2-second cache duration
- Added background scanning thread for continuous process monitoring
- Optimized process scanning to only get essential info (pid, name)
- Created cache invalidation logic based on game list changes
- Added thread-safe cache management with RLock
- Reduced blocking operations in hot paths

### 2025-12-10: HRM Integration - Structured Reasoning ⭐
- ✅ **Intelligent Question Type Detection** - Puzzle, strategy, optimization, sequence analysis
- ✅ **Multi-word Phrase Recognition** - Complex reasoning query identification
- ✅ **Game Genre-aware Routing** - Automatic triggers for reasoning-heavy games
- ✅ **Structured Reasoning Frameworks** - Templates guide LLM responses
- ✅ **Timeout Protection** - 5s default, configurable timeout
- ✅ **Graceful Fallback** - Continues if analysis fails

**How It Works:**
1. User asks complex reasoning question
2. HRM detects question type and game context
3. Generates structured reasoning outline
4. Outline prepended to message sent to Ollama
5. LLM follows reasoning structure in response

**Configuration (.env):**
```
HRM_ENABLED=true
HRM_MAX_INFERENCE_TIME=5.0
```

### 2025-12-06: Ollama-Only Migration (MAJOR REFACTOR)
- ✅ **Simplified to Ollama exclusively** - Removed OpenAI, Anthropic, Gemini providers
- ✅ **No API keys required** - Ollama runs locally without external dependencies
- ✅ **Privacy-first architecture** - All inference happens locally by default
- ✅ **Model freedom** - Use any Ollama model (llama3, mistral, codellama, etc.)
- ✅ **Automatic model discovery** - UI shows available models from Ollama
- ✅ **Connection testing** - Validates Ollama daemon availability
- ✅ **Parameter translation** - Maps common params (max_tokens → num_predict)
- ✅ **Flexible hosting** - Supports both local and remote Ollama instances

### 2025-11-20: React/TypeScript Frontend (MAJOR UI UPGRADE)
- ✅ Created complete React/TypeScript frontend with Tailwind CSS
- ✅ Implemented Sci-Fi/Cyberpunk HUD design
- ✅ Added neon blue (#00f3ff) and red (#ff2a2a) color scheme
- ✅ Integrated Lucide React icons
- ✅ Set up Vite build system
- ✅ Added custom fonts (Orbitron, Rajdhani)
- ✅ Implemented reusable Panel component with corner accents
- ✅ Created responsive 12-column grid layout
- ✅ Added glassmorphism effects and backdrop blur
- ✅ Implemented chat interface with message bubbles
- ✅ Created rotating game status display
- ✅ Added settings panel with hover effects
- ✅ Implemented AI provider selector with radio buttons
- ✅ Added comprehensive frontend documentation

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

## Code Audit Results Summary

**Issues Fixed:**
1. **AUD-01 (high)** - Import inconsistencies resolved with standardized absolute imports for executable compatibility
2. **AUD-02 (high)** - Hardcoded values replaced with configuration constants
3. **AUD-03 (medium)** - Enhanced credential storage security with stronger encryption
4. **AUD-04 (medium)** - Implemented caching and background scanning for performance
5. **AUD-05 (medium)** - Consolidated UI components with deprecation warnings
6. **AUD-06 (low)** - Restored test coverage by removing unnecessary ignores
7. **AUD-07 (low)** - Cleaned up outdated dependencies and incomplete features

**Security Enhancements:**
- OWASP 2024 compliant PBKDF2 iterations (600K)
- Secure temporary directory for fallback keys
- Enhanced encryption with better key management
- Improved error handling and security warnings

**Performance Improvements:**
- 2-second caching for game detection results
- Background scanning thread for continuous monitoring
- Optimized process scanning (reduced data collection)
- Thread-safe cache management
- Reduced blocking operations in UI hot paths

**Quality Improvements:**
- Restored 7 legitimate unit tests to active test suite
- Removed commented/inactive dependencies
- Consolidated UI components with clear migration path
- Enhanced configuration management with constants

---

## Common Commands

### Development (Python Backend)
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

# UI smoke testing
python scripts/ui_test_tool.py --message "UI test ping"

# Code quality checks
pre-commit run --all-files
```

### Frontend Development (React/TypeScript)
```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Run development server (http://localhost:3000)
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Lint code
npm run lint
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

# Run game detection tests
pytest tests/unit/test_game_detector.py -v

# Run credential store tests
pytest tests/unit/test_credential_store.py -v
```

---

## Important Conventions

### Code Style
- PEP 8 compliance
- Type hints for function signatures
- Docstrings (Google style)
- 4 spaces indentation

### Import Pattern
**CRITICAL:** Use absolute imports for executable compatibility
```python
# GOOD (for executable compatibility)
from config import Config
from ai_router import get_router
from providers import ProviderError

# AVOID relative imports (breaks PyInstaller)
from .config import Config
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

### Fixed Issues (2025-12-10)
- ✅ **Import Regression** (2025-12-10) - Fixed executable compatibility with absolute imports
- ✅ **Security Vulnerability** (2025-12-10) - Enhanced credential storage with OWASP 2024 compliance
- ✅ **Performance Issues** (2025-12-10) - Implemented caching and background scanning
- ✅ **UI Duplication** (2025-12-10) - Consolidated components with migration path
- ✅ **Test Coverage** (2025-12-10) - Restored 7 previously ignored tests
- ✅ **Dependency Bloat** (2025-12-10) - Cleaned up requirements.txt

### Legacy Fixed Issues
- ✅ **Search Index Corruption** (2025-11-19) - TF-IDF persistence fixed
- ✅ **Circular Import** (2025-11-18) - Import patterns standardized
- ✅ **Theme System** (2025-11-17) - Unified design system

### Active Considerations
- HRM features require PyTorch installation for full functionality
- Self-hosted runner requires manual maintenance
- Headless testing requires `QT_QPA_PLATFORM=offscreen`
- Remote-only API keys (for secured Ollama endpoints) live in the system keyring (encrypted)
- Frontend requires Node.js 18+ for development
- Frontend integration with Python backend TBD (options: Electron, API server, WebView)

---

## For AI Assistants

### When Working on This Codebase

**DO:**
- ✅ Use design system components from `ui/components/`
- ✅ Use worker threads for long operations (Qt)
- ✅ Use absolute imports for executable compatibility
- ✅ Add tests for new features
- ✅ Use type hints and docstrings
- ✅ Run `python scripts/verify_ci.py` before committing
- ✅ Check CLAUDE.md for detailed information
- ✅ Follow security best practices for credential handling
- ✅ Implement proper error handling and logging

**DON'T:**
- ❌ Block the GUI thread with long operations
- ❌ Hardcode styles (use design tokens)
- ❌ Use relative imports (breaks PyInstaller executable)
- ❌ Modify built-in game profiles
- ❌ Commit sensitive data
- ❌ Assume API keys are required (except for secured remote Ollama)
- ❌ Remove security features without consultation

### Common Tasks

**Add a new game:**
1. Update `game_detector.py` with exe names
2. Create profile in `game_profile.py` or via UI

**Configure Ollama:**
1. Install Ollama: `curl https://ollama.ai/install.sh | sh`
2. Pull models: `ollama pull llama3`
3. Configure in .env (optional): `OLLAMA_BASE_URL`, `OLLAMA_MODEL` (overrides defaults)
4. Test connection via Setup Wizard or providers tab

**Add tests:**
1. Unit tests → `tests/unit/`
2. Integration tests → `tests/integration/`
3. Use fixtures from `conftest.py`
4. Add markers (`@pytest.mark.unit`)

**Deploy to staging:**
1. Merge to staging branch
2. Push (triggers workflow)
3. Or run `./scripts/deploy_staging.sh`

**Security Best Practices:**
1. Never commit API keys or credentials
2. Use system keyring for sensitive data storage
3. Follow OWASP guidelines for encryption
4. Implement proper error handling without exposing sensitive information
5. Use secure temporary directories for sensitive operations

---

## Quick Stats

- **Total LOC:** ~14,700 (src) + 3,196 (tests)
- **Test Functions:** 272
- **Test Files:** 20 (16 unit + 4 integration + 1 edge case)
- **CI Workflows:** 2
- **Supported Games:** 15 built-in + custom
- **AI Provider:** Ollama (local/remote, any model)
- **Platforms:** Windows, macOS, Linux
- **Default Model:** llama3
- **Default Base URL:** http://localhost:11434
- **Security Level:** OWASP 2024 compliant (600K PBKDF2 iterations)
- **Performance:** 2-second caching, background scanning
- **UI Framework:** PyQt6 + Optional React/TypeScript frontend

---

## Contact & Resources

- **Repository:** https://github.com/shingoku2/Omnix-All-knowing-gaming-companion
- **Issues:** GitHub Issues
- **Actions:** https://github.com/shingoku2/Omnix-All-knowing-gaming-companion/actions

---

**This file provides quick context for AI assistants. For comprehensive information, see CLAUDE.md**