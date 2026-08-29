This is a passion project of mine. I am using AI to fully help me code the entire app. So I guess it's also an experiment, to see if it's possible.

# 🎮 Omnix - All-knowing Gaming Companion

A sophisticated desktop AI gaming companion that automatically detects what game you're playing and provides AI-powered assistance, knowledge integration, macro automation, and session coaching to enhance your gaming experience.

[![Tests](https://github.com/shingoku2/Omnix-All-knowing-gaming-companion/actions/workflows/tests.yml/badge.svg)](https://github.com/shingoku2/Omnix-All-knowing-gaming-companion/actions/workflows/tests.yml)
[![codecov](https://codecov.io/gh/shingoku2/Omnix-All-knowing-gaming-companion/branch/main/graph/badge.svg)](https://codecov.io/gh/shingoku2/Omnix-All-knowing-gaming-companion)
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)

## ✨ Features

### Core Features
- **🎯 Automatic Game Detection** - Monitors 15 pre-configured games with custom profile support
- **🤖 Ollama AI Integration** - Local/remote LLM inference without API keys
- **📚 Knowledge System** - Per-game knowledge packs with semantic search (TF-IDF)
- **⌨️ Macro & Automation** - Record and execute keyboard/mouse macros with hotkey support
- **📊 Session Coaching** - AI-powered gameplay insights and improvement tips
- **🔒 Privacy First** - All AI inference runs locally by default

### User Interface
- **🎨 Modern Design System** - Consistent UI with design tokens and reusable components
- **🪟 Advanced Overlay** - Movable, resizable, minimizable with auto-save
- **📐 Display Modes** - Switch between compact and full chat interfaces
- **⌨️ Global Hotkeys** - Customizable shortcuts for all actions
- **🌙 Dark Theme** - Sleek gaming-optimized dark interface

### Intelligence Features
- **🔍 Knowledge Integration** - Import PDFs, documents, wikis, and notes per game
- **🧠 Semantic Search** - Find relevant information with TF-IDF embeddings
- **🎮 Game-Specific AI** - Customized system prompts for each game profile
- **📝 Session Tracking** - Log interactions and generate AI-powered recaps
- **💡 Coaching Insights** - Personalized tips based on your gameplay patterns

## 🎥 Demo

The assistant automatically:
1. Detects when you launch a game
2. Provides an overview and general tips
3. Answers your specific questions about gameplay
4. Scrapes relevant wikis and guides for additional context

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- **[Ollama](https://ollama.com/)** - Local/remote AI models (free, no API key required)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/shingoku2/Omnix-All-knowing-gaming-companion.git
   cd Omnix-All-knowing-gaming-companion
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install and configure Ollama**
   ```bash
   # Install Ollama from https://ollama.com

   # Pull a model (choose one):
   ollama pull llama3       # Recommended - fast and capable
   ollama pull mistral      # Alternative - fast and efficient
   ollama pull codellama    # Optimized for coding/technical content

   # Verify Ollama is running:
   ollama list
   ```

4. **Run the application**
   ```bash
   python main.py
   ```

   **The Setup Wizard will appear on first run** and guide you through:
   - Configuring Ollama connection (base URL, model selection)
   - Testing the connection to Ollama daemon
   - Selecting your preferred model from available options
   - Saving your configuration

### Manual Configuration (Optional)

If you prefer to skip the Setup Wizard, configure `.env` manually:

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env to configure Ollama
AI_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434  # Default Ollama host (optional)
OLLAMA_MODEL=llama3  # Default model (optional, can be changed in UI)

# For remote Ollama instances:
# OLLAMA_BASE_URL=http://your-server-ip:11434
```

### 🦙 About Ollama

Omnix now uses **Ollama exclusively** for AI inference, allowing you to run AI models **completely locally and for free** on your own computer!

**Why Ollama?**
- ✅ **100% Free** - No API costs, no subscriptions
- ✅ **Privacy First** - All data stays on your machine
- ✅ **Offline Capable** - Works without internet
- ✅ **No Rate Limits** - Use as much as you want
- ✅ **Open Source** - Fully transparent, community-driven
- ✅ **Model Freedom** - Use any Ollama model (llama3, mistral, codellama, etc.)

**Hardware Requirements:**
- **Minimum:** 8GB RAM
- **Recommended:** 16GB+ RAM, dedicated GPU
- **Storage:** 4-8GB per model

**Recommended Models:**
```bash
# General gaming assistance (recommended):
ollama pull llama3          # 4.7GB - Fast, general-purpose
ollama pull llama3.1        # 4.7GB - Improved reasoning

# Alternatives:
ollama pull mistral         # 4.1GB - Fast and efficient
ollama pull gemma2:9b       # 5.4GB - Google's compact model

# Specialized:
ollama pull codellama       # 3.8GB - Optimized for technical content
```

**Remote Ollama:**
You can also connect to a remote Ollama instance running on another machine:
```bash
# .env configuration
OLLAMA_BASE_URL=http://192.168.1.100:11434

# Or use the UI: Settings > AI Providers > Base URL
```

## 📖 Usage

### Basic Usage

1. Launch the Gaming AI Assistant
2. Open any supported game
3. The assistant will automatically detect it and provide an overview
4. Ask questions in the chat interface
5. Use Ctrl+Shift+G to toggle the window visibility

### Example Questions

- "What's the best build for a tank character?"
- "How do I defeat the boss in the Fire Temple?"
- "What are some beginner tips?"
- "Explain the crafting system"
- "What's the current meta?"

### Keyboard Shortcuts

- **Ctrl+Shift+G** - Toggle assistant window
- **Enter** - Send message
- **Escape** - Clear input field

### Overlay Controls

- **Drag Title Bar** - Move the window anywhere on screen
- **Drag Edges** - Resize window from any edge or corner
- **Minimize Button (−)** - Collapse window to title bar only
- **Auto-Save** - Window position and size automatically saved to config

## 🎮 Supported Games

The assistant has built-in support for 15 popular games including:

### MOBA & Competitive
- League of Legends
- Dota 2
- VALORANT
- Counter-Strike 2
- Overwatch

### RPG & Adventure
- Elden Ring
- Dark Souls 3
- The Witcher 3
- Skyrim
- Cyberpunk 2077
- Final Fantasy XIV

### Battle Royale
- Fortnite
- Apex Legends
- PUBG
- Call of Duty: Warzone

### MMO
- World of Warcraft
- Guild Wars 2
- Elder Scrolls Online

### And many more...

*Don't see your game? The assistant can still detect and help with unknown games!*

## 🔧 Advanced Features

### Knowledge Packs
Create game-specific knowledge bases to enhance AI responses:
- **Import Sources**: PDFs, DOCX, TXT, Markdown files, or web URLs
- **Semantic Search**: TF-IDF-based retrieval finds relevant information
- **Per-Game Organization**: Each game can have multiple knowledge packs
- **Automatic Integration**: Knowledge automatically augments AI conversations

**Example Use Cases:**
- Import boss strategy guides for Elden Ring
- Add build guides for League of Legends
- Save patch notes for competitive games

### Macro System
Automate repetitive actions with keyboard/mouse macros:
- **Record Macros**: Capture keyboard and mouse inputs
- **AI-Assisted Creation**: Generate macros from natural language descriptions
- **Global Hotkeys**: Bind macros to custom keyboard shortcuts
- **Safety Limits**: Built-in protections against infinite loops and runaway execution
- **Game-Specific**: Create macros that only activate for specific games

**Macro Step Types:**
- Key press/hold/release
- Mouse movement and clicks
- Scroll actions
- Delays with jitter (anti-detection)
- Text typing sequences

### Session Coaching
Track your gaming sessions and get AI-powered insights:
- **Automatic Logging**: All questions and answers are tracked
- **Session Recaps**: AI-generated summaries of your gaming session
- **Pattern Recognition**: Identify areas where you need help most
- **Personalized Tips**: Coaching based on your actual gameplay questions
- **Progress Tracking**: See your improvement over time

### Game Profiles
Customize AI behavior per game:
- **Custom System Prompts**: Tailor AI personality and expertise
- **Provider Selection**: Choose different AI providers per game
- **Overlay Preferences**: Set default display mode (compact/full)
- **Knowledge Integration**: Enable/disable knowledge packs
- **Macro Library**: Game-specific automation scripts

## 🏗️ Project Structure

**~14,700 lines of Python code** organized into a modular architecture:

```
Omnix-All-knowing-gaming-companion/
├── main.py                      # Application entry point
├── requirements.txt             # Python dependencies
├── .env.example                 # Configuration template
├── CLAUDE.md                    # Comprehensive developer guide
├── README.md                    # This file
├── GamingAIAssistant.spec       # PyInstaller build specification
│
└── src/                         # Main source directory
    ├── Core Application
    ├── config.py                # Configuration management
    ├── credential_store.py      # Encrypted API key storage
    │
    ├── Game Detection
    ├── game_detector.py         # Process monitoring & detection
    ├── game_watcher.py          # Background monitoring thread
    ├── game_profile.py          # Per-game configurations
    │
    ├── AI Integration
    ├── ai_assistant.py          # High-level AI interface
    ├── ai_router.py             # Multi-provider routing
    ├── providers.py             # Ollama provider implementation
    │
    ├── Knowledge System
    ├── knowledge_pack.py        # Knowledge data structures
    ├── knowledge_store.py       # Persistence layer
    ├── knowledge_index.py       # TF-IDF semantic search
    ├── knowledge_integration.py # AI augmentation
    ├── knowledge_ingestion.py   # Import from files/URLs
    │
    ├── Macro & Automation
    ├── macro_manager.py         # Macro definitions
    ├── macro_runner.py          # Execution engine
    ├── keybind_manager.py       # Global hotkey system
    │
    ├── Session Management
    ├── session_logger.py        # Event tracking
    ├── session_coaching.py      # AI-powered insights
    │
    ├── GUI Layer
    ├── gui.py                   # Main application window
    ├── settings_dialog.py       # Settings interface
    ├── settings_tabs.py         # Advanced configuration
    ├── appearance_tabs.py       # Theme customization UI
    │
    ├── Theme System
    ├── theme_compat.py          # Backward compatibility wrapper
    ├── theme_manager.py         # [DEPRECATED] Legacy theme system
    │
    └── ui/                      # Design System
        ├── design_system.py     # Centralized styling
        ├── tokens.py            # Design tokens
        ├── theme_manager.py     # Unified theme management
        └── components/          # Reusable UI components
            ├── buttons.py
            ├── inputs.py
            ├── cards.py
            └── ... more
```

For detailed architecture documentation, see [CLAUDE.md](CLAUDE.md).

## ⚙️ Configuration

### Secure API Key Storage
Local Ollama mode does **not** need API keys. If you connect to a secured or remote
Ollama endpoint, any required credentials are stored securely using your system's
credential manager:
- **Windows**: Windows Credential Manager
- **macOS**: Keychain
- **Linux**: SecretService with encrypted file fallback

Keys are encrypted with AES-256 and never stored in plain text.

### Basic Configuration
Edit `.env` to customize the application:

```env
# AI Provider (Ollama-first)
AI_PROVIDER=ollama
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3

# Application Settings
OVERLAY_HOTKEY=ctrl+shift+g    # Hotkey to toggle window
CHECK_INTERVAL=5               # Game detection interval (seconds)

# Overlay Window Settings (auto-saved when you move/resize)
OVERLAY_X=100                  # Window X position
OVERLAY_Y=100                  # Window Y position
OVERLAY_WIDTH=900              # Window width
OVERLAY_HEIGHT=700             # Window height
OVERLAY_MINIMIZED=false        # Minimized state
OVERLAY_OPACITY=0.95           # Window transparency (0.0-1.0)
```

### Extended Configuration
Additional settings are stored in `~/.gaming_ai_assistant/`:
- `game_profiles.json` - Custom game configurations
- `macros.json` - Macro definitions
- `keybinds.json` - Custom hotkey bindings
- `theme.json` - Appearance preferences
- `knowledge_packs/` - Game knowledge bases
- `sessions/` - Gaming session logs

## 🎨 Customization

### Adding Custom Games

You can add support for any game through the GUI:
1. Open **Settings** → **Game Profiles**
2. Click **Add Custom Profile**
3. Enter the game's executable name (e.g., `yourgame.exe`)
4. Customize the AI system prompt
5. Set preferred AI provider and overlay mode

Or edit `src/game_detector.py` directly:

```python
common_games = {
    "Your Game Name": ["yourgame.exe", "alternate.exe"],
    # ... more games
}
```

## 🛠️ Development

### Running Tests

Comprehensive test suite with 10+ test files:

```bash
# Run all tests
python -m pytest

# Run specific test suites
python test_modules.py           # Module imports
python test_macro_system.py      # Macro functionality
python test_knowledge_system.py  # Knowledge packs
python test_game_profiles.py     # Game profiles
python test_edge_cases.py        # Error handling

# Pre-build validation
python test_before_build.py

# Live API testing (requires API keys)
python live_test.py
```

### Building Executables

Build standalone Windows executable:

```bash
# Automated build script
python build_windows_exe.py

# Manual PyInstaller build
pyinstaller GamingAIAssistant.spec

# Debug build (shows console)
pyinstaller GamingAIAssistant_DEBUG.spec
```

Output: `dist/GamingAIAssistant/GamingAIAssistant.exe`

### Development Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run from source
python main.py
```

### Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes and test thoroughly
4. Commit with clear messages (`git commit -m 'Add amazing feature'`)
5. Push to your branch (`git push origin feature/amazing-feature`)
6. Submit a pull request

See [CLAUDE.md](CLAUDE.md) for detailed architecture documentation.

## 📋 Requirements

### Core Technologies
- **Python** 3.8+ (3.10+ recommended)
- **PyQt6** 6.6.0+ - Desktop GUI framework

### AI Provider
- **ollama** 0.1.0+ - Local/remote LLM inference (required)

### System Integration
- **psutil** 5.9.0+ - Process monitoring for game detection
- **pynput** 1.7.6+ - Keyboard/mouse automation
- **keyring** 24.2.0+ - Secure credential storage
- **cryptography** 41.0.0+ - API key encryption

### Data Processing
- **beautifulsoup4** 4.12.0+ - HTML/XML parsing
- **lxml** 4.9.0+ - Fast XML/HTML processing

### Configuration
- **python-dotenv** 1.0.0+ - Environment configuration
- **pywin32** 306+ - Windows-specific features

See `requirements.txt` for complete dependency list.

## ⚠️ Troubleshooting

### Ollama connection issues
- Verify the Ollama daemon is running (`ollama serve` or the installed service)
- Check `OLLAMA_HOST` matches your daemon address (default `http://localhost:11434`)
- Ensure the model is pulled locally: `ollama pull llama3`
- Use Settings → AI Providers → Test Connection to validate connectivity

### Game Not Detected
- Verify the game is actually running
- Check Task Manager/Activity Monitor for the exact process name
- Add custom profile: Settings → Game Profiles → Add Custom Profile
- Check logs in `gaming_ai_assistant_*.log` for detection attempts

### Knowledge Packs Not Working
- Ensure knowledge pack is enabled: Settings → Knowledge Packs
- Verify pack is associated with the correct game profile
- Rebuild index if needed (delete and re-add sources)
- Check that knowledge integration is enabled in game profile settings

### Macros Not Executing
- Verify macro is enabled in Macro Manager
- Check hotkey bindings for conflicts
- Ensure game window has focus (if not set to system-wide)
- Review macro execution logs for errors

### GUI Freezing or Slow Response
- Long AI responses may take time (normal behavior)
- Check internet connection for API calls
- Try reducing conversation history length in settings
- Verify system has adequate RAM (2GB+ recommended)

### Build or Installation Errors
- Ensure Python 3.8+ is installed
- Use virtual environment to avoid conflicts
- Install all dependencies: `pip install -r requirements.txt`
- On Windows, install Visual C++ Redistributable if needed
- On Linux, install PyQt6 system packages

For detailed troubleshooting, see [CLAUDE.md](CLAUDE.md) Troubleshooting Guide.

## 🔐 Privacy & Security

### Data Protection
- **Local Processing**: All data processing happens on your machine
- **Direct API Calls**: Communicates directly with AI providers (no intermediaries)
- **Encrypted Storage**: API keys encrypted with AES-256 and stored in system keyring
- **No Telemetry**: No usage tracking, analytics, or data collection
- **Session Privacy**: Gaming sessions stored locally only

### What Gets Sent to AI Providers
- Your questions and conversation history
- Game context (game name, current profile)
- Relevant knowledge pack excerpts (if enabled)
- No screenshots, no keystrokes, no personal data beyond what you type

### Security Features
- **Credential Encryption**: AES-256 encryption for API keys
- **System Keyring**: Platform-native secure storage (Credential Manager, Keychain, SecretService)
- **Macro Safety Limits**: Prevents runaway automation with timeouts and repeat limits
- **No Code Execution**: Knowledge packs and macros don't execute arbitrary code
- **Git Safety**: API keys never committed to repository (.gitignore protected)

### Platform Security
- **Windows**: Windows Credential Manager integration
- **macOS**: Keychain Services integration
- **Linux**: SecretService D-Bus API with encrypted fallback

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Gaming wikis and communities for game information
- Ollama for local/remote AI inference
- The gaming community for inspiration

## 🤝 Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Check existing issues for solutions
- Contribute improvements via pull requests

## 📝 Recent Updates

### Version 2.0 (Ollama-first release)
- ✅ **Ollama-only defaults** – App now ships configured for local Ollama (no API keys)
- ✅ **Simplified setup** – Setup Wizard focuses on Ollama host/model selection
- ✅ **Lean dependencies** – Removed cloud provider SDKs from core install

### CI/CD & Infrastructure
- ✅ **CI/CD Pipeline** - Self-hosted Proxmox infrastructure with automated testing
- ✅ **Staging Deployment** - Automated deployment to staging environment
- ✅ **Comprehensive Testing** - 20+ CI integration tests for pipeline validation
- ✅ **Deployment Tools** - Verification scripts and automated backup system

### Critical Bug Fixes
- ✅ **Knowledge Index Persistence** - Fixed TF-IDF model state not persisting to disk
  - Search results now remain accurate after application restarts
  - No more random/irrelevant knowledge pack search results
- ✅ **Circular Import Resolution** - Fixed startup errors from inconsistent import patterns

### Technical Improvements
- ✅ **Enhanced Documentation** - Comprehensive CI/CD guides and quick references
- ✅ **Improved Security** - Enhanced credential storage and validation
- ✅ **Performance Optimizations** - Faster startup and reduced memory usage

### Version 1.2+ (2025-11-17)
**Major Feature Additions:**
- ✅ **Knowledge Pack System** - Import and search game-specific knowledge bases
- ✅ **Macro Automation** - Create and execute keyboard/mouse macros
- ✅ **Session Coaching** - AI-powered gameplay insights and session recaps
- ✅ **Design System** - Comprehensive UI component library with design tokens
- ✅ **Secure Credentials** - System keyring integration with AES-256 encryption
- ✅ **Game Profiles** - Advanced per-game AI customization
- ✅ **Global Hotkeys** - Customizable keybindings system

**Technical Improvements (2025-11-17):**
- ✅ **Unified Theme System** - Migrated from dual theme systems to unified token-based design
  - Consolidated legacy theme_manager.py and new ui/design_system.py into single OmnixThemeManager
  - Per-token customization with real-time UI updates via observer pattern
  - Automatic theme.json v1 → v2 migration with backward compatibility
  - Zero breaking changes via compatibility layer
- ✅ **Dependency Cleanup** - Removed unnecessary dependencies
  - Removed PyQt6-WebEngine (was only used for deprecated login_dialog feature)
  - Removed scikit-learn (using custom TF-IDF implementation)
  - Smaller binary size and faster installation

**Infrastructure:**
- ✅ **~14,700 LOC** - Extensive codebase with modular architecture
- ✅ **10+ Test Files** - Comprehensive test coverage
- ✅ **CLAUDE.md** - Detailed developer documentation
- ✅ **PyInstaller Build** - Windows executable distribution

### Version 1.2 (2025-11-13)
**UI Improvements:**
- ✅ **Movable & Resizable Overlay** - Drag window to any position, resize from edges/corners
- ✅ **Minimize/Restore Button** - Collapse overlay to title bar
- ✅ **Auto-Save Window Layout** - Position and size automatically saved
- ✅ **Dashboard Redesign** - 2x3 layout with avatar display

### Version 1.1 (2025-11-13)
**Provider Streamlining:**
### v2.0.0 - Ollama-Only Migration (2025-12-06)
- ✅ **Simplified to Ollama exclusively** - Removed cloud provider dependencies
- ✅ **No API keys required** - Privacy-first, local-first architecture
- ✅ **Model freedom** - Use any Ollama model (llama3, mistral, codellama, etc.)
- ✅ **Automatic model discovery** - UI shows available models from Ollama daemon
- ✅ **Connection testing** - Validates Ollama availability
- ✅ **Parameter translation** - Maps common parameters (max_tokens → num_predict)
- ✅ **Flexible hosting** - Supports both local and remote Ollama instances

### Example Ollama Models
- ✅ **llama3** - Fast, general-purpose (recommended)
- ✅ **mistral** - Fast and efficient alternative
- ✅ **codellama** - Optimized for technical content
- ✅ **gemma2** - Google's compact model
- ✅ **...and any other Ollama model** - Full flexibility

## 🗺️ Roadmap

### Planned Features
- [ ] **Voice Input Support** - Speak questions instead of typing
- [ ] **Advanced Overlay Modes** - Transparent window overlay, always-on-top
- [ ] **Plugin System** - Game-specific extension plugins
- [ ] **Multi-Language Support** - Internationalization (i18n)
- [ ] **Mobile Companion App** - Cross-platform mobile client
- [ ] **Replay Analysis** - Analyze recorded gameplay with AI
- [ ] **Performance Tracking** - Stats tracking and improvement metrics
- [ ] **Cloud Sync** - Sync knowledge packs and settings across devices
- [ ] **Community Knowledge** - Share knowledge packs with other users
- [ ] **Advanced Macro Recorder** - Visual macro builder with conditional logic

### Under Consideration
- [ ] **Screenshot Analysis** - AI vision for gameplay screenshots
- [ ] **Streaming Integration** - Twitch/YouTube chat integration
- [ ] **Tournament Mode** - Features for competitive gaming
- [ ] **Team Coordination** - Multi-user session support

## 🔗 Quick Links

- **Repository**: [github.com/shingoku2/Omnix-All-knowing-gaming-companion](https://github.com/shingoku2/Omnix-All-knowing-gaming-companion)
- **Developer Guide**: [CLAUDE.md](CLAUDE.md) - Comprehensive architecture documentation
- **Setup Guide**: [SETUP.md](SETUP.md) - Installation and configuration
- **Issues**: [GitHub Issues](https://github.com/shingoku2/Omnix-All-knowing-gaming-companion/issues)
- **Pull Requests**: [GitHub PRs](https://github.com/shingoku2/Omnix-All-knowing-gaming-companion/pulls)

## 💻 Technology Stack

**Language & Framework:**
- Python 3.8+ (~14,700 LOC)
- PyQt6 for desktop GUI

**AI Integration:**
- Ollama (local/remote LLM inference)
- Supports any Ollama model (llama3, mistral, codellama, etc.)

**Key Libraries:**
- **UI**: PyQt6
- **Process Monitoring**: psutil
- **Automation**: pynput
- **Security**: cryptography, keyring
- **Web Scraping**: requests, BeautifulSoup4, lxml
- **Semantic Search**: Custom TF-IDF implementation (no ML dependencies)

**Platform Support:**
- ✅ Windows 10/11 (Primary)
- ✅ macOS (Supported)
- ✅ Linux (Supported)

---

## 🌟 Star History

If you find Omnix useful, please consider giving it a star! ⭐

This helps others discover the project and motivates continued development.

---

**Made with ❤️ for gamers by gamers**

*This project demonstrates the power of AI-assisted development - the entire codebase was created with AI collaboration.*

*Happy Gaming! 🎮*
