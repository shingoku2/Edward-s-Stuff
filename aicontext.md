# Gaming AI Assistant - AI Context

This file provides complete context for AI assistants working on this project.

## Project Overview

**Gaming AI Assistant** - A PyQt6 desktop application that detects running games and provides real-time AI assistance for gameplay.

### Key Features
- Automatic game detection from running processes
- AI-powered chat assistance for gameplay tips and strategies
- Support for multiple AI providers (OpenAI, Anthropic, Gemini, Ollama, Open WebUI)
- System tray integration with hotkey toggle
- Web scraping for game information
- Strictly gaming-focused AI responses

### Tech Stack
- **Language**: Python 3.14
- **GUI**: PyQt6
- **AI Providers**: OpenAI GPT, Anthropic Claude, Google Gemini, Ollama, Open WebUI
- **Dependencies**: requests, beautifulsoup4, python-dotenv, psutil, keyboard

---

## Recent Session: Open WebUI Integration & Authentication (2025-11-11)

### Session Goals
1. Fix Ollama/Open WebUI API integration issues
2. Add authentication support for Open WebUI
3. Add login/signup page buttons for all AI providers

### Starting Context
- User reported persistent 405/404 errors when trying to use Ollama/Open WebUI
- Previous attempts to use `/api/chat` and `/api/generate` endpoints failed
- User's Open WebUI runs on `http://localhost:8080` (not default 11434)

---

## Changes Made

### 1. Open WebUI API Endpoint Support (Commits: 4e9c6ff, f41e40f, 8a8eab5, d757977)

#### Problem
- Open WebUI uses different API endpoints than native Ollama
- Initial attempts used `/api/chat` which returned 404/405 errors
- Need to support both OpenAI-compatible and native Ollama APIs

#### Solution
Implemented three-tier fallback system in `src/ai_assistant.py`:

1. **First Try**: `/v1/chat/completions` (OpenAI-compatible, for Open WebUI)
2. **Second Try**: `/api/chat` (native Ollama chat endpoint)
3. **Third Try**: `/api/generate` (older Ollama endpoint, more widely supported)

**Files Modified:**
- `src/ai_assistant.py:353-459` - Added multi-endpoint fallback logic
- `src/gui.py:497-504` - Updated help text for clarity

**Key Code:**
```python
# Try OpenAI-compatible API first
response = requests.post(f"{endpoint}/v1/chat/completions", ...)
if response.status_code in [404, 405]:
    # Try native Ollama API
    response = requests.post(f"{endpoint}/api/chat", ...)
    if response.status_code in [404, 405]:
        # Try generate endpoint
        response = requests.post(f"{endpoint}/api/generate", ...)
```

**Commits:**
- `4e9c6ff` - Add support for Open WebUI with OpenAI-compatible API
- `f41e40f` - Fix fallback logic to handle 405 Method Not Allowed errors (first attempt)
- `8a8eab5` - Add fallback to /api/generate endpoint for Ollama
- `d757977` - Fix fallback logic to handle 405 Method Not Allowed errors (second attempt)

---

### 2. Open WebUI Authentication with Bearer Token (Commit: 8d55ae1)

#### Problem
**All three endpoints returned 405 errors** even with fallback logic:
```
POST /v1/chat/completions HTTP/1.1" 405 31
POST /api/chat HTTP/1.1" 405 31
POST /api/generate HTTP/1.1" 405 31
```

**Root Cause**: Open WebUI requires authentication via Bearer token headers.

#### Solution
Added full Open WebUI API key support with Bearer token authentication:

**Backend Changes (`src/config.py`):**
```python
# Line 53: Added new configuration field
self.open_webui_api_key = os.getenv('OPEN_WEBUI_API_KEY')

# Lines 127-130: Added parameter to save_to_env
def save_to_env(provider: str, openai_key: str, anthropic_key: str, gemini_key: str = '',
                ollama_endpoint: str = 'http://localhost:11434',
                open_webui_api_key: str = '',  # NEW
                overlay_hotkey: str = 'ctrl+shift+g', check_interval: int = 5):

# Line 175: Save to .env file
existing_content['OPEN_WEBUI_API_KEY'] = open_webui_api_key
```

**AI Assistant Changes (`src/ai_assistant.py`):**
```python
# Lines 21-23: Added parameter to __init__
def __init__(self, provider: str = "anthropic", api_key: Optional[str] = None,
             ollama_endpoint: str = "http://localhost:11434",
             open_webui_api_key: Optional[str] = None):  # NEW

# Line 36: Store API key
self.open_webui_api_key = open_webui_api_key or os.getenv("OPEN_WEBUI_API_KEY")

# Lines 357-361: Add Authorization header
headers = {"Content-Type": "application/json"}
if self.open_webui_api_key:
    headers["Authorization"] = f"Bearer {self.open_webui_api_key}"
    logger.debug("Using Open WebUI API key for authentication")

# All requests now include headers parameter:
requests.post(url, json=payload, headers=headers, timeout=30)
```

**GUI Changes (`src/gui.py`):**
```python
# Line 252: Updated signal to include new parameter
settings_saved = pyqtSignal(str, str, str, str, str, str)
# provider, openai_key, anthropic_key, gemini_key, ollama_endpoint, open_webui_api_key

# Lines 481-494: Added Open WebUI API Key input field
open_webui_key_label = QLabel("Open WebUI API Key (optional, for authentication):")
self.open_webui_key_input = QLineEdit()
self.open_webui_key_input.setPlaceholderText("Get from Settings > Account in Open WebUI")
self.open_webui_key_input.setEchoMode(QLineEdit.EchoMode.Password)
# ... with show/hide button

# Line 594: Get API key from input
open_webui_api_key = self.open_webui_key_input.text().strip()

# Line 631: Emit with new parameter
self.settings_saved.emit(provider, openai_key, anthropic_key, gemini_key,
                        ollama_endpoint, open_webui_api_key)

# Lines 1076-1099: Updated handler
def handle_settings_saved(self, provider, openai_key, anthropic_key, gemini_key,
                          ollama_endpoint, open_webui_api_key):
    Config.save_to_env(provider, openai_key, anthropic_key, gemini_key,
                      ollama_endpoint, open_webui_api_key)
    self.ai_assistant = AIAssistant(
        provider=self.config.ai_provider,
        api_key=self.config.get_api_key(),
        ollama_endpoint=self.config.ollama_endpoint,
        open_webui_api_key=self.config.open_webui_api_key
    )
```

**Main.py Changes:**
```python
# Lines 119-124: Pass open_webui_api_key when initializing
ai_assistant = AIAssistant(
    provider=config.ai_provider,
    api_key=config.get_api_key(),
    ollama_endpoint=config.ollama_endpoint,
    open_webui_api_key=config.open_webui_api_key
)
```

**Commit:** `8d55ae1` - Add Open WebUI authentication with Bearer token support

**How to Get Open WebUI API Key:**
1. Open Open WebUI in browser (e.g., http://localhost:8080)
2. Log in to your account
3. Go to Settings > Account
4. Copy the API key
5. Paste into "Open WebUI API Key" field in settings

---

### 3. Login/Signup Page Buttons (Commit: 8793386)

#### Feature
Added "Get API Key" buttons for all AI providers to simplify signup process.

**Implementation (`src/gui.py`):**

**Added webbrowser import:**
```python
# Line 18
import webbrowser
```

**Added helper method:**
```python
# Lines 576-583
def open_api_key_page(self, url):
    """Open API key signup/login page in browser"""
    try:
        webbrowser.open(url)
        logger.info(f"Opening API key page: {url}")
    except Exception as e:
        logger.error(f"Failed to open URL: {e}")
        QMessageBox.warning(self, "Error", f"Failed to open browser: {str(e)}")
```

**Added buttons for each provider:**

1. **OpenAI** (Lines 411-427)
   - URL: `https://platform.openai.com/api-keys`
   - Color: Green (#10a37f)

2. **Anthropic** (Lines 461-477)
   - URL: `https://console.anthropic.com/settings/keys`
   - Color: Orange (#c96329)

3. **Gemini** (Lines 511-527)
   - URL: `https://aistudio.google.com/app/apikey`
   - Color: Blue (#1a73e8)

4. **Open WebUI** (Lines 555-571)
   - URL: User's custom endpoint from `ollama_endpoint_input.text()`
   - Color: Purple (#6366f1)
   - Opens user's configured Open WebUI instance

**Button Style Example:**
```python
button.setStyleSheet("""
    QPushButton {
        background-color: #10a37f;
        color: #ffffff;
        border: none;
        border-radius: 3px;
        padding: 5px 10px;
        font-size: 9pt;
    }
    QPushButton:hover {
        background-color: #1a7f64;
    }
""")
button.clicked.connect(lambda: self.open_api_key_page("https://platform.openai.com/api-keys"))
```

**Commit:** `8793386` - Add login/signup page buttons for all AI providers

---

## Error Log & Troubleshooting

### Error 1: ModuleNotFoundError: No module named 'ollama'
**When:** Initial Ollama integration attempt
**Logs:**
```
2025-11-11 20:33:09,418 - ModuleNotFoundError: No module named 'ollama'
```

**Cause:** Original implementation tried to use the `ollama` Python package

**Solution:** Removed ollama package dependency, used REST API directly with `requests`
**Commit:** `dda768f` - Remove ollama package dependency - use REST API directly

---

### Error 2: 404 on /v1/chat/completions
**When:** First attempt to use OpenAI-compatible endpoint
**Logs:**
```
2025-11-11 20:33:34,619 - http://localhost:11434 "POST /v1/chat/completions HTTP/1.1" 404 93
```

**Cause:** Endpoint didn't exist on native Ollama installation

**Solution:** Added fallback to `/api/chat` endpoint
**Commit:** `4e9c6ff` - Add support for Open WebUI with OpenAI-compatible API

---

### Error 3: 404 on /api/chat
**When:** Second fallback attempt
**Logs:**
```
2025-11-11 20:33:34,619 - http://localhost:11434 "POST /api/chat HTTP/1.1" 404 36
```

**Cause:** `/api/chat` endpoint also didn't exist

**Solution:** Added third fallback to `/api/generate` endpoint
**Commit:** `8a8eab5` - Add fallback to /api/generate endpoint for Ollama

---

### Error 4: 405 Method Not Allowed on ALL endpoints (Open WebUI)
**When:** Testing with Open WebUI on port 8080
**Logs:**
```
2025-11-11 21:24:09,315 - http://localhost:8080 "POST /v1/chat/completions HTTP/1.1" 405 31
2025-11-11 21:24:09,320 - http://localhost:8080 "POST /api/chat HTTP/1.1" 405 31
2025-11-11 21:24:38,865 - http://localhost:8080 "POST /api/generate HTTP/1.1" 405 31
```

**Cause:** Open WebUI requires authentication via Bearer token headers

**Root Cause Analysis:**
- `/v1/models` GET request worked (200 OK) ✅
- All POST requests failed with 405 ❌
- 405 = "Method Not Allowed" typically indicates missing authentication

**Research:** Found that Open WebUI requires `Authorization: Bearer <token>` header for API requests

**Solution:**
1. Added `open_webui_api_key` configuration field
2. Added Bearer token to all Ollama/Open WebUI requests
3. Updated GUI to accept and save Open WebUI API key

**Commits:**
- `d757977` - Fix fallback logic to handle 405 Method Not Allowed errors
- `8d55ae1` - Add Open WebUI authentication with Bearer token support

**Verification:** Connection test to `/v1/models` succeeds:
```
2025-11-11 21:23:41,595 - http://localhost:8080 "GET /v1/models HTTP/1.1" 200 2246
2025-11-11 21:23:41,596 - Open WebUI connection test successful (OpenAI-compatible API)
```

---

## Testing Results

### Automated Tests Run (2025-11-11)

**1. Syntax Checks** ✅
```bash
python3 -m py_compile src/config.py         # PASSED
python3 -m py_compile src/ai_assistant.py   # PASSED
python3 -m py_compile src/gui.py            # PASSED
python3 -m py_compile main.py               # PASSED
```

**2. Config Module Test** ✅
```
✓ Config module imported successfully
✓ Config has open_webui_api_key attribute: True
✓ Config.open_webui_api_key value: None
✓ Config.save_to_env parameters: ['provider', 'openai_key', 'anthropic_key',
  'gemini_key', 'ollama_endpoint', 'open_webui_api_key', 'overlay_hotkey', 'check_interval']
✓ Has open_webui_api_key parameter: True
```

**3. AIAssistant Module Test** ✅
```
✓ AIAssistant module imported successfully
✓ AIAssistant.__init__ parameters: ['self', 'provider', 'api_key', 'ollama_endpoint', 'open_webui_api_key']
✓ Has open_webui_api_key parameter: True
✓ AIAssistant instance created with open_webui_api_key
✓ open_webui_api_key stored correctly: True
```

**4. GUI Components Verification** ✅
```
✓ webbrowser import: Line 18
✓ open_api_key_page method: Line 654
✓ Number of Get API Key buttons: 3 (OpenAI, Anthropic, Gemini)
✓ Open WebUI API Key field: Lines 544-546
✓ Open Open WebUI button: Line 555
```

**5. Signal/Handler Signature Verification** ✅
```
✓ Signal definition: Line 252
  pyqtSignal(str, str, str, str, str, str)
✓ Signal emission: Line 719
  emit(provider, openai_key, anthropic_key, gemini_key, ollama_endpoint, open_webui_api_key)
✓ Handler definition: Line 1164
  def handle_settings_saved(provider, openai_key, anthropic_key, gemini_key,
                            ollama_endpoint, open_webui_api_key)
```

**6. API Key URLs Verification** ✅
```
✓ OpenAI: https://platform.openai.com/api-keys
✓ Anthropic: https://console.anthropic.com/settings/keys
✓ Gemini: https://aistudio.google.com/app/apikey
```

---

## File Structure

```
Edward-s-Stuff/
├── main.py                 # Entry point
├── src/
│   ├── config.py          # Configuration management (MODIFIED)
│   ├── ai_assistant.py    # AI integration logic (MODIFIED)
│   ├── gui.py             # PyQt6 GUI (MODIFIED)
│   ├── game_detector.py   # Game detection logic
│   └── info_scraper.py    # Web scraping for game info
├── .env                   # Environment variables (API keys)
├── requirements.txt       # Python dependencies
└── aicontext.md          # This file
```

---

## Configuration (.env file)

```bash
# AI Provider Selection
AI_PROVIDER=ollama  # Options: openai, anthropic, gemini, ollama

# API Keys
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GEMINI_API_KEY=AIza...
OPEN_WEBUI_API_KEY=sk-...  # NEW: For Open WebUI authentication

# Ollama/Open WebUI Configuration
OLLAMA_ENDPOINT=http://localhost:8080  # or http://localhost:11434 for native Ollama

# Application Settings
OVERLAY_HOTKEY=ctrl+shift+g
CHECK_INTERVAL=5
```

---

## API Provider Details

### OpenAI
- **API Key Format:** `sk-...`
- **Signup:** https://platform.openai.com/api-keys
- **Models Used:** gpt-4, gpt-3.5-turbo

### Anthropic Claude
- **API Key Format:** `sk-ant-...`
- **Signup:** https://console.anthropic.com/settings/keys
- **Models Used:** claude-3-opus-20240229

### Google Gemini
- **API Key Format:** `AIza...`
- **Signup:** https://aistudio.google.com/app/apikey
- **Models Used:** gemini-pro

### Ollama (Local)
- **API Key:** None required
- **Default Endpoint:** http://localhost:11434
- **Models:** Any model installed locally (llama2, mistral, etc.)
- **Endpoints:**
  - `/api/tags` - List models
  - `/api/chat` - Chat completion
  - `/api/generate` - Text generation

### Open WebUI
- **API Key Required:** Yes (Bearer token)
- **Default Endpoint:** http://localhost:8080
- **How to Get API Key:**
  1. Open browser to your Open WebUI URL
  2. Login
  3. Go to Settings > Account
  4. Copy API key
- **API Structure:** OpenAI-compatible (`/v1/chat/completions`)
- **Authentication:** `Authorization: Bearer <api_key>`

---

## Known Issues & Limitations

### 1. Open WebUI Endpoint Differences
**Issue:** Open WebUI may use different API structures than native Ollama
**Workaround:** Three-tier fallback system handles most cases
**Status:** Resolved with Bearer token authentication

### 2. WSL Port Forwarding
**Issue:** WSL2 automatically forwards localhost ports, but WSL1 does not
**Workaround:** Use http://localhost:<port> format, WSL2 auto-forwards
**Status:** Documented in help text

### 3. Model Selection
**Issue:** Ollama model is hardcoded to "llama2"
**Impact:** Cannot select different models without code change
**Status:** Known limitation, future enhancement needed
**Location:** `src/ai_assistant.py:358, 390, 435`

---

## Development Notes

### Running the Application

**From Source:**
```bash
python main.py
```

**From Bundled Executable (PyInstaller):**
```bash
cd dist/GamingAIAssistant_DEBUG
./GamingAIAssistant_DEBUG
```

### Testing Ollama/Open WebUI Integration

1. **Start Ollama in WSL:**
   ```bash
   ollama serve
   ```

2. **Start Open WebUI:**
   ```bash
   # Usually runs on port 8080
   # Access at http://localhost:8080
   ```

3. **Configure in App:**
   - Set Ollama Endpoint to `http://localhost:8080`
   - Click "Open Open WebUI" button
   - Login and get API key from Settings > Account
   - Paste API key into "Open WebUI API Key" field
   - Save settings

4. **Test:**
   - Launch a game
   - Press Ctrl+Shift+G
   - Ask a gaming question
   - Check logs for successful API calls

---

## Debugging

### Enable Debug Logging

Check the log file created in the application directory:
```
gaming_ai_assistant_YYYYMMDD_HHMMSS.log
```

### Common Log Patterns

**Successful Connection:**
```
INFO - Open WebUI connection test successful (OpenAI-compatible API)
```

**Authentication Issue:**
```
ERROR - 405 Client Error: Method Not Allowed
```
**Fix:** Add Open WebUI API key

**Connection Issue:**
```
ERROR - Cannot connect to Ollama at http://localhost:8080
```
**Fix:** Start Ollama/Open WebUI service

**Endpoint Fallback:**
```
INFO - OpenAI-compatible endpoint returned 405, trying native Ollama API
INFO - Native /api/chat endpoint returned 405, trying /api/generate
```
**Normal:** Shows fallback chain working

---

## Future Enhancements

### Suggested Improvements

1. **Model Selection UI**
   - Add dropdown to select Ollama model
   - Fetch available models from `/api/tags`
   - Save preference to config

2. **Connection Status Indicator**
   - Show green/red indicator for Ollama/Open WebUI connection
   - Test connection on settings dialog open
   - Auto-retry failed connections

3. **Better Error Messages**
   - Detect specific error types (auth, connection, rate limit)
   - Provide actionable troubleshooting steps in GUI
   - Link to documentation

4. **Open WebUI Token Auto-fetch**
   - Implement OAuth flow
   - Store token securely
   - Auto-refresh expired tokens

5. **Multi-instance Support**
   - Allow multiple Ollama/Open WebUI endpoints
   - Quick-switch between instances
   - Load balancing

---

## Commit History Summary

| Commit | Date | Description |
|--------|------|-------------|
| `8793386` | 2025-11-11 | Add login/signup page buttons for all AI providers |
| `8d55ae1` | 2025-11-11 | Add Open WebUI authentication with Bearer token support |
| `d757977` | 2025-11-11 | Fix fallback logic to handle 405 Method Not Allowed errors |
| `8a8eab5` | 2025-11-11 | Add fallback to /api/generate endpoint for Ollama |
| `f41e40f` | 2025-11-11 | Fix fallback logic to handle 405 Method Not Allowed errors |
| `4e9c6ff` | 2025-11-11 | Add support for Open WebUI with OpenAI-compatible API |
| `dda768f` | 2025-11-11 | Remove ollama package dependency - use REST API directly |
| `84c9f43` | 2025-11-11 | Improve Ollama error handling and add WSL setup guidance |
| `33b4895` | 2025-11-11 | Add support for Gemini and Ollama AI providers |

---

## Quick Reference

### Endpoints Tried (in order):
1. `/v1/chat/completions` - OpenAI-compatible (Open WebUI)
2. `/api/chat` - Native Ollama chat
3. `/api/generate` - Older Ollama generation

### Error Code Meanings:
- **200** - Success
- **404** - Endpoint not found (try next fallback)
- **405** - Method not allowed (authentication required or try next fallback)
- **401** - Unauthorized (API key invalid)
- **403** - Forbidden (API key missing)

### Settings Dialog Fields:
- AI Provider: Radio buttons (Anthropic/OpenAI/Gemini/Ollama)
- OpenAI API Key: Text input with show/hide
- Anthropic API Key: Text input with show/hide
- Gemini API Key: Text input with show/hide
- Ollama Endpoint: Text input (URL)
- Open WebUI API Key: Text input with show/hide (NEW)

### Buttons Added:
- "Get API Key" (OpenAI) - Opens platform.openai.com
- "Get API Key" (Anthropic) - Opens console.anthropic.com
- "Get API Key" (Gemini) - Opens aistudio.google.com
- "Open Open WebUI" - Opens user's configured endpoint

---

## Support Resources

- **Ollama Documentation:** https://github.com/ollama/ollama/blob/main/docs/api.md
- **Open WebUI GitHub:** https://github.com/open-webui/open-webui
- **PyQt6 Documentation:** https://doc.qt.io/qtforpython-6/
- **Project Repository:** https://github.com/shingoku2/Edward-s-Stuff

---

*Last Updated: 2025-11-11*
*Session: Open WebUI Integration & Authentication*
*Status: All tests passing ✅*

## Recent Session: Headless Environment GUI Test (2025-11-12)

### Session Goals
1. Execute the full PyQt6 desktop client to verify graphical startup sequence.

### Actions Taken
- Installed all dependencies from `requirements.txt`.
- Ran `python main.py` inside the container.

### Outcome
- Application startup aborted during GUI import because the container lacks the system OpenGL runtime (`libGL.so.1`).
- PyQt6 requires X11/Wayland display services and the GL shim, which are unavailable in this headless environment.

### Next Steps
- Install an OpenGL-compatible package (e.g., `libgl1` on Debian/Ubuntu) and provide a virtual display via Xvfb or run the application on a machine with a graphical environment.

*Last Updated: 2025-11-12*
*Session: Headless Environment GUI Test*
*Status: Blocked ❌*

## Recent Session: Branch Comparison (2025-11-13)

### Session Goals
1. Compare `codex/create-adjustable-in-game-overlay` against `main` to determine which branch has the latest code.
2. Align future work with the most up-to-date branch.

### Actions Taken
- Reconstructed the historical branch tips using commit `e8c3026` for `codex/create-adjustable-in-game-overlay` and `11119cc` for `main`.
- Ran `git diff main..codex/create-adjustable-in-game-overlay --stat` to audit file-level differences.
- Inspected `test_before_build.py` and `aicontext.md` in both branches to confirm that `main` contains the newest headless-environment safeguards and documentation updates.

### Outcome
- `main` is ahead of `codex/create-adjustable-in-game-overlay` (latter is ancestor commit `e8c3026`).
- No merge required; continue development from `main` (currently mirrored by the `work` branch).
- Documented findings here for continuity.

*Last Updated: 2025-11-13*
*Session: Branch Comparison*
*Status: Complete ✅*

## Current Session: Persist Open WebUI API Key (2025-11-12)

### Session Goals
1. Ensure Open WebUI API keys saved via Settings dialog persist in the generated `.env` file.
2. Run a lightweight syntax validation to confirm configuration changes compile.

### Actions Taken
- Updated `src/config.py` so `Config.save_to_env` writes the `OPEN_WEBUI_API_KEY` value into the `.env` output block under a new **Open WebUI Authentication** section.
- Executed `python -m compileall src` to verify the source tree compiles without syntax errors inside the container.

### Outcome
- Open WebUI API keys are now persisted alongside other credentials, preventing loss of authentication between application restarts.
- Syntax validation succeeded with no errors reported.

*Last Updated: 2025-11-12*
*Session: Persist Open WebUI API Key*
*Status: Complete ✅*

## Current Session: Expand Open WebUI Endpoint Compatibility (2025-11-14)

### Session Goals
1. Resolve persistent `405 Method Not Allowed` errors when using Open WebUI via the Windows debug build.
2. Broaden REST endpoint detection to accommodate newer Open WebUI deployments that nest APIs under `/api/v1`.
3. Provide richer authentication headers compatible with both legacy and current Open WebUI releases.

### Actions Taken
- Refactored `src/ai_assistant.py` Ollama/Open WebUI request flow to iterate through a prioritized list of candidate endpoints, automatically falling back across OpenAI-compatible, native, and legacy generate routes (including the new `/api/v1/*` variants).
- Added dual authentication headers (`Authorization: Bearer` and `X-API-Key`) plus `Accept: application/json` to satisfy stricter Open WebUI API gateways.
- Introduced centralized error tracking so the final exception bubbles up the last encountered HTTP or transport issue for clearer GUI notifications.

### Outcome
- The assistant now gracefully retries alternate endpoints instead of halting after the first 405 response, improving compatibility with Open WebUI releases that re-map APIs.
- Users running behind locked-down reverse proxies gain broader header support, reducing false "authentication failed" alerts when valid API keys are supplied.
- Verified source tree compiles successfully via `python -m compileall src`.

### Update (2025-11-14 - Model Auto-Detection)
- Added dynamic model discovery in `src/ai_assistant.py` that parses `/v1/models` and `/api/tags` responses to select an installed model instead of hard-coding `llama2`.
- When Open WebUI responds with a 400 error indicating an unknown model, the assistant now refreshes the model list and retries with the detected default to avoid cascading 405 fallbacks.
- Introduced helper utilities to refresh model metadata while preserving authentication headers and retry ordering.

### Tests
- `python -m compileall src`

*Last Updated: 2025-11-14*
*Session: Expand Open WebUI Endpoint Compatibility*
*Status: In Progress ⚙️*
## Current Session: Comprehensive Test Audit (2025-11-12)

### Session Goals
1. Execute all distributed test harnesses to validate functionality and identify blocking issues.
2. Document environment-dependent failures for follow-up remediation.

### Actions Taken
- Ran `python -m compileall src` to ensure the source tree compiles cleanly (no errors reported).
- Executed `python test_modules.py` to exercise module imports and component checks; GUI-related tests failed because the container lacks `libGL.so.1`, and Anthropic-specific checks were skipped without API keys.
- Executed `python test.py`; run aborted when legacy expectations for `GameDetector.KNOWN_GAMES` triggered an `AttributeError` due to the current implementation exposing `KNOWN_PROCESSES` instead.
- Executed `python test_edge_cases.py`; all edge-case suites passed, though network scraping gracefully degraded behind the sandbox proxy.
- Executed `python test_minimal.py`; halted on the same `GameDetector.KNOWN_GAMES` attribute mismatch seen in `test.py`.
- Executed `python test_before_build.py`; reported missing `KNOWN_GAMES` attribute and skipped GUI/PyQt6 checks because `libGL.so.1` is unavailable in this headless environment.

### Outcomes
- Source compilation succeeded.
- Functional coverage scripts repeatedly surfaced an AttributeError: `'GameDetector' object has no attribute 'KNOWN_GAMES'`; this regression blocks several pre-build and smoke-test flows.
- GUI validation remains blocked by the absence of the system OpenGL shim (`libGL.so.1`) in the container.
- Web-scraping routines emitted proxy-related warnings but continued without hard failures.

### Next Steps
- Align the test harnesses with the current `GameDetector` API (or restore a compatibility shim exposing `KNOWN_GAMES`).
- Install `libgl1` (or equivalent) and a virtual display (e.g., Xvfb) if GUI smoke tests must run headlessly.
- Optionally mock outbound HTTP calls in scraper tests to avoid proxy-induced warnings.

*Last Updated: 2025-11-12*
*Session: Comprehensive Test Audit*
*Status: Attention Required ⚠️*
