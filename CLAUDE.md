# CLAUDE.md - AI Assistant Guide for Omnix Gaming Companion

**Last Updated:** 2026-08-28
**Codebase Version:** 2.0+ (Ollama-only)
**Total LOC:** ~14,700 (src) + 3,196 (tests)

---

## Quick Navigation

1. [Project Overview](#project-overview)
2. [Architecture Summary](#architecture-summary)
3. [Key Modules](#key-modules)
4. [Technology Stack](#technology-stack)
5. [Development Guide](#development-guide)
6. [Code Conventions](#code-conventions)
7. [Testing](#testing)
8. [Common Tasks](#common-tasks)
9. [Troubleshooting](#troubleshooting)

---

## Project Overview

### What is Omnix?

Omnix is a desktop AI gaming companion that:
- **Automatically detects** games via process monitoring
- **Provides AI assistance** using Ollama (local/remote LLM)
- **Integrates game knowledge** with semantic search (TF-IDF)
- **Supports macros** with keyboard/mouse automation
- **Tracks sessions** with AI-powered coaching
- **Offers modern overlay** with customizable appearance

### Key Features

- 🎯 Automatic Game Detection (15 pre-configured games)
- 🤖 Ollama AI Integration (no API keys required)
- 📚 Knowledge System (per-game knowledge packs)
- ⌨️ Macro System (record/execute macros)
- 🎨 Design System (consistent UI tokens)
- 📊 Session Coaching (AI-powered insights)

### Project Structure (Simplified)

```
omnix/
├── main.py                    # Entry point
├── BUILD.bat                  # Unified build script
├── src/
│   ├── config.py              # Configuration
│   ├── credential_store.py    # Secure storage
│   ├── game_*.py              # Game detection
│   ├── ai_*.py, providers.py  # AI integration
│   ├── knowledge_*.py         # Knowledge system
│   ├── macro_*.py             # Macros & automation
│   ├── session_*.py           # Session tracking
│   ├── gui.py, settings_*.py  # GUI components
│   └── ui/                    # Design system
└── tests/                     # Test suite
    ├── unit/                  # Unit tests
    ├── integration/           # Integration tests
    └── ui/                    # UI tests
```

**User Data:** `~/.gaming_ai_assistant/` (profiles, macros, knowledge packs, sessions)

---

## Architecture Summary

### Layered Architecture

```
Presentation (PyQt6 GUI) → Business Logic → Data/Integration → Persistence
```

### Core Data Flow

```
User Input → Game Detection → Profile Lookup → Knowledge Integration
→ AI Assistant → Ollama Provider → Session Logger → GUI Response
```

### Key Design Patterns

- **Strategy:** AI provider abstraction (`OllamaProvider`)
- **Observer:** Qt signals for events (`game_detected`, `response_ready`)
- **Singleton:** Global instances (`Config()`, `get_knowledge_index()`)
- **Repository:** Data persistence (`GameProfileStore`, `MacroStore`)
- **Thread:** Background operations (`AIWorkerThread`, `GameWatcher`)

---

## Key Modules

### Core Application

**main.py** - Entry point, initialization orchestrator
**config.py** - Configuration management (`.env` + JSON)
**credential_store.py** - Secure API key storage (AES-256, system keyring)

### Game Detection

**game_detector.py** - Process monitoring with psutil
**game_watcher.py** - Background monitoring thread (QThread)
**game_profile.py** - Per-game configurations with system prompts

### AI Integration

**ai_assistant.py** - High-level AI interface (conversation management)
**ai_router.py** - Provider routing and fallback logic
**providers.py** - `OllamaProvider` implementation
- Default: llama3 @ http://localhost:11434
- No API key required (optional for secured endpoints)
- Automatic model discovery
- Parameter translation (max_tokens → num_predict)

### Knowledge System

**knowledge_pack.py** - Data structures (sources, packs)
**knowledge_index.py** - TF-IDF semantic search (no external API)
**knowledge_integration.py** - AI conversation augmentation
**knowledge_ingestion.py** - Import from PDF/DOCX/TXT/URLs

### Macro & Automation

**macro_manager.py** - Macro definitions (8 step types: KEY_PRESS, MOUSE_CLICK, DELAY, etc.)
**macro_runner.py** - Execution engine with safety limits
**keybind_manager.py** - Global hotkey management

### Session Management

**session_logger.py** - Event tracking (questions, answers, macros)
**session_coaching.py** - AI-powered insights and tips

### GUI & Design

**gui.py** - Main window (1,800 LOC)
**ui/design_system.py** - Token-based styling system
**ui/tokens.py** - Design tokens (colors, typography, spacing)
**ui/components/** - Reusable components (buttons, inputs, cards, etc.)

---

## Technology Stack

| Layer | Technology |
|---|---|
| Language | Python 3.10+ |
| GUI Framework | PyQt6 6.6.0+ (100% native — no QWebEngineView) |
| AI Inference | Ollama (local/remote LLM) |
| Process Monitoring | psutil |
| Macro Automation | pynput |
| Security | cryptography (AES-256) + keyring |
| Licensing | Supabase (REST API) |
| Packaging | PyInstaller |

**React/QWebEngineView removed in v2.1** — see git tag `archive/react-frontend`.

---

## Development Guide

### Setup

```bash
# Clone and setup
git clone https://github.com/shingoku2/Omnix-All-knowing-gaming-companion.git
cd Omnix-All-knowing-gaming-companion
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env

# Install and configure Ollama
curl https://ollama.ai/install.sh | sh
ollama serve
ollama pull llama3

# Run application
python main.py
```

### Testing

```bash
python -m pytest                  # Run all tests
python test_before_build.py       # Pre-build validation
```

### Building

```bash
BUILD.bat                         # Automated build (Release)
BUILD.bat debug                   # Debug build (with console)
```

### CI/CD

**Self-hosted pipeline** on Proxmox infrastructure. See `docs/CI_CD_GUIDE.md` for details.

**Quick verification:**
```bash
python scripts/verify_ci.py       # Health check
./scripts/deploy_staging.sh       # Deploy to staging
```

**Workflows:**
- `.github/workflows/ci.yml` - Automated testing (flake8, pytest)
- `.github/workflows/staging-deploy.yml` - Staging deployment

---

## Code Conventions

### Python Style

- **PEP 8** compliance
- **Type hints** for functions
- **Docstrings** (Google style)
- **4 spaces** indentation

### Naming

| Type | Convention | Example |
|------|-----------|---------|
| Classes | PascalCase | `GameDetector` |
| Functions | snake_case | `detect_running_game()` |
| Constants | UPPER_SNAKE_CASE | `MAX_RETRIES` |
| Private | _leading_underscore | `_normalize_name()` |

### Qt Patterns

**Always use worker threads for long operations:**
```python
# BAD: Blocks GUI
response = ai_assistant.ask_question(question)

# GOOD: Non-blocking
worker = AIWorkerThread(ai_assistant, question)
worker.response_ready.connect(display_response)
worker.start()
```

### UI Components

**Use design system components:**
```python
# GOOD
from ui.components.buttons import OmnixButton
button = OmnixButton("Click Me", variant="primary")

# BAD - hardcoded styles
button = QPushButton("Click Me")
button.setStyleSheet("background: blue;")
```

---

## Testing

### Test Organization

```
tests/
├── unit/                 # Logic tests (no GUI)
│   ├── test_game_detector.py
│   ├── test_knowledge_system.py
│   └── ...
├── ui/                   # GUI tests
│   ├── test_gui_minimal.py
│   └── ...
└── integration/          # Integration tests
    ├── test_ollama_integration.py
    └── ...
```

### Headless Testing

```bash
# Offscreen platform (recommended for CI)
export QT_QPA_PLATFORM=offscreen
python -m pytest

# Xvfb virtual display
Xvfb :99 -screen 0 1920x1080x24 &
export DISPLAY=:99
python -m pytest
```

See `GUI_TESTING.md` for comprehensive documentation.

---

## Common Tasks

### Adding a New Game

```python
# 1. Add to game_detector.py
common_games = {
    "Your Game": ["yourgame.exe"],
}

# 2. Create profile (via UI or programmatically)
profile = GameProfile(
    id="your-game",
    display_name="Your Game",
    exe_names=["yourgame.exe"],
    system_prompt="You are an expert at Your Game...",
    default_provider="ollama",
    default_model="llama3"
)
```

### Configuring Ollama

```bash
# .env file
AI_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434  # Optional
OLLAMA_MODEL=llama3                      # Optional

# Pull models
ollama pull llama3
ollama pull mistral
```

### Creating a Knowledge Pack

```python
from knowledge_pack import KnowledgePack, KnowledgeSource

pack = KnowledgePack(
    id="game-guide",
    name="Game Guide",
    game_profile_id="elden-ring",
    sources=[
        KnowledgeSource(
            id="wiki", type="url",
            url="https://wiki.example.com",
            tags=["bosses"]
        )
    ],
    enabled=True
)

# Save and index
from knowledge_store import get_knowledge_store
from knowledge_index import get_knowledge_index

get_knowledge_store().save_pack(pack)
get_knowledge_index().index_pack(pack)
```

### Creating a Macro

```python
from macro_manager import Macro, MacroStep

macro = Macro(
    id="quick-heal",
    name="Quick Heal",
    steps=[
        MacroStep(type="KEY_PRESS", key="h"),
        MacroStep(type="DELAY", duration_ms=100)
    ]
)

from macro_store import get_macro_store
get_macro_store().save_macro(macro)
```

---

## Troubleshooting

### Game Not Detected

**Check:** Executable name in `game_detector.py:common_games`

```python
import psutil
for proc in psutil.process_iter(['name']):
    print(proc.info['name'])  # Find exact process name
```

### Knowledge Pack Search Issues

**Symptom:** Irrelevant results after restart
**Cause:** Legacy index format (pre-2025-11-19)
**Fix:**
```python
from knowledge_index import get_knowledge_index
index = get_knowledge_index()
index.rebuild_index_for_game("your-game-id")
```

### Circular Import Errors

**Check:** Consistent `src.` prefix in imports
**Fix:** Use `from src.module import X` everywhere
**Avoid:** Module names conflicting with stdlib (e.g., `types.py`)
**Test:** `python test_circular_import.py`

### GUI Freezing

**Always use worker threads:**
```python
worker = AIWorkerThread(ai_assistant, question)
worker.response_ready.connect(display_response)
worker.start()
```

### Build Errors

**Check PyInstaller spec for missing:**
- Hidden imports
- Data files
- Dependencies

**Test:** `BUILD.bat debug` (shows console errors)

---

## Recent Changes

### HRM Removal (2026-08-28)

The HRM (Hierarchical Reasoning Model) structured-reasoning integration has been removed entirely — `src/hrm_integration.py`, the `HRMSettingsTab` settings UI, `HRM_ENABLED`/`HRM_MAX_INFERENCE_TIME` config, the vendored `HRM-main/` model source, and the Tauri `hrm.rs` reasoning-prefix module are all gone. It is no longer used by the app.

### Ollama Model Dropdowns + Fetch Parsing Fix (2026-08-28, PR #221)

The dashboard's Quick Settings "AI Model" field and the Game Profile editor's Model field were static/plain inputs showing only the configured default. Both now use the same `FetchModelsThread` as the Providers settings tab to populate a live dropdown of installed Ollama models.

**Root cause fixed:** `FetchModelsThread` parsed Ollama's response as `{"models": [{"name": ...}]}`, but the installed `ollama` package actually returns a `ListResponse`/`Model` pydantic object (`Model.model`), so every fetch silently failed and fell back to the `llama3` placeholder everywhere.

Also fixed two unrelated pre-existing crashes hit while testing:
- `main.py` / `license_dialog.py` called `credential_store.get_credential`/`set_credential` with the old single-arg signature; the store now requires `(service, key)`.
- `gui.py`'s `OverlayWindow` called the now-renamed `design_system.get_overlay_stylesheet` instead of `generate_overlay_stylesheet`.

### Codebase Audit Fixes + Dependency Updates (2026-08-28, PR #220)

**Security/reliability fixes:**
- `credential_store.py`: added missing `sys` import (crashed the interactive password-prompt fallback), wired up the previously-unused `FileLock` for real cross-process locking, scoped the password-fallback key file per-instance instead of one shared global temp-dir path, and routed save/delete through the existing atomic-write helper.
- `gui.py`: escaped sender/text before interpolating into the chat `QTextEdit` HTML (was vulnerable to HTML injection via chat content).
- `knowledge_ingestion.py`: blocked SSRF in URL-based knowledge pack ingestion — validates scheme and resolved IP (rejects loopback/private/link-local/reserved) on the initial URL and every redirect hop.
- `keybind_manager.py`: `KeybindManager` is now a `QObject` that dispatches global hotkey callbacks through a queued signal, so they run on the Qt GUI thread instead of the pynput listener thread touching widgets directly.
- `base_store.py`, `session_logger.py`: JSON writes are now atomic (temp file + `os.replace`); `session_logger` also flushes every event instead of every 10th and fixes session-ID parsing for `game_profile_id` values containing underscores.
- `config.py`: a plaintext `AI_API_KEY` found in `.env` is migrated into the encrypted `CredentialStore` instead of being written back to disk in plaintext on every settings save (only once the vault migration actually succeeds — otherwise it's still written in plaintext so the key isn't lost).
- `ai_assistant.py`: `clear_history()` no longer locks the AI into a persona for a game literally named "Unknown Game" when no game is detected.
- `settings_tabs.py`: added the missing `Config` import — `save_config()` called `Config.save_to_env()` without it, raising `NameError` at runtime.

**Test suite:** fixed pre-existing bugs in `test_core.py`, `test_gui.py`, `test_imports.py`, `test_overlay_geometry.py`, `test_session_coaching.py` (and the now-removed `test_hrm_integration.py`). Full suite went from 346 passed/12 failing to 358 passed/8 skipped (torch not installed)/0 failing.

**Dependencies:** bumped React, Vite, ESLint, and other devDependencies in `frontend/` and `omnix-tauri/` to latest compatible versions (TypeScript held at 5.9.x; Tailwind held at 3.x — 4.x needs a config migration neither project has done); `npm audit fix` in `omnix-tauri/`.

**CI:** fixed the Omnix Tauri GitHub Actions workflow, which had been broken on every run since it was introduced — wrong action reference (`dtolnay/rust-toolchain@stable`, not `rust-action`), a `WindowConfig.label` type mismatch after a Tauri version bump, unused-variable TS6133 build failures, missing Linux system deps (`libwebkit2gtk-4.1-dev`, `libxdo-dev` for enigo) on `rust-check`, and a Rust `tauri` crate version pinned behind the npm `@tauri-apps/api` version.

### Ollama-Only Migration (2025-12-06) ⭐

**Why:** Privacy-first, no API costs, local inference, model freedom

**Changes:**
- Removed OpenAI, Anthropic, Gemini providers
- Simplified to single `OllamaProvider`
- No API key storage needed (unless secured endpoint)
- Automatic model discovery
- UI shows available Ollama models

**Setup:**
```bash
curl https://ollama.ai/install.sh | sh
ollama serve
ollama pull llama3
python main.py  # Auto-detects Ollama
```

### CI/CD Enhancement (2025-11-20)

- Self-hosted runner on Proxmox LXC
- Automated testing and deployment
- See `docs/CI_CD_GUIDE.md`

### Search Index Fix (2025-11-19) ⭐

**Fixed:** TF-IDF model persistence - search results now consistent across restarts

### Theme System Unification (2025-11-17)

**Unified token-based design system** with backward compatibility

---

## Best Practices

### ✅ DO

1. Use design system components
2. Use worker threads for long operations
3. Type hint function signatures
4. Test before committing
5. Follow naming conventions

### ❌ DON'T

1. Block GUI thread
2. Hardcode styles
3. Store API keys in .env
4. Skip error handling
5. Modify core architecture without discussion

---

## Quick Reference

### File Locations

```
Main:        main.py
Config:      src/config.py
Game:        src/game_detector.py
AI:          src/ai_assistant.py, src/providers.py
Knowledge:   src/knowledge_*.py
Macros:      src/macro_*.py
GUI:         src/gui.py
UI System:   src/ui/design_system.py
User Data:   ~/.gaming_ai_assistant/
```

### Key Commands

```bash
python main.py                    # Run app
python test_before_build.py       # Test
BUILD.bat                         # Build
python -m pytest                  # All tests
```

### Resources

- **Repository:** https://github.com/shingoku2/Omnix-All-knowing-gaming-companion
- **Branch:** `claude/update-context-files-014mNueuX6ktLe9z76DJrpY9`
- **Ollama:** https://ollama.ai
- **CI/CD:** `docs/CI_CD_GUIDE.md`
- **Testing:** `GUI_TESTING.md`

---

**Last Updated:** 2026-08-28
**Maintained by:** AI assistants working on Omnix

*For user documentation, see README.md*
