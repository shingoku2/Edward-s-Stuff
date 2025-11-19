# Omnix Gaming Companion - AI Coding Agent Instructions

**Project:** Omnix - All-knowing Gaming Companion  
**Stack:** Python 3.8+, PyQt6, Multi-Provider AI (OpenAI/Anthropic/Gemini)  
**Status:** Active development (~14,700 LOC)

## Architecture Overview

Omnix follows a **strict layered architecture** designed for AI integration:

```
Presentation (gui.py, ui/*, *_dialog.py)
    ↓ PyQt6 signals
Business Logic (ai_assistant.py, game_watcher.py, macro_runner.py)
    ↓ Dependency injection
Data/Integration (providers.py, ai_router.py, game_detector.py)
    ↓ Store pattern
Persistence (config.py, credential_store.py, *_store.py)
```

**Critical:** Always respect layer boundaries. GUI changes must flow through signals, never direct imports up the stack.

## Core Data Flows

### Game Detection → AI Response Pipeline
1. `GameWatcher` monitors active process (5s intervals via `game_detector.py`)
2. Matches against `game_profile.json` (15 pre-configured games)
3. Looks up game-specific system prompt from `GameProfile`
4. `KnowledgeIntegration` augments prompt with semantic search results from knowledge packs
5. `AIRouter` dispatches to active provider (Anthropic/OpenAI/Gemini)
6. `SessionLogger` records interaction for coaching analysis

**Key insight:** Game detection is passive polling, not event-driven. UI updates via Qt signals only.

### Multi-Provider Architecture
- **AIProvider Protocol**: Defines common interface (`chat()`, `get_health()`)
- **Factory Pattern**: `create_provider(name, api_key)` in `providers.py`
- **Router Selection**: `AIRouter.send_message()` uses `config.ai_provider` to pick implementation
- **Error Cascade**: Auth → Quota → RateLimit → Fallback (logged, never silent)

**Convention:** All provider-specific code stays in `providers.py`. Never hardcode provider logic elsewhere.

## Essential Patterns & Conventions

### Configuration Management (`config.py`)
- Singleton pattern via `Config()` constructor
- Three-tier loading: `.env` → `~/.gaming_ai_assistant/*.json` → runtime memory
- **Critical:** Use `config.get_api_key(provider_name)` (retrieves from secure keyring), not raw `config.{provider}_api_key`
- Window position/size auto-persisted; call `config.save()` after changes

### Credential Security (`credential_store.py`)
- **Windows:** System Credential Manager (native)
- **macOS/Linux:** Keyring + AES-256 fallback encryption
- **CI/CD:** Set `OMNIX_MASTER_PASSWORD` env var for encrypted storage
- Never log API keys; use `CredentialStore` exclusively

### Persistence Layer (`*_store.py` pattern)
- **Pattern:** `GameProfileStore`, `MacroStore`, `KnowledgePackStore` all follow same interface
- Methods: `get_all()`, `get_by_id()`, `save()`, `delete()` with consistent error handling
- **Location:** `~/.gaming_ai_assistant/` (platform-specific via `Path.home()`)
- Index files (e.g., `macros.json`) separate from individual data files

### Knowledge System (`knowledge_index.py` + `knowledge_integration.py`)
- **SimpleTFIDFEmbedding:** Local, no API calls (TF-IDF based, not transformer)
- **Semantic Search:** Returns `RetrievedChunk` objects with `content`, `source_id`, `relevance_score`
- **Integration:** `augment_prompt()` prepends relevant chunks before AI call
- **Limitation:** Currently TF-IDF; extensible for sentence-transformers if needed

### PyQt6 Signals & Threading (`gui.py`, `game_watcher.py`)
- **Pattern:** Long-running ops → `QThread` subclass + `pyqtSignal` for results
- `AIWorkerThread` handles AI calls; emits `response_ready` or `error_occurred`
- **Important:** Never block the main thread; use `time.sleep()` in worker threads only
- Example: `game_changed = pyqtSignal(str, object)` → `game_changed.connect(on_game_changed_handler)`

### UI Design System (`src/ui/`)
- **Tokens:** All colors/spacing/typography centralized in `tokens.py` (COLORS, SPACING, RADIUS, TYPOGRAPHY)
- **Components:** Reusable in `components/` (OmnixButton, OmnixLineEdit, OmnixTextEdit, etc.)
- **Convention:** Always import from `ui.tokens` and `ui.components`, never hardcode values
- **Colors:** Dark theme (#1A1A2E base, #00BFFF accent, #39FF14 success)

### Macro System (`macro_runner.py`, `keybind_manager.py`)
- **Execution:** `MacroRunner.execute_macro()` runs in background thread
- **Anti-Cheat Aware:** Check `enabled` flag; some games don't allow automation
- **Input Simulation:** Uses `pynput` library (graceful fallback if unavailable)
- **Steps:** Each step is `MacroStep` with `step_type` (KEYSTROKE, DELAY, MOUSE_MOVE, etc.)
- **State Machine:** `MacroExecutionState` enum tracks IDLE → RUNNING → PAUSED/STOPPED

## Developer Workflows

### Setup & Testing
```pwsh
# Install dependencies (Windows PowerShell)
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Run all tests
pytest

# Run with coverage report
pytest --cov=src --cov-report=html
```

### Running Locally
```pwsh
# Set environment variables
$env:QT_QPA_PLATFORM="offscreen"  # For headless testing
$env:OMNIX_MASTER_PASSWORD="dev-password"  # For CI/credential testing

# Start application
python main.py
```

### Building Windows Executable
```pwsh
# Automated (recommended)
.\BUILD_WINDOWS.bat

# Manual
pip install pyinstaller
pyinstaller GamingAIAssistant.spec
# Output: dist\GamingAIAssistant\GamingAIAssistant.exe
```

### Adding New Game Profile
1. Add entry to default profiles in `game_profile.py` (exe_names, system_prompt)
2. Test detection with `game_detector.py` (check process matching logic)
3. Create knowledge pack in UI or programmatically
4. Update `game_profiles.json` via `GameProfileStore.save()`

## Testing Conventions

- **Unit tests:** `tests/unit/` - Mock everything external (providers, processes, files)
- **Integration tests:** `tests/integration/` - Real file I/O, fake API responses
- **Markers:** `@pytest.mark.windows` (platform-specific), `@pytest.mark.requires_api_key` (skip in CI)
- **Fixtures:** `conftest.py` provides `temp_dir`, `config`, `mock_api_key`, `game_detector`
- **Qt Testing:** Set `QT_QPA_PLATFORM=offscreen` before importing PyQt6

## Common Tasks

### Adding AI Provider
1. Create class inheriting from `AIProvider` protocol in `providers.py`
2. Implement: `chat(messages, **kwargs)`, `get_health()`, `validate_key()`
3. Update `create_provider()` factory
4. Add tests in `tests/unit/test_providers.py`
5. Config automatically supports via `ai_provider=newprovider`

### Debugging Game Detection
- Check logs: `gaming_ai_assistant_*.log` in project root or `~/.gaming_ai_assistant/logs/`
- `GameDetector.get_foreground_process()` is platform-specific (Windows: GetForegroundWindow)
- Test manually: `python -c "from game_detector import GameDetector; print(GameDetector().get_foreground_process())"`

### Handling Async API Calls
- **Pattern:** `AIWorkerThread` in GUI (spawns QThread for blocking calls)
- **Never:** Use `asyncio` directly; PyQt6 event loop conflicts
- **Alternative:** Consider `concurrent.futures.ThreadPoolExecutor` for non-GUI code

## Key Files Reference

| File | Purpose | Size | Complexity |
|------|---------|------|-----------|
| `main.py` | Entry point & initialization | 316 LOC | Low |
| `gui.py` | Main UI window | 1,526 LOC | High |
| `providers.py` | AI provider abstraction | 537 LOC | Medium |
| `ai_router.py` | Multi-provider routing | 295 LOC | Medium |
| `game_watcher.py` | Game detection threading | 259 LOC | Medium |
| `macro_runner.py` | Macro execution engine | 512 LOC | High |
| `knowledge_index.py` | TF-IDF semantic search | 566 LOC | High |
| `config.py` | Configuration management | 350 LOC | Medium |
| `credential_store.py` | Secure key storage | 250 LOC | Medium |

## Debugging Tips

**UI Freezes:** Check for blocking calls on main thread; wrap in `AIWorkerThread`  
**Game Not Detected:** Verify exe name in `game_profiles.json`; check process matching logic  
**API Key Issues:** Ensure stored in keyring; test via `CredentialStore.get_key()`  
**Qt Import Errors:** Set `QT_QPA_PLATFORM=offscreen` for headless environments  
**Macro Not Executing:** Verify `MacroRunner.enabled=True` and `pynput` available

## Extension Points

- **New Knowledge Sources:** Extend `KnowledgeSource` dataclass + add ingestion method
- **Custom UI Components:** Inherit from PyQt6 base + add to `ui/components/`
- **Session Analysis:** Extend `SessionLogger` with new event types
- **Macro Step Types:** Add to `MacroStepType` enum + handler in `MacroRunner`

---

**Last Updated:** 2025-11-18 | **Version:** 1.2+
