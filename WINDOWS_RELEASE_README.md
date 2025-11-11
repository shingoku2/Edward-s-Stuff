# Gaming AI Assistant - Windows Release

**Your AI Gaming Companion** 🎮

Automatically detects your game and provides real-time AI assistance using Claude AI.

---

## 📥 Installation (For Users)

### If you received a pre-built executable:

1. **Extract the zip file**
   - Extract `GamingAIAssistant.zip` to any folder

2. **Setup API Key**
   - Copy `.env.example` to `.env`
   - Open `.env` in Notepad
   - Get an API key from: https://console.anthropic.com/
   - Paste your key:
     ```
     ANTHROPIC_API_KEY=sk-ant-api03-your-key-here
     ```

3. **Run the application**
   - Double-click `GamingAIAssistant.exe`
   - The app will start in the system tray

4. **Play your game**
   - Launch any supported game
   - Press **Ctrl+Shift+G** to open the AI assistant

---

## 🎮 Supported Games (37+)

**MOBAs & Shooters:**
- League of Legends
- VALORANT
- Dota 2
- Counter-Strike 2
- Overwatch
- Apex Legends
- Fortnite

**RPGs:**
- Elden Ring
- Dark Souls 3
- Skyrim Special Edition
- The Witcher 3
- Cyberpunk 2077
- Fallout 4

**MMOs:**
- World of Warcraft
- Final Fantasy XIV
- Elder Scrolls Online
- Guild Wars 2

**Others:**
- Minecraft
- Rocket League
- Grand Theft Auto V
- Red Dead Redemption 2
- Palworld
- Helldivers 2

...and more!

---

## 🚀 How to Use

1. **Launch the app** - Double-click `GamingAIAssistant.exe`

2. **Start your game** - The app auto-detects when you launch a supported game

3. **Press Ctrl+Shift+G** - Opens the AI assistant overlay

4. **Ask questions** like:
   - "What are the best beginner tips?"
   - "How do I beat this boss?"
   - "What's the current meta?"
   - "Explain this game mechanic"
   - "Best character builds?"

5. **Get instant AI responses** from Claude!

---

## ⚙️ Features

✅ **Auto Game Detection** - Automatically knows what you're playing
✅ **Real-Time AI Assistance** - Powered by Claude (Anthropic)
✅ **Game-Specific Knowledge** - Context-aware responses
✅ **Web Scraping** - Pulls info from wikis and forums
✅ **Dark Theme GUI** - Easy on the eyes
✅ **System Tray** - Runs in background
✅ **Hotkey Access** - Ctrl+Shift+G anytime
✅ **Conversation History** - Remembers context

---

## 🔧 Requirements

- **Windows 10 or 11**
- **Anthropic API Key** (free tier available)
- **Internet connection** (for AI queries)

### Getting an API Key:

1. Visit: https://console.anthropic.com/
2. Create a free account
3. Navigate to API Keys section
4. Click "Create Key"
5. Copy your key to the `.env` file

**Cost:** Claude Haiku is very affordable (~$0.25 per 1M input tokens)

---

## 📁 File Structure

```
GamingAIAssistant/
├── GamingAIAssistant.exe    # Main application
├── .env.example              # API key template
├── START_HERE.txt            # Quick start guide
├── README.md                 # Full documentation
├── SETUP.md                  # Detailed setup guide
└── [library files]           # Python dependencies
```

---

## 🐛 Troubleshooting

### App won't start
- Check if antivirus blocked it
- Run as Administrator
- Ensure .env file has valid API key

### Game not detected
- Check if game is in the supported list
- Game must be running
- Try restarting the app

### AI not responding
- Verify API key in .env file
- Check internet connection
- Ensure Anthropic account has credits

### Hotkey not working
- Check if another app uses Ctrl+Shift+G
- Try clicking the system tray icon instead
- Restart the app

---

## 💰 API Usage & Costs

### Claude Haiku Pricing:
- **Input**: $0.25 per 1M tokens (~750,000 words)
- **Output**: $1.25 per 1M tokens

### Typical Usage:
- **1 question**: ~200-500 tokens ($0.0001 - $0.0003)
- **100 questions**: ~$0.01 - $0.03
- **Very affordable** for personal use!

### Free Tier:
Anthropic offers $5 in free credits for new users.

---

## 🔒 Privacy & Security

- **Your API key is stored locally** in the .env file
- **No data is sent** to anyone except Anthropic
- **Conversation history** is stored in memory only
- **No telemetry or tracking**
- **Open source** - check the code on GitHub

---

## 🎯 Tips for Best Experience

1. **Be specific** in your questions
   - Good: "What are the best ADC champions in League?"
   - Better: "What are the top 3 ADC champions for beginners in current meta?"

2. **Provide context** when needed
   - "I'm playing Elden Ring and stuck at Margit, any tips?"

3. **Use follow-up questions**
   - The AI remembers conversation context

4. **Ask for builds**
   - "Show me a tanky build for Skyrim"

5. **Request strategies**
   - "How do I farm efficiently in Minecraft?"

---

## 🔄 Updates

To check for updates:
1. Visit the GitHub repository
2. Download the latest release
3. Replace the old files with new ones
4. Keep your `.env` file with your API key

---

## 📝 License

MIT License - Free to use and modify

---

## 🙏 Credits

- **AI Provider**: Anthropic (Claude)
- **GUI Framework**: PyQt6
- **Game Detection**: psutil
- **Web Scraping**: BeautifulSoup4

---

## 📧 Support

For issues or questions:
- Check TROUBLESHOOTING section above
- Review SETUP.md for detailed setup
- Visit the GitHub repository for updates

---

## 🎮 Happy Gaming!

Enjoy your AI-powered gaming companion!

Press **Ctrl+Shift+G** anytime in-game for instant assistance.

---

**Version**: 1.0.0
**Built with**: Python, PyQt6, Claude AI
**Status**: Production Ready ✅
