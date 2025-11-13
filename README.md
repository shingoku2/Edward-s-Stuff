# 🎮 Gaming AI Assistant

An intelligent, real-time gaming companion that automatically detects what game you're playing and provides AI-powered tips, strategies, and answers to your questions while you play.

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## ✨ Features

- **🎯 Automatic Game Detection** - Detects running games by monitoring processes
- **🤖 AI-Powered Assistant** - Uses Claude, GPT, or Gemini to answer gaming questions in real-time
- **🔍 Web Information Retrieval** - Scrapes gaming wikis, forums, and guides automatically
- **💬 Real-Time Q&A** - Ask questions about the game and get instant answers
- **🎨 Modern GUI** - Clean, dark-themed interface with system tray support
- **⌨️ Hotkey Support** - Quick access with Ctrl+Shift+G
- **📐 Movable & Resizable Overlay** - Drag to move, resize from edges, remembers position
- **🪟 Minimize/Restore** - Collapse overlay to title bar, one-click restore
- **💾 Auto-Save Layout** - Window position and size saved automatically
- **📚 Game Knowledge Base** - Supports 50+ popular games out of the box
- **🌐 Multi-Source Intelligence** - Combines AI with wiki data and community resources

## 🎥 Demo

The assistant automatically:
1. Detects when you launch a game
2. Provides an overview and general tips
3. Answers your specific questions about gameplay
4. Scrapes relevant wikis and guides for additional context

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- An API key from one of:
  - [Anthropic (Claude)](https://www.anthropic.com/) (recommended)
  - [OpenAI (GPT)](https://platform.openai.com/)
  - [Google (Gemini)](https://aistudio.google.com/app/apikey)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/gaming-ai-assistant.git
   cd gaming-ai-assistant
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure API keys**
   ```bash
   # Copy the example environment file
   cp .env.example .env

   # Edit .env and add your API key
   # For Anthropic (recommended):
   ANTHROPIC_API_KEY=your_api_key_here
   AI_PROVIDER=anthropic

   # OR for OpenAI:
   OPENAI_API_KEY=your_api_key_here
   AI_PROVIDER=openai

   # OR for Google Gemini:
   GEMINI_API_KEY=your_api_key_here
   AI_PROVIDER=gemini
   ```

4. **Run the application**
   ```bash
   python main.py
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

The assistant has built-in support for 50+ popular games including:

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

## 🏗️ Project Structure

```
gaming-ai-assistant/
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies
├── .env.example           # Example environment configuration
├── .gitignore            # Git ignore file
├── README.md             # This file
└── src/
    ├── game_detector.py   # Game detection module
    ├── ai_assistant.py    # AI integration (Claude/GPT)
    ├── info_scraper.py    # Web scraping for game info
    ├── gui.py            # GUI interface
    └── config.py         # Configuration management
```

## ⚙️ Configuration

Edit `.env` to customize the application:

```env
# AI Provider (choose one: anthropic, openai, or gemini)
AI_PROVIDER=anthropic
ANTHROPIC_API_KEY=your_key
OPENAI_API_KEY=your_key
GEMINI_API_KEY=your_key

# Application Settings
OVERLAY_HOTKEY=ctrl+shift+g    # Hotkey to toggle window
CHECK_INTERVAL=5               # Game detection interval (seconds)

# Overlay Window Settings (auto-saved when you move/resize)
OVERLAY_X=100                  # Window X position
OVERLAY_Y=100                  # Window Y position
OVERLAY_WIDTH=900              # Window width
OVERLAY_HEIGHT=700             # Window height
OVERLAY_MINIMIZED=false        # Minimized state
```

## 🔧 Advanced Features

### Adding Custom Games

Edit `src/game_detector.py` to add custom game detection:

```python
KNOWN_GAMES = {
    "yourgame.exe": "Your Game Name",
    # ... more games
}
```

### Custom Wiki Sources

Add custom wiki URLs in `src/info_scraper.py`:

```python
self.wiki_urls = {
    "Your Game": "https://yourgame.wiki.com/",
    # ... more wikis
}
```

## 🛠️ Development

### Running Tests

```bash
# Test game detection
python src/game_detector.py

# Test AI assistant
python src/ai_assistant.py

# Test web scraper
python src/info_scraper.py
```

### Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📋 Requirements

- Python 3.8+
- psutil (process monitoring)
- requests (web scraping)
- beautifulsoup4 (HTML parsing)
- PyQt6 (GUI framework)
- openai or anthropic (AI providers)
- python-dotenv (environment configuration)

## ⚠️ Troubleshooting

### "No API key found"
- Make sure you've copied `.env.example` to `.env`
- Add your API key to the `.env` file
- Set `AI_PROVIDER` to match your API key

### "No game detected"
- Make sure the game is running
- Check if your game is in the supported games list
- Try adding your game manually to `KNOWN_GAMES`

### GUI doesn't start
- Make sure PyQt6 is installed: `pip install PyQt6`
- On Linux, you may need: `apt-get install python3-pyqt6`

## 🔐 Privacy & Security

- All data is processed locally on your machine
- API calls are made directly to OpenAI/Anthropic (no intermediaries)
- No game data is stored or transmitted except to the AI provider
- API keys are stored locally in `.env` file (never committed to git)

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Gaming wikis and communities for game information
- OpenAI and Anthropic for AI capabilities
- The gaming community for inspiration

## 🤝 Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Check existing issues for solutions
- Contribute improvements via pull requests

## 📝 Recent Updates

### Version 1.2 (2025-11-13)
- ✅ **Movable & Resizable Overlay** - Drag window to any position, resize from edges/corners
- ✅ **Minimize/Restore Button** - Collapse overlay to title bar for minimal screen space usage
- ✅ **Auto-Save Window Layout** - Position and size automatically saved to .env configuration
- ✅ **Smart Cursor Feedback** - Cursor changes to indicate resize directions

### Version 1.1 (2025-11-13)
- ✅ **Removed Ollama/Open WebUI support** - Streamlined to focus on mainstream cloud AI providers (OpenAI, Anthropic, Gemini)
- ✅ **Fixed API key handling** - Resolved issue with pre-loaded test keys in executable builds
- ✅ **Improved setup wizard** - Fixed provider switching and placeholder string consistency
- ✅ **Added .env.example template** - Better configuration management for new users
- ✅ **Cleaned up test suite** - Removed 1,000+ lines of deprecated Ollama-specific test code

### Supported AI Providers
- ✅ **Anthropic Claude** (recommended)
- ✅ **OpenAI GPT**
- ✅ **Google Gemini**

## 🗺️ Roadmap

- [ ] Voice input support
- [ ] Overlay mode (transparent window over games)
- [ ] Custom hotkeys for quick actions
- [ ] Game-specific plugins
- [ ] Multi-language support
- [ ] Mobile companion app
- [ ] Replay analysis
- [ ] Performance tracking

---

**Made with ❤️ for gamers by gamers**

*Happy Gaming! 🎮*
