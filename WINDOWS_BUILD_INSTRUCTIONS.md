# How to Create Windows Executable (.exe)

This guide shows you how to build the Gaming AI Assistant into a standalone Windows executable.

---

## Option 1: Automated Build (Recommended)

### Requirements:
- Windows 10/11
- Python 3.8 or higher installed
- Internet connection

### Steps:

1. **Download this project folder to your Windows PC**
   - Copy the entire `Edward-s-Stuff` folder to your Windows machine

2. **Open Command Prompt**
   - Press `Win + R`
   - Type `cmd` and press Enter

3. **Navigate to the project folder**
   ```cmd
   cd path\to\Edward-s-Stuff
   ```

4. **Run the build script**
   ```cmd
   BUILD_WINDOWS.bat
   ```

5. **Wait 3-5 minutes** for the build to complete

6. **Your executable will be at:**
   ```
   dist\GamingAIAssistant\GamingAIAssistant.exe
   ```

---

## Option 2: Manual Build

If the batch file doesn't work, follow these manual steps:

### Step 1: Install Dependencies
```cmd
pip install -r requirements.txt
pip install pyinstaller
```

### Step 2: Build the Executable
```cmd
python -m PyInstaller --name=GamingAIAssistant --windowed --onedir --clean --noconfirm --paths=src --add-data=".env.example;." --add-data="README.md;." --hidden-import=PyQt6.QtCore --hidden-import=PyQt6.QtGui --hidden-import=PyQt6.QtWidgets --hidden-import=config --hidden-import=game_detector --hidden-import=ai_assistant --hidden-import=info_scraper --hidden-import=gui --hidden-import=anthropic --hidden-import=openai --hidden-import=psutil --hidden-import=requests --hidden-import=bs4 --hidden-import=dotenv main.py
```

### Step 3: Copy Additional Files
```cmd
copy .env.example dist\GamingAIAssistant\.env.example
copy README.md dist\GamingAIAssistant\README.md
copy SETUP.md dist\GamingAIAssistant\SETUP.md
```

---

## Option 3: Single-File Executable

For a single .exe file (larger but more portable):

```cmd
python -m PyInstaller --name=GamingAIAssistant --windowed --onefile --clean --noconfirm --paths=src --add-data=".env.example;." --hidden-import=PyQt6.QtCore --hidden-import=PyQt6.QtGui --hidden-import=PyQt6.QtWidgets --hidden-import=config --hidden-import=game_detector --hidden-import=ai_assistant --hidden-import=info_scraper --hidden-import=gui --hidden-import=anthropic --hidden-import=openai --hidden-import=psutil --hidden-import=bs4 --hidden-import=dotenv main.py
```

**Note:** Single-file builds are slower to start but easier to distribute.

---

## After Building

### Your executable location:
- **Folder build**: `dist\GamingAIAssistant\GamingAIAssistant.exe`
- **Single file**: `dist\GamingAIAssistant.exe`

### To distribute to other Windows PCs:

1. **For folder build:**
   - Zip the entire `dist\GamingAIAssistant` folder
   - Send the zip file
   - Recipients extract and run `GamingAIAssistant.exe`

2. **For single-file build:**
   - Just send the `GamingAIAssistant.exe` file
   - Recipients need to create a `.env` file with their API key

---

## Setting Up the Executable

After building, users need to:

1. **Create .env file** (if using folder build):
   - Copy `.env.example` to `.env`
   - Edit `.env` and add Anthropic API key:
     ```
     ANTHROPIC_API_KEY=your_actual_key_here
     AI_PROVIDER=anthropic
     ```

2. **Run GamingAIAssistant.exe**

3. **Launch a game**

4. **Press Ctrl+Shift+G** to open the assistant

---

## Troubleshooting

### "Python is not recognized"
- Install Python from https://www.python.org/downloads/
- Check "Add Python to PATH" during installation

### "PyInstaller failed"
- Make sure all dependencies are installed: `pip install -r requirements.txt`
- Try running as Administrator

### "ModuleNotFoundError during build"
- Install the missing module: `pip install [module-name]`
- Re-run the build

### ".exe doesn't start"
- Check if antivirus is blocking it
- Run from command prompt to see error messages:
  ```cmd
  dist\GamingAIAssistant\GamingAIAssistant.exe
  ```

### "libEGL.so.1 error" or similar
- This only happens on Linux. Build on Windows for Windows.

---

## File Size

The executable folder will be approximately:
- **Folder build**: 150-200 MB (includes all dependencies)
- **Single file**: 80-120 MB (compressed)

This is normal for PyQt6 applications.

---

## Notes

- The .exe is only for Windows
- Mac users need to build on Mac with PyInstaller
- Linux users can run the Python script directly
- The executable includes all Python dependencies
- No Python installation needed on target machines

---

## Distribution Checklist

When sharing your executable:

- [ ] Built the executable successfully
- [ ] Tested it runs on your Windows machine
- [ ] Included .env.example file
- [ ] Included README.md with instructions
- [ ] Created START_HERE.txt with quick setup
- [ ] Zipped the dist folder
- [ ] Tested unzipping and running on another PC

---

## Security Note

**DO NOT include your .env file with your API key in the distribution!**

Only include `.env.example`. Users must add their own API keys.

---

For questions or issues, see the main README.md file.
