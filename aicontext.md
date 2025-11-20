# AI Context - Omnix Gaming Companion

**Quick Reference for AI Assistants**
**Last Updated:** 2025-11-20

---

## Project Summary

**Omnix** is a desktop AI gaming companion built with Python and PyQt6 that provides real-time assistance for gamers using multiple AI providers (OpenAI, Anthropic, Google Gemini). A new React/TypeScript web frontend with Tailwind CSS is now available for a modern Sci-Fi/Cyberpunk UI experience.

**Backend Tech Stack:** Python 3.8+, PyQt6, psutil, OpenAI/Anthropic/Gemini APIs
**Frontend Tech Stack:** React 18, TypeScript, Tailwind CSS, Vite, Lucide Icons
**LOC:** ~14,700 lines (backend) + frontend code
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
src/                     # 14,700 LOC main source (Python/PyQt6)
├── config.py            # Configuration management
├── game_*.py            # Game detection and profiles
├── ai_*.py              # AI integration
├── knowledge_*.py       # Knowledge system
├── macro_*.py           # Macro system
├── session_*.py         # Session management
└── ui/                  # UI components and design system

frontend/                # React/TypeScript web UI (NEW - 2025-11-20)
├── src/
│   ├── App.tsx          # Main HUD component
│   ├── main.tsx         # React entry point
│   └── index.css        # Global styles + Tailwind
├── index.html           # HTML entry point
├── package.json         # Node dependencies
├── tsconfig.json        # TypeScript configuration
├── tailwind.config.js   # Tailwind theme (Omnix colors)
├── vite.config.ts       # Vite build config
└── README.md            # Frontend documentation

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

**Frontend Features:**
- Modern web-based UI alongside PyQt6 desktop app
- Vite dev server with hot module replacement
- TypeScript for type safety
- Tailwind CSS with custom Omnix theme
- Production build optimization
- Custom scrollbars and animations

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
- Frontend requires Node.js 18+ for development
- Frontend integration with Python backend TBD (options: Electron, API server, WebView)

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

## 2025-??-?? UI Neon HUD Refresh
- Implemented neon HUD styling for main dashboard panels (chat, game status, settings, AI provider) using enhanced gradients, glows, and typography.
- Added hex status widget icon layering, dual-border rendering, and brighter online indicators for closer match to concept art.
- Expanded bottom bar with settings shortcut and tightened layout spacing to mirror reference layout proportions.
- Applied updated omnix.qss styles for deep-space background, glowing buttons, chat dividers, and holographic stat chips.
- Test: `python -m compileall src/gui.py` (pass).

## 2025-11-20 React/TypeScript Frontend Implementation
- **MAJOR UPGRADE:** Created complete React/TypeScript web frontend with modern Sci-Fi/Cyberpunk aesthetic
- **Framework:** React 18 + TypeScript + Vite for fast development and optimized builds
- **Styling:** Tailwind CSS with custom Omnix theme (neon blue #00f3ff, alert red #ff2a2a)
- **Icons:** Lucide React for consistent, modern iconography
- **Fonts:** Google Fonts - Orbitron (HUD/headers), Rajdhani (body text)

### Frontend Architecture
```
frontend/
├── src/
│   ├── App.tsx          # Main HUD component with Panel wrapper
│   ├── main.tsx         # React entry point
│   └── index.css        # Global styles + Tailwind + custom animations
├── index.html           # HTML entry with font imports
├── package.json         # Node dependencies
├── tsconfig.json        # TypeScript config (strict mode)
├── tailwind.config.js   # Custom Omnix theme (colors, fonts, shadows)
├── vite.config.ts       # Vite build config (port 3000)
└── README.md            # Comprehensive frontend documentation
```

### Key Features Implemented
1. **Reusable Panel Component** - Glassmorphism container with decorative corner accents
2. **12-Column Grid Layout** - Responsive layout with chat (col 1-3), status (col 4-8), settings (col 9-12)
3. **Chat Interface** - Message bubbles with role indicators (OMNIX, USER, SYSTEM)
4. **Game Status Display** - Rotating circular border with animated pulse indicator
5. **Settings Panel** - Menu items with hover effects and smooth transitions
6. **AI Provider Selector** - Radio button groups with neon blue selection state
7. **Custom Animations** - Slow rotation (8s), pulse effects, hover transitions
8. **Custom Scrollbars** - Cyberpunk-themed with neon blue accents

### Design System
- **Colors:**
  - `omnix-dark`: #050b14 (deep space background)
  - `omnix-panel`: rgba(10, 20, 40, 0.7) (glassmorphism)
  - `omnix-blue`: #00f3ff (primary cyan neon)
  - `omnix-blueDim`: rgba(0, 243, 255, 0.1) (subtle highlights)
  - `omnix-red`: #ff2a2a (alert/accent red)
  - `omnix-text`: #e0f7ff (text color)

- **Typography:**
  - Font HUD: Orbitron (futuristic display)
  - Font Body: Rajdhani (clean sans-serif)
  - Tracking: Wide letter spacing for titles

- **Effects:**
  - Box shadows: Neon glow effects
  - Backdrop blur: Glassmorphism
  - Borders: Corner accents, gradient lines
  - Animations: Spin-slow, pulse, fade transitions

### Development Commands
```bash
cd frontend
npm install              # Install dependencies
npm run dev             # Start dev server (localhost:3000)
npm run build           # Production build
npm run preview         # Preview production build
npm run lint            # ESLint checks
```

### Next Steps for Integration
1. **Electron App** - Package as standalone desktop app
2. **API Server** - Run Python backend as REST/WebSocket API
3. **WebView Embed** - Embed in PyQt6 QWebEngineView
4. **Hybrid Mode** - Use web UI for settings, PyQt6 for system tray

### Dependencies Added
- react: ^18.2.0
- react-dom: ^18.2.0
- lucide-react: ^0.292.0 (icons)
- typescript: ^5.2.2
- tailwindcss: ^3.3.5
- vite: ^5.0.0
- @vitejs/plugin-react: ^4.2.0

### Files Created
- ✅ frontend/package.json - Node dependencies and scripts
- ✅ frontend/tsconfig.json - TypeScript configuration
- ✅ frontend/tailwind.config.js - Tailwind theme (Omnix colors)
- ✅ frontend/postcss.config.js - PostCSS for Tailwind
- ✅ frontend/vite.config.ts - Vite build configuration
- ✅ frontend/index.html - HTML entry point
- ✅ frontend/src/App.tsx - Main HUD component (330+ lines)
- ✅ frontend/src/main.tsx - React entry point
- ✅ frontend/src/index.css - Global styles + Tailwind directives
- ✅ frontend/.eslintrc.cjs - ESLint configuration
- ✅ frontend/.gitignore - Node/build artifacts
- ✅ frontend/README.md - Comprehensive documentation (200+ lines)

### Troubleshooting
- Port conflict: Change port in vite.config.ts
- Build errors: Clear node_modules and reinstall
- TypeScript errors: Ensure @types/react and @types/react-dom are installed
- Missing dependencies: Run `npm install` in frontend directory

## 2025-11-20 - UI interaction restoration (frontend)
- Added stateful chat panel in `frontend/src/App.tsx` with input handling, quick action buttons, and dynamic message list (Omnix/user messages, processing indicator) to ensure every chat control triggers visible behavior.
- Rewired settings menu to track active submenu (Overlay, General, Notifications, Privacy) and added actionable toggles (overlay layout, lock position, startup/energy/tooltips, desktop/sound/AI alerts, streamer/privacy toggles, usage sharing) so each list item opens content and updates state.
- Added active provider banner and quick action mapping so provider selection and commands visibly respond to clicks.
- Troubleshooting: multiple attempts to run `npm install` in `frontend/` (commands with and without timeout/registry overrides) hung after several minutes; processes were killed (`kill -9`). Build/test commands were not executed because dependency installation could not complete in the container environment.

## 2026-02-24 Updates
- Updated `tests/integration/test_ci_pipeline.py` to use `SessionLogger.get_recent_events` and ensure `GameProfileStore` persistence tests call the correct method signature.
- Added optional `config_dir` support to `GameProfileStore` so tests can persist profiles in temporary directories without touching user directories.
- Appended `credentials.enc` to `.gitignore` to prevent encrypted credential files from being tracked.

### Troubleshooting
- Verified fixes via `pytest tests/integration/test_ci_pipeline.py::TestCIPipeline::test_session_logger_headless tests/integration/test_ci_pipeline.py::TestDatabaseIntegrity::test_game_profile_persistence` (pass).

## 2026-02-25 UI smoke test helper
- Added `scripts/ui_test_tool.py` to drive the chat widget headlessly with a stub AI assistant, capture optional screenshots, and report bubble counts for UI validation.
- Documented usage in `TESTING.md` under the new UI Smoke Test Helper section.

### Troubleshooting
- Attempted `python scripts/ui_test_tool.py --message "UI test ping"` but exited early with `libGL.so.1` missing; tool now detects the missing OpenGL runtime and provides installation guidance while returning exit code 2.
