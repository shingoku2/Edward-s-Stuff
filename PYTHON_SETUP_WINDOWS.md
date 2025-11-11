# Python Setup for Windows - Quick Guide

If you got the error "pip is not recognized", follow this guide.

---

## Install Python on Windows

### Step 1: Download Python

1. Go to: **https://www.python.org/downloads/**
2. Click the big yellow button: **"Download Python 3.x.x"**
3. Save the installer file

### Step 2: Run the Installer

**CRITICAL:** Before clicking anything else:

1. ✅ **CHECK THE BOX:** "Add Python to PATH" (at the bottom)
2. ✅ This is the most important step!

![Python Installer - Check "Add Python to PATH"]

Then click: **"Install Now"**

### Step 3: Verify Installation

After installation completes:

1. **Open Command Prompt**
   - Press `Win + R`
   - Type `cmd` and press Enter

2. **Check Python version:**
   ```cmd
   python --version
   ```

   Should show: `Python 3.x.x`

3. **Check pip:**
   ```cmd
   python -m pip --version
   ```

   Should show: `pip xx.x.x from ...`

If both commands work, you're ready to build!

---

## If Python is Already Installed But Not in PATH

### Option 1: Reinstall Python (Easiest)

1. Uninstall Python from Control Panel
2. Download and reinstall, checking "Add Python to PATH"

### Option 2: Add Python to PATH Manually

1. Find where Python is installed (usually `C:\Python3x\` or `C:\Users\YourName\AppData\Local\Programs\Python\Python3x\`)

2. **Add to PATH:**
   - Right-click "This PC" → Properties
   - Click "Advanced system settings"
   - Click "Environment Variables"
   - Under "System variables", find "Path"
   - Click "Edit"
   - Click "New"
   - Add these two paths:
     ```
     C:\Python3x\
     C:\Python3x\Scripts\
     ```
     (Replace `Python3x` with your actual Python folder)

3. **Restart Command Prompt** and test again

---

## After Python is Working

Run the build script:

```cmd
BUILD_WINDOWS.bat
```

It will now work! The script:
- ✅ Checks if Python is installed
- ✅ Checks if pip is available
- ✅ Installs all dependencies automatically
- ✅ Builds the .exe file
- ✅ Creates distribution package

---

## Alternative: Manual Command-by-Command Build

If the batch file still has issues, run these commands one by one:

```cmd
REM Navigate to project folder
cd path\to\Edward-s-Stuff

REM Install dependencies
python -m pip install -r requirements.txt

REM Install PyInstaller
python -m pip install pyinstaller

REM Build the executable
python -m PyInstaller --name=GamingAIAssistant --windowed --onedir --paths=src --add-data=".env.example;." --hidden-import=PyQt6.QtCore --hidden-import=PyQt6.QtGui --hidden-import=PyQt6.QtWidgets --hidden-import=config --hidden-import=game_detector --hidden-import=ai_assistant --hidden-import=info_scraper --hidden-import=gui --hidden-import=anthropic --hidden-import=openai --hidden-import=psutil --hidden-import=bs4 --hidden-import=dotenv main.py

REM Your .exe will be at: dist\GamingAIAssistant\GamingAIAssistant.exe
```

---

## Common Issues

### "python is not recognized"
- Python not installed or not in PATH
- Follow the installation guide above

### "Microsoft Store opens when I type 'python'"
- Windows redirecting to Store
- Install actual Python from python.org
- Or disable the redirect in Windows Settings → Apps → App execution aliases

### "pip install fails with permission error"
- Run Command Prompt as Administrator
- Right-click Command Prompt → "Run as administrator"

### "pyinstaller command not found"
- Use `python -m PyInstaller` instead of just `pyinstaller`
- Or add Python Scripts folder to PATH

---

## Quick Test

Once Python is installed correctly, test with:

```cmd
python -c "print('Python works!')"
python -m pip list
```

Both should work without errors.

Then run: **BUILD_WINDOWS.bat**

---

## Need More Help?

Check these resources:
- Python Installation: https://docs.python.org/3/using/windows.html
- PyInstaller Docs: https://pyinstaller.org/
- PATH Setup: https://www.java.com/en/download/help/path.html

Or contact the developer for support.

---

**Summary:**
1. Install Python from python.org
2. ✅ CHECK "Add Python to PATH" during install
3. Restart Command Prompt
4. Run BUILD_WINDOWS.bat
5. Done!
