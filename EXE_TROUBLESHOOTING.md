# EXE Not Running - Troubleshooting Guide

If your .exe does nothing when you run it, follow this guide to diagnose and fix the issue.

---

## Quick Diagnosis

### Step 1: Run the DEBUG Version

The normal .exe is built with `--windowed` which hides the console, so you can't see errors.

**Build and run the DEBUG version:**

```cmd
BUILD_DEBUG.bat
```

This creates: `dist\GamingAIAssistant_DEBUG\GamingAIAssistant_DEBUG.exe`

**Run it** - you'll see a console window with error messages!

---

## Common Issues and Fixes

### Issue 1: "No .env file found" or "API key not found"

**Problem:** The .exe can't find your .env file with the API key.

**Fix:**
1. Make sure `.env` file is in the same folder as the .exe
2. Copy your .env file to the dist folder:
   ```cmd
   copy .env dist\GamingAIAssistant\.env
   ```

**For distribution:** Put .env next to GamingAIAssistant.exe:
```
GamingAIAssistant\
├── GamingAIAssistant.exe
├── .env                    ← Your API key file
├── _internal\              ← Libraries
└── other files...
```

---

### Issue 2: "ModuleNotFoundError"

**Problem:** Python can't find the src modules (config, game_detector, etc.)

**Fix:** Rebuild with the correct command that includes `--paths=src` and all hidden imports.

Use the updated BUILD_WINDOWS.bat or BUILD_SIMPLE.bat

---

### Issue 3: DLL Errors or PyQt6 Errors

**Problem:** Missing system libraries or PyQt6 dependencies

**Symptoms:**
- "DLL not found"
- "Qt platform plugin" errors
- Application starts then immediately closes

**Fix:**

1. **Make sure you have Microsoft Visual C++ Redistributables:**
   - Download from: https://aka.ms/vs/17/release/vc_redist.x64.exe
   - Install it

2. **Try installing PyQt6 system dependencies:**
   ```cmd
   python -m pip install --upgrade PyQt6
   ```

3. **Rebuild with all dependencies:**
   ```cmd
   BUILD_WINDOWS.bat
   ```

---

### Issue 4: Nothing Happens at All

**Problem:** .exe doesn't start, no error, no window

**Debugging steps:**

1. **Check if it's running in Task Manager:**
   - Press Ctrl+Shift+Esc
   - Look for "GamingAIAssistant.exe"
   - If it's there but no window, it might be crashing immediately

2. **Run from Command Prompt to see errors:**
   ```cmd
   cd dist\GamingAIAssistant
   GamingAIAssistant.exe
   ```

3. **Check Windows Event Viewer:**
   - Press Win+R, type `eventvwr`
   - Go to Windows Logs → Application
   - Look for errors from your application

4. **Disable antivirus temporarily:**
   - Some antivirus software blocks PyInstaller .exe files
   - Try adding an exception

---

### Issue 5: "API Error" or "Permission Denied"

**Problem:** The app starts but AI doesn't work

**Fix:**

1. **Check your API key in .env:**
   ```
   ANTHROPIC_API_KEY=sk-ant-api03-your-actual-key-here
   AI_PROVIDER=anthropic
   ```

2. **Make sure the API key is valid:**
   - Visit: https://console.anthropic.com/
   - Check if your key is still active
   - Check if you have credits

3. **Test the API key:**
   - Run test_minimal.py before building
   - It will verify your API key works

---

## Pre-Build Testing

**Before building the .exe, run these tests:**

### Test 1: Component Test
```cmd
python test_before_build.py
```

This checks:
- .env file exists
- API keys are configured
- All modules import correctly
- Dependencies are installed

### Test 2: Minimal Test
```cmd
python test_minimal.py
```

This tests the core functionality without GUI.

### Test 3: Run from Python
```cmd
python main.py
```

If this works, the .exe should work too (once built correctly).

---

## Rebuild Checklist

If the .exe doesn't work, try rebuilding with this checklist:

- [ ] Delete old build folders:
  ```cmd
  rmdir /s /q dist
  rmdir /s /q build
  ```

- [ ] Make sure .env file exists with valid API key

- [ ] Run pre-build test:
  ```cmd
  python test_before_build.py
  ```

- [ ] Use the correct build script:
  ```cmd
  BUILD_WINDOWS.bat
  ```
  (or BUILD_DEBUG.bat for debugging)

- [ ] Wait for build to complete (3-5 minutes)

- [ ] Copy .env to the dist folder:
  ```cmd
  copy .env dist\GamingAIAssistant\.env
  ```

- [ ] Test the .exe:
  ```cmd
  dist\GamingAIAssistant\GamingAIAssistant.exe
  ```

---

## Build Scripts Available

| Script | Purpose | When to Use |
|--------|---------|-------------|
| BUILD_WINDOWS.bat | Normal build (no console) | Final distribution |
| BUILD_DEBUG.bat | Debug build (shows console) | Troubleshooting errors |
| BUILD_SIMPLE.bat | Simplified build | If BUILD_WINDOWS.bat fails |

---

## Getting Help

If none of these fix your issue:

1. **Run the DEBUG build** and copy the error message

2. **Check these files:**
   - .env (is it in the right place?)
   - requirements.txt (all dependencies installed?)
   - Python version (3.8+ required)

3. **Common error patterns:**

   **Error:** "ImportError: DLL load failed"
   **Fix:** Install Visual C++ Redistributables

   **Error:** "FileNotFoundError: .env"
   **Fix:** Copy .env to same folder as .exe

   **Error:** "ValueError: API key not found"
   **Fix:** Check .env file has correct API key

   **Error:** "ModuleNotFoundError: config"
   **Fix:** Rebuild with --paths=src flag

---

## Still Not Working?

Try building a simple test version:

```cmd
python -m PyInstaller --name=Test --console --onefile test_minimal.py
```

Run: `dist\Test.exe`

If this works, the issue is with the main app. If this fails, the issue is with your Python/PyInstaller setup.

---

## File Locations Reference

**After building, you should have:**

```
Edward-s-Stuff/
├── dist/
│   └── GamingAIAssistant/
│       ├── GamingAIAssistant.exe    ← The application
│       ├── .env                      ← Copy this here!
│       ├── _internal/                ← Dependencies (auto-created)
│       ├── README.md
│       └── other files...
├── .env                              ← Your original (DON'T distribute this)
├── .env.example                      ← Template
├── BUILD_WINDOWS.bat
├── BUILD_DEBUG.bat
└── main.py
```

---

**Remember:** The .exe needs the .env file in the same directory to work!
