# CLAUDE.md - AI Assistant Guide for Omnix Gaming Companion

**Last Updated:** 2025-11-18
**Codebase Version:** 1.2+
**Total LOC:** ~14,700

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Architecture Summary](#architecture-summary)
3. [Key Modules & Responsibilities](#key-modules--responsibilities)
4. [Technology Stack](#technology-stack)
5. [Development Workflows](#development-workflows)
6. [Code Conventions](#code-conventions)
7. [Testing Strategy](#testing-strategy)
8. [Common Tasks & Patterns](#common-tasks--patterns)
9. [Troubleshooting Guide](#troubleshooting-guide)
10. [Extension Points](#extension-points)

---

## Project Overview

### What is Omnix?

Omnix is a sophisticated desktop AI gaming companion that:
- **Automatically detects** what game you're playing via process monitoring
- **Provides AI-powered assistance** using OpenAI, Anthropic, or Google Gemini
- **Integrates game knowledge** from wikis, guides, and custom knowledge packs
- **Supports macros & automation** with keyboard/mouse input simulation
- **Tracks gaming sessions** with AI-powered coaching and insights
- **Offers a modern overlay** with customizable appearance and hotkeys

### Key Features

- 🎯 **Automatic Game Detection** - 15 pre-configured games with custom profile support
- 🤖 **Multi-Provider AI** - OpenAI, Anthropic, Google Gemini with easy switching
- 📚 **Knowledge System** - Per-game knowledge packs with semantic search (TF-IDF)
- ⌨️ **Macro System** - Record, create, and execute keyboard/mouse macros
- 🎨 **Design System** - Consistent UI with design tokens and reusable components
- 💾 **Secure Credentials** - Encrypted API key storage in system keyring
- 📊 **Session Coaching** - AI-powered gameplay insights and improvement tips
- 🪟 **Overlay Window** - Movable, resizable, minimizable with auto-save

### Project Structure

```
gaming-ai-assistant/
├── main.py                      # Application entry point
├── requirements.txt             # Python dependencies
├── .env.example                 # Configuration template
├── CLAUDE.md                    # This file - AI assistant guide
├── README.md                    # User-facing documentation
├── GamingAIAssistant.spec       # PyInstaller build spec
├── build_windows_exe.py         # Windows build automation
│
├── src/                         # Main source directory (~14,700 LOC)
│   ├── __init__.py
│   │
│   ├── Core Application
│   ├── config.py                # Configuration management
│   ├── credential_store.py      # Encrypted API key storage
│   │
│   ├── Game Detection
│   ├── game_detector.py         # Process monitoring & game detection
│   ├── game_watcher.py          # Background game monitoring thread
│   ├── game_profile.py          # Per-game configuration profiles
│   │
│   ├── AI Integration
│   ├── ai_assistant.py          # High-level AI interface
│   ├── ai_router.py             # Multi-provider routing
│   ├── providers.py             # Provider implementations (OpenAI, Anthropic, Gemini)
│   ├── provider_tester.py       # Connection testing
│   │
│   ├── Knowledge System
│   ├── knowledge_pack.py        # Knowledge pack data structures
│   ├── knowledge_store.py       # Knowledge persistence
│   ├── knowledge_index.py       # Semantic search with TF-IDF
│   ├── knowledge_integration.py # Knowledge augmentation for AI
│   ├── knowledge_ingestion.py   # Import content from files/URLs
│   │
│   ├── Macro & Automation
│   ├── macro_manager.py         # Macro definitions & management
│   ├── macro_store.py           # Macro persistence
│   ├── macro_runner.py          # Macro execution engine
│   ├── macro_ai_generator.py    # AI-assisted macro creation
│   ├── keybind_manager.py       # Global hotkey management
│   │
│   ├── Session Management
│   ├── session_logger.py        # Session event tracking
│   ├── session_coaching.py      # AI-powered coaching
│   ├── session_recap_dialog.py  # Session summary UI
│   │
│   ├── GUI Layer
│   ├── gui.py                   # Main application window (1,800 LOC)
│   ├── overlay_modes.py         # Compact/Full display modes
│   ├── settings_dialog.py       # Settings UI
│   ├── settings_tabs.py         # Advanced settings tabs
│   ├── providers_tab.py         # AI provider configuration
│   ├── game_profiles_tab.py     # Game profile management
│   ├── appearance_tabs.py       # Theme & appearance
│   ├── knowledge_packs_tab.py   # Knowledge pack UI
│   ├── setup_wizard.py          # First-run setup
│   ├── theme_manager.py         # Visual theming
│   │
│   └── ui/                      # UI Design System
│       ├── design_system.py     # Design system manager
│       ├── tokens.py            # Design tokens (colors, typography, spacing)
│       ├── components/          # Reusable UI components
│       │   ├── buttons.py
│       │   ├── inputs.py
│       │   ├── cards.py
│       │   ├── layouts.py
│       │   ├── navigation.py
│       │   ├── modals.py
│       │   ├── overlay.py
│       │   └── dashboard_button.py
│       └── __init__.py
│
└── test_*.py                    # Test files (10 files, ~500+ LOC)
```

### User Data Directory

```
~/.gaming_ai_assistant/
├── game_profiles.json           # User game profiles
├── macros.json                  # Macro index
├── keybinds.json                # Hotkey definitions
├── theme.json                   # Theme preferences
├── credentials.enc              # Encrypted API keys
├── macros/{macro_id}.json       # Individual macro files
├── knowledge_packs/{pack_id}.json  # Knowledge pack files
├── knowledge_sources/{source_id}.json  # Source files
└── sessions/{game_profile_id}/{date}.json  # Session logs
```

---

## Architecture Summary

### High-Level Design

Omnix follows a **layered architecture** with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────────┐
│                    Presentation Layer                        │
│  gui.py, ui/*, settings_*.py, *_dialog.py                   │
│  (PyQt6-based desktop application with design system)        │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                  Business Logic Layer                        │
│  ai_assistant.py, game_watcher.py, macro_runner.py,         │
│  session_coaching.py, knowledge_integration.py               │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│               Data/Integration Layer                         │
│  providers.py, ai_router.py, game_detector.py,              │
│  knowledge_index.py                                          │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                  Persistence Layer                           │
│  config.py, credential_store.py, *_store.py,                │
│  session_logger.py                                           │
└─────────────────────────────────────────────────────────────┘
```

### Core Data Flow

```
User Input (Game Launch / Question)
    ↓
Game Detection (game_detector.py) ←→ Game Watcher (game_watcher.py)
    ↓
Game Profile Lookup (game_profile.py)
    ↓
Knowledge Integration (knowledge_integration.py)
    ├── Knowledge Index (knowledge_index.py)
    └── Knowledge Packs (knowledge_pack.py)
    ↓
AI Assistant (ai_assistant.py)
    ↓
AI Router (ai_router.py) → Provider Selection
    ├── OpenAI Provider
    ├── Anthropic Provider
    └── Google Gemini Provider
    ↓
Session Logger (session_logger.py)
    ↓
GUI Display (gui.py) → User Response
```

### Key Design Patterns

| Pattern | Usage | Example |
|---------|-------|---------|
| **Provider/Strategy** | AI provider abstraction | `AIProvider` protocol with multiple implementations |
| **Observer (Qt Signals)** | Event-driven updates | `game_changed.connect(on_game_changed)` |
| **Singleton** | Global instances | `Config()`, `get_knowledge_index()` |
| **Factory** | Object creation | `create_provider(provider_name, api_key)` |
| **Repository** | Data persistence | `GameProfileStore`, `MacroStore`, `KnowledgePackStore` |
| **Command** | Macro steps | Each `MacroStep` is an executable command |
| **State Machine** | Macro execution | `MacroExecutionState` enum |
| **Thread** | Background operations | `AIWorkerThread`, `GameDetectionThread` |

---

## Key Modules & Responsibilities

### Core Application Layer

#### **main.py** (250 LOC)
**Purpose:** Application entry point and initialization orchestrator

**Key Responsibilities:**
- Logging setup with file and console output
- Sequential module initialization with error handling
- UTF-8 encoding for Windows console
- Graceful error reporting with user-friendly messages
- GUI lifecycle management

**Initialization Flow:**
1. Logging setup
2. Config loading
3. Credential store initialization
4. Game detector initialization
5. AI router initialization (if keys present)
6. Info scraper initialization
7. GUI startup

**Important:** Always initialize modules in this order to maintain dependencies.

#### **config.py** (350 LOC)
**Purpose:** Centralized configuration management

**Key Classes:**
```python
class Config:
    # AI Provider
    ai_provider: str  # "anthropic" | "openai" | "gemini"

    # API Keys (stored in credential_store, not here)
    openai_api_key: str
    anthropic_api_key: str
    gemini_api_key: str

    # Session Tokens (for embedded login)
    session_tokens: Dict[str, dict]

    # Application Settings
    overlay_hotkey: str  # Default: "ctrl+shift+g"
    check_interval: int  # Game detection interval (seconds)

    # Window Settings (auto-saved)
    overlay_x: int
    overlay_y: int
    overlay_width: int
    overlay_height: int
    overlay_minimized: bool
    overlay_opacity: float

    # Extended Settings (loaded from JSON)
    keybinds: Dict
    macros: Dict
    theme: Dict
```

**Configuration Sources:**
- `.env` file for basic settings
- `~/.gaming_ai_assistant/*.json` for extended settings
- System keyring for API keys (via `credential_store.py`)

**Important Methods:**
- `is_configured() -> bool` - Check if API keys are set
- `has_provider_key() -> bool` - Check if current provider has key
- `save()` - Persist configuration to .env
- `load_extended_settings()` - Load JSON configuration files

#### **credential_store.py** (250 LOC)
**Purpose:** Secure API key storage using system keyring

**Security Features:**
- AES-256 encryption (Fernet from cryptography library)
- Platform-specific keyring integration
- Automatic fallback to encrypted file storage

**Platform Support:**
- **Windows:** Windows Credential Manager (via pywin32)
- **macOS:** Keychain
- **Linux:** SecretService / keyring with encrypted file fallback

**Key Methods:**
```python
class CredentialStore:
    def set_credential(service: str, key: str, value: str)
    def get_credential(service: str, key: str) -> Optional[str]
    def delete_credential(service: str, key: str)
```

**Usage:**
```python
store = CredentialStore()
store.set_credential("omnix.ai", "openai_api_key", "sk-...")
api_key = store.get_credential("omnix.ai", "openai_api_key")
```

### Game Detection Layer

#### **game_detector.py** (300 LOC)
**Purpose:** Detect running games via process monitoring

**Key Features:**
- Process monitoring using `psutil` library
- 50+ pre-configured game mappings
- Executable name normalization (case-insensitive)
- Legacy game mapping support

**Data Structure:**
```python
common_games = {
    "League of Legends": ["LeagueClient.exe", "League of Legends.exe"],
    "Elden Ring": ["eldenring.exe"],
    "Cyberpunk 2077": ["Cyberpunk2077.exe"],
    # ... more games (15 built-in profiles total)
}
```

**Key Methods:**
```python
class GameDetector:
    def detect_running_game() -> Optional[Dict]
    # Returns: {"name": str, "process": psutil.Process, "pid": int, "timestamp": datetime}

    def is_game_running(game_name: str) -> bool
    def get_game_process(game_name: str) -> Optional[psutil.Process]
```

**Adding New Games:**
```python
# In game_detector.py, add to common_games dict:
"Your Game Name": ["yourgame.exe", "alternate.exe"]
```

#### **game_watcher.py** (250 LOC)
**Purpose:** Background thread for continuous game monitoring

**Qt Signals:**
```python
class GameWatcher(QThread):
    game_changed = pyqtSignal(str, object)  # game_name, profile
    game_detected = pyqtSignal(str)         # game_name
    game_closed = pyqtSignal()              # No args
```

**Usage:**
```python
watcher = GameWatcher(game_detector, profile_store, check_interval=5)
watcher.game_detected.connect(on_game_detected)
watcher.start()
```

#### **game_profile.py** (350 LOC)
**Purpose:** Per-game configuration profiles

**Data Structure:**
```python
@dataclass
class GameProfile:
    id: str                           # Unique identifier (slug)
    display_name: str                 # Human-readable name
    exe_names: List[str]              # Executable names to match
    system_prompt: str                # AI behavior customization
    default_provider: str             # "anthropic" | "openai" | "gemini"
    default_model: Optional[str]      # Model override (e.g., "gpt-4")
    overlay_mode_default: str         # "compact" | "full"
    extra_settings: Dict              # Extensible settings
    is_builtin: bool                  # Built-in vs user-created
```

**Built-in Profiles:** 15 games with optimized system prompts

**Creating Custom Profiles:**
```python
profile = GameProfile(
    id="my-game",
    display_name="My Game",
    exe_names=["mygame.exe"],
    system_prompt="You are an expert at My Game...",
    default_provider="anthropic",
    is_builtin=False
)
profile_store.save_profile(profile)
```

### AI Integration Layer

#### **ai_router.py** (300 LOC)
**Purpose:** Central routing for AI requests across providers

**Key Responsibilities:**
- Provider initialization and lifecycle
- Default provider selection
- Fallback provider logic
- Error handling and retry

**Key Methods:**
```python
class AIRouter:
    def get_default_provider() -> Optional[AIProvider]
    def get_provider(provider_name: str) -> Optional[AIProvider]
    def route_request(messages, model=None, **kwargs) -> Dict
```

#### **providers.py** (550 LOC)
**Purpose:** Multi-provider AI implementations

**Provider Protocol:**
```python
class AIProvider(Protocol):
    name: str

    def is_configured() -> bool
    def test_connection() -> ProviderHealth
    async def chat(messages: List[Dict], model: str = None, **kwargs) -> Dict[str, Any]
```

**Implementations:**
- `OpenAIProvider` - GPT-4, GPT-3.5 with streaming support
- `AnthropicProvider` - Claude 3 Opus, Sonnet with extended context
- `GoogleGeminiProvider` - Gemini Pro, Gemini Pro Vision

**Error Classification:**
```python
class ProviderError(Exception): pass
class ProviderAuthError(ProviderError): pass
class ProviderQuotaError(ProviderError): pass
class ProviderRateLimitError(ProviderError): pass
class ProviderConnectionError(ProviderError): pass
```

**Adding a New Provider:**
1. Create provider class in `providers.py`
2. Implement `AIProvider` protocol
3. Add to `ai_router.py` provider registry
4. Add UI configuration in `providers_tab.py`

#### **ai_assistant.py** (400 LOC)
**Purpose:** High-level AI interaction interface

**Key Features:**
- Conversation context management (max 20 messages)
- Game context integration
- Knowledge pack retrieval
- Error formatting

**Key Methods:**
```python
class AIAssistant:
    MAX_CONVERSATION_MESSAGES = 20

    def ask_question(question: str, game_context: Optional[Dict] = None) -> str
    def update_current_game(game: Dict, profile: GameProfile)
    def update_conversation_history(role: str, content: str)
    def clear_conversation()
    def get_conversation_history() -> List[Dict]
```

**Message Format:**
```python
messages = [
    {"role": "system", "content": "You are a gaming assistant..."},
    {"role": "user", "content": "How do I beat this boss?"},
    {"role": "assistant", "content": "To defeat the boss..."}
]
```

### Knowledge System

#### **knowledge_pack.py** (200 LOC)
**Purpose:** Knowledge pack data structures

**Core Classes:**
```python
@dataclass
class KnowledgeSource:
    id: str
    type: str              # "file" | "url" | "note"
    title: str
    path: Optional[str]    # For files
    url: Optional[str]     # For URLs
    tags: List[str]
    content: Optional[str] # For notes or cached content

@dataclass
class KnowledgePack:
    id: str
    name: str
    description: str
    game_profile_id: str
    sources: List[KnowledgeSource]
    enabled: bool
    created_at: datetime
    updated_at: datetime
```

**Source Types:**
- **file:** PDF, DOCX, TXT, Markdown documents
- **url:** Web pages, wikis, guides
- **note:** User-written tips and notes

#### **knowledge_index.py** (450 LOC)
**Purpose:** Semantic search with TF-IDF embeddings

**Key Features:**
- Local TF-IDF embedding generation (no external API)
- Chunk-based indexing
- Similarity search with scoring

**Key Classes:**
```python
@dataclass
class RetrievedChunk:
    source_id: str
    content: str
    score: float
    metadata: Dict

class SimpleTFIDFEmbedding(EmbeddingProvider):
    def generate_embedding(text: str) -> List[float]
    def fit(documents: List[str])
    def search(query: str, top_k: int = 5) -> List[RetrievedChunk]

class KnowledgeIndex:
    def index_pack(pack: KnowledgePack)
    def search(query: str, game_profile_id: str, top_k: int = 5) -> List[RetrievedChunk]
    def clear_index(game_profile_id: str)
```

**Usage:**
```python
index = get_knowledge_index()
index.index_pack(knowledge_pack)
chunks = index.search("how to beat boss", game_profile_id="elden-ring", top_k=5)
```

#### **knowledge_integration.py** (250 LOC)
**Purpose:** Integrate knowledge into AI conversations

**Key Methods:**
```python
class KnowledgeIntegration:
    def should_use_knowledge_packs(game_profile_id: str, extra_settings: Dict) -> bool
    def get_knowledge_context(game_profile_id: str, question: str, extra_settings: Dict) -> Optional[str]
    def format_knowledge_context(chunks: List[RetrievedChunk]) -> str
```

**Knowledge Augmentation Flow:**
1. Check if knowledge packs are enabled for game
2. Retrieve relevant chunks via semantic search
3. Format chunks into context string
4. Prepend to AI conversation

#### **knowledge_ingestion.py** (350 LOC)
**Purpose:** Import content from external sources

**Supported Formats:**
- PDF documents
- DOCX files
- TXT/Markdown files
- Web pages (via BeautifulSoup)

**Key Methods:**
```python
def ingest_file(file_path: str) -> str
def ingest_url(url: str) -> str
def chunk_text(text: str, chunk_size: int = 500) -> List[str]
```

### Macro & Automation System

#### **macro_manager.py** (600 LOC)
**Purpose:** Macro definition and management

**Macro Step Types:**
```python
class MacroStepType(Enum):
    KEY_PRESS = "key_press"        # Press and release
    KEY_DOWN = "key_down"          # Hold key
    KEY_UP = "key_up"              # Release key
    KEY_SEQUENCE = "key_sequence"  # Type string
    MOUSE_MOVE = "mouse_move"      # Move cursor
    MOUSE_CLICK = "mouse_click"    # Click button
    MOUSE_SCROLL = "mouse_scroll"  # Scroll wheel
    DELAY = "delay"                # Wait
```

**Data Structures:**
```python
@dataclass
class MacroStep:
    type: str
    key: Optional[str]         # For keyboard actions
    duration_ms: int           # For delays
    button: Optional[str]      # "left" | "right" | "middle"
    x: Optional[int]           # Mouse X coordinate
    y: Optional[int]           # Mouse Y coordinate
    scroll_amount: int         # For scroll actions
    delay_jitter_ms: int       # Random variation

@dataclass
class Macro:
    id: str
    name: str
    description: str
    game_profile_id: Optional[str]  # None = global
    steps: List[MacroStep]
    enabled: bool
    created_at: datetime
    max_repeat: int = 10       # Safety limit
    execution_timeout: int = 30 # Safety limit (seconds)
```

**Creating Macros:**
```python
macro = Macro(
    id="quick-heal",
    name="Quick Heal",
    description="Press H for health potion",
    game_profile_id="elden-ring",
    steps=[
        MacroStep(type="KEY_PRESS", key="h", duration_ms=0),
        MacroStep(type="DELAY", duration_ms=100)
    ],
    enabled=True
)
macro_store.save_macro(macro)
```

#### **macro_runner.py** (450 LOC)
**Purpose:** Execute macros with safety limits

**Key Features:**
- Keyboard/mouse simulation via `pynput`
- Execution state tracking
- Safety limits (max repeat, timeout)
- Manual stop capability

**Execution States:**
```python
class MacroExecutionState(Enum):
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    ERRORED = "errored"
```

**Key Methods:**
```python
class MacroRunner:
    def execute_macro(macro: Macro) -> MacroExecutionResult
    def is_running() -> bool
    def stop_macro()
    def get_state() -> MacroExecutionState
```

**Safety Features:**
- Max repeat protection prevents infinite loops
- Execution timeout prevents hung macros
- Manual stop capability
- Detailed error reporting

#### **keybind_manager.py** (550 LOC)
**Purpose:** Global hotkey management

**Key Features:**
- Global hotkey listening via `pynput`
- Game-specific keybind scoping
- Conflict detection
- Action-based triggers

**Keybind Actions:**
```python
class KeybindAction(Enum):
    TOGGLE_OVERLAY = "toggle_overlay"
    START_RECORDING = "start_recording"
    RUN_MACRO = "run_macro"
    STOP_MACRO = "stop_macro"
    SHOW_TIPS = "show_tips"
    CLEAR_CHAT = "clear_chat"
```

**Data Structures:**
```python
@dataclass
class Keybind:
    action: str
    keys: str              # e.g., "ctrl+shift+g"
    description: str
    enabled: bool
    system_wide: bool

@dataclass
class MacroKeybind:
    macro_id: str
    keys: str
    description: str
    game_profile_id: Optional[str]
    enabled: bool
    system_wide: bool
```

### Session Management

#### **session_logger.py** (350 LOC)
**Purpose:** Track user interactions and AI responses

**Event Types:**
- `question` - User asked a question
- `answer` - AI provided response
- `macro` - Macro executed
- `knowledge_query` - Knowledge pack searched
- `game_detected` - Game launched
- `game_closed` - Game exited

**Data Structure:**
```python
@dataclass
class SessionEvent:
    timestamp: datetime
    event_type: str
    game_profile_id: str
    content: str
    meta: Dict  # Additional metadata
```

**Key Methods:**
```python
class SessionLogger:
    MAX_EVENTS_IN_MEMORY = 100
    MAX_EVENTS_ON_DISK = 500
    SESSION_TIMEOUT = timedelta(hours=2)

    def log_event(event_type: str, game_profile_id: str, content: str, meta: Dict = None)
    def get_session_events(game_profile_id: str) -> List[SessionEvent]
    def get_all_sessions() -> Dict[str, List[SessionEvent]]
    def clear_session(game_profile_id: str)
```

#### **session_coaching.py** (300 LOC)
**Purpose:** AI-powered gameplay insights

**Key Features:**
- Session recap generation using AI
- Pattern identification
- Personalized coaching tips
- Performance insights

**Key Methods:**
```python
class SessionCoach:
    def generate_recap(game_profile_id: str, session_events: List[SessionEvent]) -> str
    def generate_insights(game_profile_id: str) -> Dict
    def get_coaching_tips(game_profile_id: str) -> List[str]
```

### GUI Layer

#### **gui.py** (1,800 LOC)
**Purpose:** Main application window and UI orchestration

**Key Components:**
```python
class AIWorkerThread(QThread):
    """Background thread for AI queries (prevents GUI freezing)"""
    response_ready = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

class GameDetectionThread(QThread):
    """Background game monitoring"""
    game_detected = pyqtSignal(dict)
    game_lost = pyqtSignal()

class OmnixMainWindow(QMainWindow):
    """Main application window"""
    # Features:
    # - Chat interface
    # - Game detection status
    # - Settings access
    # - Overlay controls
    # - System tray integration
```

**Important UI Patterns:**
- **Always use worker threads** for long-running operations (AI calls, game detection)
- **Never block the main GUI thread** - use signals/slots for communication
- **Auto-save window geometry** on close

#### **overlay_modes.py** (200 LOC)
**Purpose:** Display mode configurations

**Modes:**
```python
class OverlayMode(Enum):
    COMPACT = "compact"  # Single-line input with preview
    FULL = "full"        # Complete chat interface

MODES = {
    "compact": {
        "min_width": 300,
        "default_width": 500,
        "default_height": 120,
        "show_conversation_history": False,
        "input_rows": 1
    },
    "full": {
        "min_width": 400,
        "default_width": 900,
        "default_height": 700,
        "show_conversation_history": True,
        "input_rows": 3
    }
}
```

#### **settings_dialog.py** & **settings_tabs.py** (1,500 LOC total)
**Purpose:** Comprehensive settings UI

**Tabs:**
- **General:** Basic application settings
- **AI Providers:** Provider selection and API keys
- **Game Profiles:** Game-specific configurations
- **Knowledge Packs:** Knowledge management
- **Macros:** Macro creation and editing
- **Keybinds:** Hotkey configuration
- **Appearance:** Themes and visual customization
- **Advanced:** Debug options and expert settings

### UI Design System

#### **ui/design_system.py** (500 LOC)
**Purpose:** Centralized styling and design tokens

**Key Features:**
- Design token system (colors, typography, spacing)
- QSS stylesheet generation
- Component styling utilities
- Theme management

**Usage:**
```python
from ui.design_system import design_system

# Apply design system to app
app.setStyleSheet(design_system.generate_base_stylesheet())

# Get component style
button_style = design_system.get_component_style("button")
```

#### **ui/tokens.py** (200 LOC)
**Purpose:** Design tokens definition

**Color Palette:**
```python
COLORS = {
    "primary_bg": "#1A1A2E",      # Deep charcoal
    "secondary_bg": "#2C2C4A",    # Dark muted blue
    "accent_primary": "#00BFFF",  # Electric blue
    "accent_secondary": "#39FF14", # Neon green
    "text_primary": "#FFFFFF",
    "text_secondary": "#B0B0C8",
    "success": "#39FF14",
    "warning": "#FFB800",
    "error": "#FF3B3B",
    "info": "#00BFFF"
}
```

**Typography:**
```python
TYPOGRAPHY = {
    "font_family": "'Segoe UI', 'Roboto', sans-serif",
    "font_size_xs": "10px",
    "font_size_sm": "12px",
    "font_size_base": "14px",
    "font_size_lg": "16px",
    "font_size_xl": "20px",
    "font_weight_normal": "400",
    "font_weight_medium": "500",
    "font_weight_bold": "700"
}
```

**Spacing:**
```python
SPACING = {
    "xs": "4px",
    "sm": "8px",
    "md": "16px",
    "lg": "24px",
    "xl": "32px"
}
```

#### **ui/components/** (1,500 LOC)
**Purpose:** Reusable UI components

**Component Library:**
```python
# Buttons
from ui.components.buttons import OmnixButton, OmnixIconButton

# Inputs
from ui.components.inputs import OmnixLineEdit, OmnixTextEdit, OmnixComboBox

# Cards
from ui.components.cards import OmnixCard, OmnixPanel, OmnixInfoCard

# Layouts
from ui.components.layouts import OmnixVBox, OmnixHBox, OmnixGrid, OmnixFormLayout

# Navigation
from ui.components.navigation import OmnixSidebar, OmnixHeaderBar

# Modals
from ui.components.modals import OmnixDialog, OmnixConfirmDialog, OmnixMessageDialog

# Overlay
from ui.components.overlay import OmnixOverlayWidget

# Dashboard
from ui.components.dashboard_button import OmnixDashboardButton
```

**Component Design Principles:**
- All components use design tokens
- Consistent API across components
- Built-in accessibility features
- Extensible through inheritance

---

## Technology Stack

### Core Technologies

| Category | Technology | Version | Purpose |
|----------|-----------|---------|---------|
| **Language** | Python | 3.8+ | Core language |
| **GUI Framework** | PyQt6 | 6.6.0+ | Desktop application |

### AI Integration

| Provider | Library | Version | Models |
|----------|---------|---------|--------|
| **OpenAI** | openai | 1.3.0+ | GPT-4, GPT-3.5-turbo |
| **Anthropic** | anthropic | 0.7.0+ | Claude 3 Opus, Sonnet, Haiku |
| **Google** | google-generativeai | 0.3.0+ | Gemini Pro, Gemini Pro Vision |

### System Integration

| Feature | Library | Version | Purpose |
|---------|---------|---------|---------|
| **Process Monitoring** | psutil | 5.9.0+ | Game detection |
| **Web Scraping** | requests | 2.31.0+ | HTTP requests |
| | beautifulsoup4 | 4.12.0+ | HTML parsing |
| | lxml | 4.9.0+ | XML/HTML processing |
| **Input Simulation** | pynput | 1.7.6+ | Keyboard/mouse control |
| **Encryption** | cryptography | 41.0.0+ | API key security |
| **Keyring** | keyring | 24.2.0+ | System credential storage |
| **Configuration** | python-dotenv | 1.0.0+ | .env file loading |
| **Windows APIs** | pywin32 | 306+ | Windows-specific features |

### Development Tools

| Tool | Purpose |
|------|---------|
| **PyInstaller** | Windows executable building |
| **pytest** | Unit testing |
| **logging** | Application logging |

### Platform Support

- ✅ **Windows** 10/11 (Primary)
- ✅ **macOS** (Supported)
- ✅ **Linux** (Supported)

---

## Development Workflows

### Setting Up Development Environment

```bash
# Clone repository
git clone https://github.com/yourusername/Omnix-All-knowing-gaming-companion.git
cd Omnix-All-knowing-gaming-companion

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Edit .env and add API keys (or use Setup Wizard on first run)
# ANTHROPIC_API_KEY=sk-ant-...
# AI_PROVIDER=anthropic
```

### Running the Application

```bash
# Run from source
python main.py

# The Setup Wizard will guide first-time setup:
# 1. Select AI provider
# 2. Enter API key
# 3. Test connection
# 4. Save configuration
```

### Running Tests

```bash
# Run all tests
python -m pytest

# Run specific test file
python test_modules.py
python test_macro_system.py
python test_knowledge_system.py

# Run with verbose output
python -m pytest -v

# Test before building executable
python test_before_build.py
```

### Building Windows Executable

```bash
# Automated build
python build_windows_exe.py

# Manual build with PyInstaller
pyinstaller GamingAIAssistant.spec

# Debug build (shows console)
pyinstaller GamingAIAssistant_DEBUG.spec
```

**Build Output:**
```
dist/GamingAIAssistant/
├── GamingAIAssistant.exe
├── .env.example
├── README.md
├── SETUP.md
└── _internal/  (all dependencies)
```

### Git Workflow

```bash
# Create feature branch (must start with 'claude/' for this session)
git checkout -b claude/feature-name

# Make changes and commit
git add .
git commit -m "Add feature: description"

# Push to remote
git push -u origin claude/feature-name

# Create pull request (via GitHub UI or gh CLI)
gh pr create --title "Feature: description" --body "Details..."
```

**Important:** For this session, always use branch: `claude/claude-md-mi0udx5q25azj8gs-014ci8Xyu9DvRRXC76VYQcE5`

---

## Code Conventions

### Python Style

- **PEP 8** compliance for all code
- **Type hints** for function signatures
- **Docstrings** for public methods (Google style)
- **4 spaces** for indentation (no tabs)

**Example:**
```python
def detect_running_game(self, timeout: int = 5) -> Optional[Dict[str, Any]]:
    """
    Detect currently running game from process list.

    Args:
        timeout: Maximum time to wait for detection (seconds)

    Returns:
        Dictionary with game info if detected, None otherwise

    Raises:
        ProcessLookupError: If process monitoring fails
    """
    # Implementation...
```

### Naming Conventions

| Type | Convention | Example |
|------|-----------|---------|
| **Classes** | PascalCase | `GameDetector`, `AIAssistant` |
| **Functions/Methods** | snake_case | `detect_running_game()`, `ask_question()` |
| **Constants** | UPPER_SNAKE_CASE | `MAX_CONVERSATION_MESSAGES`, `SESSION_TIMEOUT` |
| **Private Methods** | _leading_underscore | `_normalize_process_name()` |
| **Modules** | snake_case | `game_detector.py`, `ai_assistant.py` |

### File Organization

**Module Structure:**
```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module docstring explaining purpose
"""

# Standard library imports
import sys
import os
from typing import Optional, Dict, List

# Third-party imports
import psutil
from PyQt6.QtCore import QThread, pyqtSignal

# Local imports
from config import Config
from game_profile import GameProfile

# Constants
MAX_RETRIES = 3
DEFAULT_TIMEOUT = 5

# Classes
class MyClass:
    pass

# Functions
def my_function():
    pass
```

### Qt Signal/Slot Patterns

**Define signals in class:**
```python
class GameWatcher(QThread):
    game_detected = pyqtSignal(str)  # game_name
    game_changed = pyqtSignal(str, object)  # game_name, profile

    def run(self):
        # Emit signals
        self.game_detected.emit("Elden Ring")
```

**Connect signals:**
```python
watcher = GameWatcher()
watcher.game_detected.connect(self.on_game_detected)
watcher.start()
```

**Always use worker threads for long operations:**
```python
# BAD: Blocks GUI
response = ai_assistant.ask_question(question)

# GOOD: Non-blocking
worker = AIWorkerThread(ai_assistant, question)
worker.response_ready.connect(self.display_response)
worker.start()
```

### Error Handling

**Use specific exceptions:**
```python
try:
    provider.chat(messages)
except ProviderAuthError:
    show_error("Invalid API key")
except ProviderQuotaError:
    show_error("API quota exceeded")
except ProviderRateLimitError:
    show_warning("Rate limited, please wait")
except ProviderError as e:
    show_error(f"Provider error: {e}")
```

**Log errors with context:**
```python
import logging
logger = logging.getLogger(__name__)

try:
    result = risky_operation()
except Exception as e:
    logger.error(f"Operation failed: {e}", exc_info=True)
    raise
```

### Configuration Management

**Always use Config class:**
```python
# GOOD
from config import Config
config = Config()
api_key = config.anthropic_api_key

# BAD
import os
api_key = os.getenv("ANTHROPIC_API_KEY")
```

**Save configuration changes:**
```python
config.overlay_width = 900
config.overlay_height = 700
config.save()  # Persist to .env
```

### UI Component Usage

**Use design system components:**
```python
# GOOD
from ui.components.buttons import OmnixButton
button = OmnixButton("Click Me", variant="primary")

# BAD
from PyQt6.QtWidgets import QPushButton
button = QPushButton("Click Me")
button.setStyleSheet("background-color: blue;")  # Hardcoded styles
```

**Apply design tokens:**
```python
from ui.design_system import design_system
from ui.tokens import COLORS, SPACING

# Use tokens instead of hardcoded values
label.setStyleSheet(f"color: {COLORS['text_primary']}; padding: {SPACING['md']};")
```

---

## Testing Strategy

### Test File Organization

```
test_modules.py           # Module import tests
test_macro_system.py      # Macro functionality
test_knowledge_system.py  # Knowledge pack operations
test_game_profiles.py     # Game profile management
test_edge_cases.py        # Error handling
test_before_build.py      # Pre-build validation
test_minimal.py           # Quick smoke test
test_gui_minimal.py       # Minimal GUI test (PyQt6 environment)
test_gui.sh               # Full GUI test with virtual display
live_test.py              # Live API testing (requires API keys)
api_key_test.py           # Provider credentials testing
ui/test_design_system.py  # UI design system
```

### Testing Levels

#### Unit Tests
**Focus:** Individual components in isolation

```python
def test_game_detector_initialization():
    detector = GameDetector()
    assert len(detector.common_games) > 0

def test_config_loading():
    config = Config(require_keys=False)
    assert config.ai_provider in ["openai", "anthropic", "gemini"]
```

#### Integration Tests
**Focus:** Component interactions

```python
def test_game_detection_with_profile_matching():
    detector = GameDetector()
    profile_store = GameProfileStore()

    # Simulate game detection
    game = detector.detect_running_game()
    if game:
        profile = profile_store.get_profile_for_game(game['name'])
        assert profile is not None
```

#### System Tests
**Focus:** End-to-end workflows

```python
def test_full_qa_workflow():
    # Setup
    config = Config()
    ai_assistant = AIAssistant(provider=config.ai_provider, config=config)

    # Detect game
    game_detector = GameDetector()
    game = game_detector.detect_running_game()

    # Ask question
    response = ai_assistant.ask_question("How do I play?", game_context=game)

    # Verify
    assert response is not None
    assert len(response) > 0
```

### Running Tests

```bash
# Run all tests
python -m pytest

# Run specific test file
python test_macro_system.py

# Run with coverage
python -m pytest --cov=src

# Run only tests matching pattern
python -m pytest -k "test_game"

# Verbose output
python -m pytest -v
```

### Test Best Practices

1. **Mock external dependencies** (API calls, file I/O)
2. **Test edge cases** (empty inputs, None values, errors)
3. **Verify error handling** (exception types, error messages)
4. **Test thread safety** for Qt components
5. **Clean up resources** after tests (temp files, threads)

### GUI Testing (Headless Environment)

**Overview:** The application can be tested in headless/CLI environments using Qt's offscreen platform or Xvfb (X Virtual Framebuffer).

**Quick Start:**
```bash
# Method 1: Offscreen Platform (Recommended)
export QT_QPA_PLATFORM=offscreen
python main.py

# Method 2: Virtual Display (Xvfb)
Xvfb :99 -screen 0 1920x1080x24 &
export DISPLAY=:99
python main.py
```

**Test Files:**
- `test_gui_minimal.py` - Minimal PyQt6 test (verifies GUI environment)
- `test_gui.sh` - Full application test with virtual display
- `GUI_TESTING.md` - Comprehensive GUI testing documentation

**Environment Setup:**
```bash
# Install Qt dependencies (already done in this environment)
apt-get install -y libegl1 libegl-mesa0 libxcb-cursor0 libxkbcommon-x11-0

# Install Python dependencies
pip install -r requirements.txt

# Test minimal GUI
export QT_QPA_PLATFORM=offscreen
python test_gui_minimal.py
```

**Available Qt Platforms:**
- `offscreen` - Memory-only rendering (fastest, recommended for CI/CD)
- `xcb` - X11 display (requires Xvfb or X server)
- `minimal` - Minimal platform plugin
- `vnc` - VNC remote display
- `wayland` - Wayland compositor

**Common Issues:**

1. **Missing EGL libraries**
   ```bash
   # Error: libEGL.so.1: cannot open shared object file
   apt-get install -y libegl1 libegl-mesa0
   ```

2. **Qt platform plugin errors**
   ```bash
   # Use offscreen platform
   export QT_QPA_PLATFORM=offscreen
   ```

3. **Application hangs**
   ```python
   # Add timeout for automated testing
   QTimer.singleShot(5000, app.quit)
   ```

**CI/CD Integration:**
```yaml
# GitHub Actions example
- name: Test GUI
  env:
    QT_QPA_PLATFORM: offscreen
  run: python test_gui_minimal.py
```

**See:** `GUI_TESTING.md` for comprehensive documentation.

---

## Common Tasks & Patterns

### Adding a New Game

**1. Add to game detector:**
```python
# src/game_detector.py
common_games = {
    "Your Game Name": ["yourgame.exe", "alternate.exe"],
    # ... existing games
}
```

**2. Create game profile:**
```python
# Via UI or programmatically
profile = GameProfile(
    id="your-game",
    display_name="Your Game Name",
    exe_names=["yourgame.exe"],
    system_prompt="You are an expert at Your Game. Provide tips and strategies.",
    default_provider="anthropic",
    default_model=None,
    overlay_mode_default="full",
    is_builtin=False
)
profile_store.save_profile(profile)
```

### Adding a New AI Provider

**1. Implement provider class:**
```python
# src/providers.py
class NewProvider:
    name = "newprovider"

    def __init__(self, api_key: str, session_tokens: Dict = None):
        self.api_key = api_key
        self.client = NewProviderClient(api_key=api_key)

    def is_configured(self) -> bool:
        return bool(self.api_key)

    def test_connection(self) -> ProviderHealth:
        try:
            # Test API connection
            self.client.test()
            return ProviderHealth(healthy=True, message="Connected")
        except Exception as e:
            return ProviderHealth(healthy=False, message=str(e))

    async def chat(self, messages: List[Dict], model: str = None, **kwargs) -> Dict:
        response = await self.client.chat.completions.create(
            model=model or "default-model",
            messages=messages
        )
        return {
            "content": response.choices[0].message.content,
            "model": response.model,
            "usage": response.usage
        }
```

**2. Register in AI router:**
```python
# src/ai_router.py
def get_provider(self, provider_name: str) -> Optional[AIProvider]:
    if provider_name == "newprovider":
        api_key = self.config.newprovider_api_key
        return NewProvider(api_key=api_key)
    # ... existing providers
```

**3. Add configuration:**
```python
# src/config.py
class Config:
    def __init__(self):
        # ...
        self.newprovider_api_key = os.getenv("NEWPROVIDER_API_KEY", "")
```

**4. Add UI support:**
```python
# src/providers_tab.py
# Add provider option to dropdown
# Add API key input field
# Add connection test button
```

### Creating a Knowledge Pack

**1. Define knowledge pack:**
```python
from knowledge_pack import KnowledgePack, KnowledgeSource
from datetime import datetime

pack = KnowledgePack(
    id="elden-ring-bosses",
    name="Elden Ring Boss Guide",
    description="Comprehensive guide for all bosses",
    game_profile_id="elden-ring",
    sources=[],
    enabled=True,
    created_at=datetime.now(),
    updated_at=datetime.now()
)
```

**2. Add sources:**
```python
# File source
file_source = KnowledgeSource(
    id="boss-guide-pdf",
    type="file",
    title="Boss Strategy Guide",
    path="/path/to/guide.pdf",
    tags=["bosses", "strategy"]
)

# URL source
url_source = KnowledgeSource(
    id="wiki-bosses",
    type="url",
    title="Elden Ring Wiki - Bosses",
    url="https://eldenring.wiki.fextralife.com/Bosses",
    tags=["bosses", "wiki"]
)

# Note source
note_source = KnowledgeSource(
    id="personal-tips",
    type="note",
    title="My Boss Tips",
    content="Margit: Stay close, dodge to the left...",
    tags=["bosses", "tips"]
)

pack.sources = [file_source, url_source, note_source]
```

**3. Save and index:**
```python
from knowledge_store import get_knowledge_store
from knowledge_index import get_knowledge_index

store = get_knowledge_store()
store.save_pack(pack)

index = get_knowledge_index()
index.index_pack(pack)
```

**4. Query knowledge:**
```python
chunks = index.search(
    query="How do I beat Margit?",
    game_profile_id="elden-ring",
    top_k=5
)

for chunk in chunks:
    print(f"Score: {chunk.score:.2f}")
    print(f"Content: {chunk.content}\n")
```

### Creating a Macro

**1. Define macro:**
```python
from macro_manager import Macro, MacroStep

macro = Macro(
    id="quick-heal",
    name="Quick Heal",
    description="Press H for health potion",
    game_profile_id="elden-ring",
    steps=[
        MacroStep(
            type="KEY_PRESS",
            key="h",
            duration_ms=0
        ),
        MacroStep(
            type="DELAY",
            duration_ms=100
        )
    ],
    enabled=True,
    max_repeat=10,
    execution_timeout=30
)
```

**2. Save macro:**
```python
from macro_store import get_macro_store

store = get_macro_store()
store.save_macro(macro)
```

**3. Execute macro:**
```python
from macro_runner import MacroRunner

runner = MacroRunner()
result = runner.execute_macro(macro)

if result.success:
    print("Macro executed successfully")
else:
    print(f"Macro failed: {result.error}")
```

**4. Bind to hotkey:**
```python
from keybind_manager import MacroKeybind, get_keybind_manager

keybind = MacroKeybind(
    macro_id="quick-heal",
    keys="ctrl+h",
    description="Quick heal hotkey",
    game_profile_id="elden-ring",
    enabled=True,
    system_wide=False
)

manager = get_keybind_manager()
manager.register_macro_keybind(keybind)
```

### Adding a UI Component

**1. Create component file:**
```python
# src/ui/components/my_component.py
from PyQt6.QtWidgets import QWidget, QLabel
from ui.tokens import COLORS, SPACING, TYPOGRAPHY

class OmnixMyComponent(QWidget):
    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.title = title
        self._init_ui()

    def _init_ui(self):
        # Use design tokens
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {COLORS['secondary_bg']};
                border-radius: 8px;
                padding: {SPACING['md']};
            }}
        """)

        label = QLabel(self.title)
        label.setStyleSheet(f"""
            QLabel {{
                color: {COLORS['text_primary']};
                font-size: {TYPOGRAPHY['font_size_lg']};
                font-weight: {TYPOGRAPHY['font_weight_bold']};
            }}
        """)
```

**2. Export component:**
```python
# src/ui/components/__init__.py
from .my_component import OmnixMyComponent

__all__ = ['OmnixMyComponent']
```

**3. Use component:**
```python
from ui.components import OmnixMyComponent

widget = OmnixMyComponent("My Title")
layout.addWidget(widget)
```

### Customizing Game Behavior

**1. Edit game profile system prompt:**
```python
profile = profile_store.get_profile("elden-ring")
profile.system_prompt = """
You are an expert Elden Ring guide specializing in boss strategies.
Always provide:
1. Boss weaknesses and resistances
2. Recommended equipment and stats
3. Phase-specific tips
4. Common mistakes to avoid
"""
profile_store.save_profile(profile)
```

**2. Set preferred AI provider:**
```python
profile.default_provider = "anthropic"  # or "openai", "gemini"
profile.default_model = "claude-3-5-sonnet-20241022"  # Specific model
profile_store.save_profile(profile)
```

**3. Configure overlay mode:**
```python
profile.overlay_mode_default = "compact"  # or "full"
profile_store.save_profile(profile)
```

### Working with Sessions

**1. Log events:**
```python
from session_logger import get_session_logger

logger = get_session_logger()
logger.log_event(
    event_type="question",
    game_profile_id="elden-ring",
    content="How do I beat Margit?",
    meta={"difficulty": "hard"}
)
```

**2. Retrieve session data:**
```python
events = logger.get_session_events("elden-ring")
for event in events:
    print(f"{event.timestamp}: {event.event_type} - {event.content}")
```

**3. Generate coaching:**
```python
from session_coaching import SessionCoach

coach = SessionCoach(ai_assistant, session_logger)
recap = coach.generate_recap("elden-ring", events)
print(recap)
```

---

## Troubleshooting Guide

### Common Issues

#### Game Not Detected

**Symptoms:** Game is running but not detected

**Diagnosis:**
1. Check if executable is in `game_detector.common_games`
2. Verify process name matches exactly
3. Check case sensitivity

**Solution:**
```python
# src/game_detector.py
# Add game executable
common_games = {
    "Your Game": ["correct_process_name.exe"],
}
```

**Debugging:**
```python
import psutil
for proc in psutil.process_iter(['name']):
    print(proc.info['name'])  # Find exact process name
```

#### API Key Not Working

**Symptoms:** "Invalid API key" or authentication errors

**Diagnosis:**
1. Verify key is saved in credential store
2. Check key format (correct prefix: `sk-ant-`, `sk-`, etc.)
3. Test key with provider directly

**Solution:**
```python
from credential_store import CredentialStore
store = CredentialStore()

# Re-save key
store.set_credential("omnix.ai", "anthropic_api_key", "sk-ant-...")

# Verify
key = store.get_credential("omnix.ai", "anthropic_api_key")
print(f"Stored key: {key[:10]}...")  # Should show first 10 chars
```

**Test connection:**
```python
from provider_tester import ProviderTester
tester = ProviderTester()
result = tester.test_connection("anthropic", api_key)
print(result.message)
```

#### Knowledge Pack Not Loading

**Symptoms:** Knowledge not appearing in AI responses

**Diagnosis:**
1. Check if pack is enabled
2. Verify pack is associated with game profile
3. Check index is built

**Solution:**
```python
from knowledge_store import get_knowledge_store
from knowledge_index import get_knowledge_index

store = get_knowledge_store()
index = get_knowledge_index()

# Verify pack
pack = store.load_pack("pack-id")
print(f"Enabled: {pack.enabled}")
print(f"Sources: {len(pack.sources)}")

# Rebuild index
index.index_pack(pack)

# Test search
chunks = index.search("test query", pack.game_profile_id)
print(f"Found {len(chunks)} chunks")
```

#### Knowledge Pack Search Quality Degraded After Restart

**Symptoms:** Search results are irrelevant or random after restarting the application

**Diagnosis:**
1. Check if you're running an older version (before 2025-11-19)
2. Verify index files exist in `~/.gaming_ai_assistant/knowledge_index/`
3. Look for warning: "Loaded legacy index format without embedding model"

**Root Cause (Fixed in v1.3+):**
- **Bug:** TF-IDF model vocabulary was not being persisted to disk
- **Impact:** After restart, queries used hash embeddings vs TF-IDF vectors
- **Result:** Mathematically invalid comparisons produced random results

**Solution:**
```python
from knowledge_index import get_knowledge_index
from knowledge_store import get_knowledge_store

# Rebuild index for affected game to fix legacy indices
index = get_knowledge_index()
store = get_knowledge_store()

# Get game profile ID
game_profile_id = "elden-ring"  # Replace with your game

# Rebuild index (this will save with new format)
index.rebuild_index_for_game(game_profile_id)

print(f"✓ Index rebuilt with TF-IDF model persistence")
```

**Verification:**
```python
# After rebuild, test search quality
results = index.query(
    game_profile_id="elden-ring",
    question="How do I beat Margit?",
    top_k=5
)

for i, result in enumerate(results, 1):
    print(f"{i}. Score: {result.score:.3f}")
    print(f"   Text: {result.text[:100]}...")
```

**Status:** ✅ Fixed in commit `78a2050` (2025-11-19)

#### Macro Not Executing

**Symptoms:** Hotkey pressed but macro doesn't run

**Diagnosis:**
1. Check if macro is enabled
2. Verify keybind is registered
3. Check for conflicts

**Solution:**
```python
from macro_store import get_macro_store
from keybind_manager import get_keybind_manager

macro_store = get_macro_store()
keybind_mgr = get_keybind_manager()

# Verify macro
macro = macro_store.load_macro("macro-id")
print(f"Enabled: {macro.enabled}")
print(f"Steps: {len(macro.steps)}")

# Verify keybind
keybinds = keybind_mgr.get_macro_keybinds()
for kb in keybinds:
    if kb.macro_id == "macro-id":
        print(f"Keybind: {kb.keys}, Enabled: {kb.enabled}")
```

#### GUI Freezing

**Symptoms:** UI becomes unresponsive

**Diagnosis:**
- Long-running operation in main thread
- Missing worker thread for AI calls
- Blocking I/O operation

**Solution:**
Always use worker threads:
```python
# BAD: Blocks GUI thread
response = ai_assistant.ask_question(question)
display_response(response)

# GOOD: Non-blocking with worker thread
worker = AIWorkerThread(ai_assistant, question)
worker.response_ready.connect(display_response)
worker.error_occurred.connect(display_error)
worker.start()
```

#### Build Errors

**Symptoms:** PyInstaller fails or executable crashes

**Diagnosis:**
1. Check all imports are found
2. Verify data files are included
3. Check for missing dependencies

**Solution:**
```python
# GamingAIAssistant.spec
# Add missing imports
hiddenimports = [
    'missing_module',
    'another_module'
]

# Add data files
datas = [
    ('.env.example', '.'),
    ('src/ui/icons/*.svg', 'ui/icons/')
]
```

**Test build:**
```bash
# Clean build
python build_windows_exe.py

# Debug build (shows console)
pyinstaller GamingAIAssistant_DEBUG.spec

# Run debug exe
dist/GamingAIAssistant/GamingAIAssistant.exe
```

#### PyInstaller --dry-run Error

**Symptoms:** `pyinstaller: error: unrecognized arguments: --dry-run` (exit code 1)

**Diagnosis:**
PyInstaller does not recognize `--dry-run` as a valid command-line option. This argument is not supported by PyInstaller.

**Solution:**
Remove the `--dry-run` argument from the PyInstaller command in your workflow or build script.

```bash
# BAD: Causes error
pyinstaller --noconfirm --log-level=DEBUG --clean --dry-run GamingAIAssistant.spec

# GOOD: Valid PyInstaller command
pyinstaller --noconfirm --log-level=DEBUG --clean GamingAIAssistant.spec
```

**Alternative for Testing:**
If you need to test your build steps without creating a full executable, consider:
- Using `--log-level=DEBUG` for diagnostic output (already included)
- Running a quick syntax validation of the spec file with Python:
  ```bash
  python -c "exec(open('GamingAIAssistant.spec').read())"
  ```
- Using PyInstaller's `--onefile` mode which is faster than `--onedir`

**Resolution History:**
- **2025-11-19:** Removed `--dry-run` argument from `.github/workflows/tests.yml` as PyInstaller does not support this option

#### Circular Import Errors

**Symptoms:** Application fails to start with `ImportError: cannot import name 'X' from partially initialized module 'Y' (most likely due to a circular import)`

**Diagnosis:**
1. Identify the circular dependency chain in the error traceback
2. Check for inconsistent import patterns (some using `src.` prefix, others not)
3. Verify import order in `src/__init__.py`

**Common Causes:**
- Inconsistent import prefixes (`from module import X` vs `from src.module import X`)
- Modules importing from `src/__init__.py` while also being imported by it
- Circular dependencies between modules
- **Module names conflicting with Python standard library** (e.g., `types.py`, `collections.py`)

**Solution:**
```python
# BAD: Inconsistent import pattern in src/ai_assistant.py
from knowledge_integration import get_knowledge_integration

# GOOD: Consistent with other src/ modules
from src.knowledge_integration import get_knowledge_integration

# BAD: Module name conflicts with Python stdlib
src/types.py  # Shadows built-in 'types' module

# GOOD: Use descriptive, non-conflicting names
src/type_definitions.py  # No conflict with stdlib
```

**Prevention:**
```bash
# Run the circular import test
python test_circular_import.py

# This test checks for:
# 1. Consistent use of 'src.' prefix in imports
# 2. Import pattern analysis across core modules
# 3. Circular dependency detection
```

**Resolution History:**
- **2025-11-18:** Fixed circular import in `ai_assistant.py` by adding `src.` prefix to `knowledge_integration` import
- **2025-11-18:** Fixed critical circular import caused by `src/types.py` shadowing Python's built-in `types` module; renamed to `src/type_definitions.py` and updated all references

### Debugging Tips

#### Enable Debug Logging

```python
# main.py
logging.basicConfig(
    level=logging.DEBUG,  # Change from INFO to DEBUG
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(sys.stdout)
    ]
)
```

#### Qt Debug Messages

```python
from PyQt6.QtCore import qDebug, qWarning, qCritical

qDebug("Debug message")
qWarning("Warning message")
qCritical("Critical error")
```

#### Profile Performance

```python
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()

# Code to profile
ai_assistant.ask_question("test")

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(10)  # Top 10 slowest
```

### Theme System (Unified as of 2025-11-17) ✅

**Migration Completed:** Omnix now uses a **unified token-based design system** with full backward compatibility.

#### Current Architecture

1. **Modern System** (`src/ui/theme_manager.py`):
   - `OmnixThemeManager` - Main theme management class
   - Direct manipulation of design tokens
   - Real-time UI updates via observer pattern
   - Automatic theme.json v1 → v2 migration
   - Full customization tracking

2. **Design Tokens** (`src/ui/tokens.py`):
   - `OmnixDesignTokens` - Color, typography, spacing, radius tokens
   - Single source of truth for all styling
   - Extensible and maintainable

3. **Compatibility Layer** (`src/theme_compat.py`):
   - `ThemeManagerCompat` - Wrapper providing legacy API
   - Allows existing code to work unchanged
   - Automatic bidirectional translation
   - Zero breaking changes

4. **Deprecated Files** (kept for reference):
   - `src/theme_manager.py` - Legacy theme manager (deprecated)
   - `src/ui/theme_bridge.py` - Old compatibility bridge (deprecated)

#### Using the Theme System

**For New Code:**
```python
from ui.theme_manager import get_theme_manager

theme_mgr = get_theme_manager()

# Update colors
theme_mgr.update_color('accent_primary', '#00FFFF')

# Update typography
theme_mgr.update_typography('size_base', 12)

# Save changes
theme_mgr.save_theme()

# Get stylesheet
stylesheet = theme_mgr.get_stylesheet()
```

**For Legacy Code:**
```python
from theme_compat import ThemeManager

theme_mgr = ThemeManager()
# Works exactly like old ThemeManager
# Automatically uses OmnixThemeManager backend
```

**Migration Details:** See `THEME_MIGRATION_PLAN.md`

#### ✅ Recent Fixes

**Status:** Latest fix completed 2025-11-19

**1. Search Index Corruption Fix (2025-11-19)** ⭐ **CRITICAL**

The knowledge pack search system was experiencing a critical bug where TF-IDF model state was not persisted to disk, causing search results to become random garbage after application restarts.

- **Issue:** Knowledge pack search returned irrelevant/random results after restarting application
- **Root Cause:** `SimpleTFIDFEmbedding` vocabulary and IDF values were not saved to disk
  - `_save_index()` only saved the index dict, not the TF-IDF model state
  - On restart, queries used hash-based embeddings while comparing against TF-IDF vectors
  - Resulted in mathematically invalid comparisons (different embedding spaces)
- **Fix:** Updated `src/knowledge_index.py:251-286`
  - `_save_index()` now serializes both index and embedding provider
  - `_load_index()` restores TF-IDF model state from disk
  - Backward compatible with legacy index files (logs warning, degrades gracefully)
- **Testing:** Added comprehensive `test_index_persistence_after_restart()` in `tests/unit/test_knowledge_system.py:316-405`
- **Impact:** Search results now remain accurate and consistent across restarts

**Verification:**
```python
# Verify TF-IDF model persistence
python -c "
import sys
sys.path.insert(0, 'src')
from knowledge_index import SimpleTFIDFEmbedding
import pickle

embedding = SimpleTFIDFEmbedding()
embedding.fit(['test doc one', 'test doc two'])
pickled = pickle.dumps(embedding)
unpickled = pickle.loads(pickled)
print(f'✓ Vocabulary: {len(unpickled.vocabulary)} terms')
print(f'✓ IDF: {len(unpickled.idf)} terms')
"
```

**Commit:** `78a2050` | **Branch:** `claude/fix-search-index-corruption-018pjySXbV9WEEHojJQgmkrY`

---

**2. Circular Import Resolution (2025-11-18)**

The application was experiencing a circular import error that prevented startup. The issue was resolved by ensuring consistent import patterns across all `src/` modules.

- **Issue:** `ImportError: cannot import name 'get_knowledge_integration' from partially initialized module 'knowledge_integration'`
- **Root Cause:** `src/ai_assistant.py` was importing `knowledge_integration` without the `src.` prefix, while all other modules used `from src.X import Y`
- **Fix:** Updated `src/ai_assistant.py:17` to use `from src.knowledge_integration import...`
- **Prevention:** Added `test_circular_import.py` to detect import pattern inconsistencies
- **Impact:** Application now starts successfully without import errors

**Testing:**
```bash
# Verify no circular imports
python test_circular_import.py
```

See [Troubleshooting Guide - Circular Import Errors](#circular-import-errors) for more details.

---

#### ✅ Recently Removed Features

**Status:** Completed in 2025-11-17

The following features were removed to streamline the codebase and reduce complexity:

1. **info_scraper.py** - Web scraping module for game wikis
   - **Reason:** Unstable and fragile; broke when websites changed HTML
   - **Replacement:** Knowledge System (knowledge_packs) provides more robust, user-controlled solution
   - **Impact:** Users can add specific wiki/guide URLs to Knowledge Packs instead

2. **login_dialog.py** - Embedded web browser for OAuth authentication
   - **Reason:** Redundant with secure API key management; insecure session cookie capture
   - **Replacement:** Setup Wizard and Providers Tab for API key management
   - **Impact:** No impact; embedded login was unused in production code

3. **PyQt6-WebEngine** dependency
   - **Reason:** Massive dependency only needed for removed login_dialog
   - **Impact:** Significantly reduced application size and build complexity

**Benefits:**
- Reduced codebase complexity (~350 LOC removed)
- Smaller application binary size (no WebEngine)
- More stable knowledge system (user-controlled vs. fragile web scraping)
- Single, secure authentication method (API keys via credential store)

#### ✅ Dependencies Clarification

**Note:** Some analysis tools may flag `scikit-learn` as a missing dependency for the knowledge system. This is **incorrect**.

The `SimpleTFIDFEmbedding` class in `src/knowledge_index.py` implements TF-IDF **from scratch** using only Python standard library:
- `re` module for tokenization
- `math` module for TF-IDF calculations
- `hashlib` for fallback embeddings

**No additional dependencies are required** for the knowledge system to function.

#### ✅ Build Files

**Note:** Only use the following build files:
- `GamingAIAssistant.spec` - Production build
- `GamingAIAssistant_DEBUG.spec` - Debug build with console
- `build_windows_exe.py` - Automated build script
- All `.bat` files in the repository

Any other `.spec` files found in older documentation should be ignored as they may be outdated.

---

## Extension Points

### Easy Extensions

#### 1. New Game Support
- **Difficulty:** Easy
- **Files:** `game_detector.py`, `game_profile.py`
- **Steps:** Add executable mapping, create profile

#### 2. New AI Provider
- **Difficulty:** Medium
- **Files:** `providers.py`, `ai_router.py`, `providers_tab.py`
- **Steps:** Implement provider interface, add UI configuration

#### 3. New Macro Step Type
- **Difficulty:** Easy
- **Files:** `macro_manager.py`, `macro_runner.py`
- **Steps:** Add enum value, implement execution logic

#### 4. New UI Component
- **Difficulty:** Easy
- **Files:** `ui/components/`
- **Steps:** Create component file, use design tokens

#### 5. New Knowledge Source Type
- **Difficulty:** Medium
- **Files:** `knowledge_pack.py`, `knowledge_ingestion.py`
- **Steps:** Add source type, implement ingestion

#### 6. New Session Event Type
- **Difficulty:** Easy
- **Files:** `session_logger.py`
- **Steps:** Add event type to enum, log events

### Future Features (Roadmap)

From README.md:
- [ ] Voice input support
- [ ] Advanced overlay transparency modes
- [ ] Custom hotkeys for quick actions
- [ ] Game-specific plugins
- [ ] Multi-language support
- [ ] Mobile companion app
- [ ] Replay analysis
- [ ] Performance tracking

### Plugin System Ideas

**1. Game-Specific Plugins:**
```python
# src/plugins/elden_ring_plugin.py
class EldenRingPlugin(GamePlugin):
    def on_game_detected(self, game):
        # Custom behavior for Elden Ring
        pass

    def enhance_ai_response(self, response, context):
        # Add Elden Ring-specific formatting
        pass
```

**2. Custom Scrapers:**
```python
# src/scrapers/custom_scraper.py
class CustomWikiScraper(WikiScraper):
    def scrape(self, url):
        # Custom scraping logic
        pass
```

**3. AI Enhancement Plugins:**
```python
# src/ai_plugins/fact_checker.py
class FactCheckerPlugin(AIPlugin):
    def post_process(self, response):
        # Verify facts against knowledge base
        pass
```

---

## Best Practices Summary

### ✅ DO

1. **Use design system components** for all UI elements
2. **Use worker threads** for long-running operations
3. **Log events** for debugging and coaching
4. **Type hint** function signatures
5. **Handle errors** with specific exception types
6. **Test before committing** - run test suite
7. **Save configuration** changes explicitly
8. **Use credential store** for API keys
9. **Follow naming conventions** consistently
10. **Document public APIs** with docstrings

### ❌ DON'T

1. **Don't block the GUI thread** with long operations
2. **Don't hardcode styles** - use design tokens
3. **Don't store API keys in .env** - use credential store
4. **Don't skip error handling** on external API calls
5. **Don't modify built-in game profiles** - create custom ones
6. **Don't commit API keys** or credentials
7. **Don't use raw Qt widgets** - use design system components
8. **Don't ignore test failures** - fix before committing
9. **Don't bypass safety limits** in macro execution
10. **Don't modify core architecture** without discussion

---

## Quick Reference

### Important File Locations

```
Main entry:           main.py
Configuration:        src/config.py
Game detection:       src/game_detector.py
AI integration:       src/ai_assistant.py, src/providers.py
Knowledge system:     src/knowledge_*.py
Macro system:         src/macro_*.py
GUI:                  src/gui.py
Design system:        src/ui/design_system.py
Components:           src/ui/components/

User data:            ~/.gaming_ai_assistant/
Logs:                 ./gaming_ai_assistant_*.log
```

### Key Commands

```bash
# Development
python main.py                    # Run application
python test_before_build.py       # Run tests
python build_windows_exe.py       # Build executable

# Testing
python -m pytest                  # Run all tests
python test_modules.py            # Test imports
python test_macro_system.py       # Test macros

# Git
git checkout -b claude/feature    # Create branch
git commit -m "message"           # Commit changes
git push -u origin claude/feature # Push branch
```

### Contact & Resources

- **Repository:** https://github.com/shingoku2/Omnix-All-knowing-gaming-companion
- **Current Branch:** `claude/claude-md-mi0udx5q25azj8gs-014ci8Xyu9DvRRXC76VYQcE5`
- **Issues:** GitHub Issues
- **Documentation:** README.md, SETUP.md, this file

---

**Last Updated:** 2025-11-15
**Maintained by:** AI assistants working on Omnix

---

*This guide is designed to help AI assistants understand and work with the Omnix codebase effectively. For user-facing documentation, see README.md.*
