# CLAUDE.md - AI Assistant Guide for Omnix Gaming Companion

**Last Updated:** 2025-12-09
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

### HRM Integration - Structured Reasoning (2025-12-10) ⭐

**Implementation**: Structured reasoning templates (no neural inference)

**Why This Approach**:
- HRM model trained on puzzles (Sudoku, ARC, Maze), not gaming Q&A
- Structured templates provide immediate value without domain mismatch
- No PyTorch model loading required (faster, lighter)
- Foundation for future fine-tuning on gaming data

**Features**:
- Intelligent question type detection (puzzle, strategy, optimization, sequence)
- Multi-word phrase recognition for complex reasoning queries
- Game genre-aware routing (automatically triggers for reasoning-heavy games)
- Structured reasoning frameworks guide LLM responses
- Timeout protection (5s default, configurable)
- Graceful fallback if analysis fails

**How It Works**:
1. User asks complex reasoning question
2. HRM detects question type and game context
3. Generates structured reasoning outline (puzzle solving, strategic planning, optimization analysis, etc.)
4. Outline prepended to message sent to Ollama
5. LLM follows reasoning structure in response

**Configuration**:
```bash
# .env
HRM_ENABLED=true
HRM_MAX_INFERENCE_TIME=5.0  # Timeout in seconds
```

**Example Reasoning Types**:
- **Puzzle**: "How do I solve this maze?" → Constraint identification, state transitions, systematic search
- **Strategy**: "Best late-game approach?" → Resource analysis, objective definition, action sequencing
- **Optimization**: "Fastest leveling route?" → Criteria definition, trade-off analysis, solution comparison
- **Sequential**: "What order should I do these in?" → Dependency identification, task ordering

**Setup**: Optional PyTorch installation for future enhancements (current implementation doesn't require it)

**Future Phases** (not in scope):
- Phase 2: Load PyTorch model architecture (no weights)
- Phase 3: Fine-tune on gaming Q&A dataset (requires data collection)

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

**Last Updated:** 2025-12-09
**Maintained by:** AI assistants working on Omnix

*For user documentation, see README.md*
