# Setup Guide - Gaming AI Assistant

This guide will walk you through setting up the Gaming AI Assistant step by step.

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Installation](#installation)
3. [API Key Setup](#api-key-setup)
4. [First Run](#first-run)
5. [Troubleshooting](#troubleshooting)

## System Requirements

### Minimum Requirements
- **OS**: Windows 10/11, macOS 10.15+, or Linux (Ubuntu 20.04+)
- **Python**: 3.8 or higher
- **RAM**: 4GB minimum
- **Internet**: Required for AI API calls

### Recommended Requirements
- **Python**: 3.10 or higher
- **RAM**: 8GB or more
- **Internet**: Stable broadband connection

## Installation

### Step 1: Install Python

#### Windows
1. Download Python from [python.org](https://www.python.org/downloads/)
2. Run the installer
3. **IMPORTANT**: Check "Add Python to PATH"
4. Click "Install Now"

#### macOS
```bash
# Using Homebrew (recommended)
brew install python@3.11

# Or download from python.org
```

#### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
```

### Step 2: Clone or Download the Project

#### Using Git
```bash
git clone https://github.com/yourusername/gaming-ai-assistant.git
cd gaming-ai-assistant
```

#### Or Download ZIP
1. Download the ZIP file from GitHub
2. Extract to a folder
3. Open terminal/command prompt in that folder

### Step 3: Create Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate

# macOS/Linux:
source venv/bin/activate
```

### Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

#### Platform-Specific Notes

**Linux**: You may need additional packages:
```bash
# For PyQt6
sudo apt-get install python3-pyqt6

# For psutil
sudo apt-get install python3-dev
```

**macOS**: If you encounter issues with PyQt6:
```bash
brew install pyqt6
```

## API Key Setup

### Option 1: Anthropic (Claude) - Recommended

1. **Get API Key**
   - Go to [console.anthropic.com](https://console.anthropic.com/)
   - Sign up or log in
   - Navigate to API Keys
   - Create a new API key
   - Copy the key

2. **Configure Application**
   ```bash
   # Copy example file
   cp .env.example .env

   # Edit .env file
   # Windows: notepad .env
   # macOS/Linux: nano .env
   ```

3. **Add Your Key**
   ```env
   ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxxxxxxx
   AI_PROVIDER=anthropic
   ```

### Option 2: OpenAI (GPT)

1. **Get API Key**
   - Go to [platform.openai.com](https://platform.openai.com/)
   - Sign up or log in
   - Navigate to API Keys
   - Create a new API key
   - Copy the key

2. **Configure Application**
   ```env
   OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxx
   AI_PROVIDER=openai
   ```

### Cost Considerations

- **Anthropic Claude**: Pay-as-you-go, ~$0.003 per request
- **OpenAI GPT-4**: Pay-as-you-go, ~$0.01-0.03 per request

*Costs are approximate and based on typical usage*

## First Run

### Step 1: Verify Installation

```bash
# Check Python version
python --version

# Check pip installation
pip list
```

### Step 2: Test Configuration

```bash
# Test config file
python src/config.py
```

Expected output:
```
Configuration loaded successfully:
Config(provider=anthropic, hotkey=ctrl+shift+g)
API Key present: Yes
```

### Step 3: Test Game Detection

```bash
# Run game detector test
python src/game_detector.py
```

### Step 4: Launch the Application

```bash
python main.py
```

You should see:
```
============================================================
🎮 Gaming AI Assistant
============================================================

Loading configuration...
✓ Configuration loaded
  AI Provider: anthropic
  Hotkey: ctrl+shift+g

Initializing game detector...
✓ Game detector ready

Initializing AI assistant...
✓ AI assistant ready

Starting GUI...
```

## Troubleshooting

### "No module named 'PyQt6'"

**Solution**:
```bash
pip install PyQt6
```

On Linux:
```bash
sudo apt-get install python3-pyqt6
```

### "No API key found"

**Solution**:
1. Make sure `.env` file exists (not `.env.example`)
2. Check that the API key is correctly copied
3. Ensure no extra spaces or quotes around the key
4. Verify the `AI_PROVIDER` matches your key type

### "Game not detected"

**Solution**:
1. Make sure the game is actually running
2. Check the game is in the supported list
3. Try adding it manually to `src/game_detector.py`

Add to the `KNOWN_GAMES` dictionary:
```python
"yourgame.exe": "Your Game Name",
```

### GUI doesn't start on Linux

**Solution**:
```bash
# Install Qt dependencies
sudo apt-get install qt6-base-dev

# Or try with X11
export DISPLAY=:0
python main.py
```

### "ModuleNotFoundError: No module named 'src'"

**Solution**:
Make sure you're running from the project root directory:
```bash
cd /path/to/gaming-ai-assistant
python main.py
```

### High API Costs

**Solution**:
1. Be mindful of question length
2. Clear chat history regularly (uses less tokens)
3. Use Anthropic Claude (generally cheaper than GPT-4)
4. Set up billing alerts in your AI provider dashboard

## Advanced Configuration

### Custom Hotkey

Edit `.env`:
```env
OVERLAY_HOTKEY=ctrl+alt+g  # or any key combination
```

### Adjust Detection Interval

```env
CHECK_INTERVAL=10  # Check for games every 10 seconds instead of 5
```

### Custom Game Wikis

Edit `src/info_scraper.py` and add to `wiki_urls`:
```python
self.wiki_urls = {
    "Your Game": "https://custom-wiki-url.com/wiki/",
}
```

## Getting Help

### Documentation
- Main README: [README.md](README.md)
- This guide: [SETUP.md](SETUP.md)

### Common Issues
1. Check the [Troubleshooting](#troubleshooting) section above
2. Search existing GitHub issues
3. Create a new issue with:
   - Your OS and Python version
   - Complete error message
   - Steps to reproduce

### Community
- GitHub Issues: Report bugs or request features
- Discussions: Ask questions and share tips

## Next Steps

Once everything is working:

1. **Launch a game** - The assistant will auto-detect it
2. **Try the quick actions** - Click "Get Tips" or "Game Overview"
3. **Ask questions** - Type in the chat box
4. **Customize** - Edit configuration files to your liking
5. **Add more games** - Expand the supported games list

Happy Gaming! 🎮
