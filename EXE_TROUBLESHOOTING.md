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

### Issue 1: "No API key found" or Setup Wizard Errors

**Problem:** The application can't find your API key.

**Fix:**
The Setup Wizard should launch automatically on first run:
1. Select your AI provider (Anthropic Claude, OpenAI, or Google Gemini)
2. Enter your API key securely
3. Your key will be encrypted and stored in CredentialStore (NOT in .env)

If the Setup Wizard doesn't appear:
1. Go to Settings → Providers
2. Enter your API key there
3. The application will save it securely

**Note:** API keys are NO LONGER stored in .env files for security reasons!

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

1. **Check your API key in Settings:**
   - Go to Settings → Providers
   - Make sure you've entered your API key
   - Select it as the default provider

2. **Make sure the API key is valid:**
   - Visit the appropriate provider:
     - Anthropic: https://console.anthropic.com/
     - OpenAI: https://platform.openai.com/api-keys
     - Gemini: https://aistudio.google.com/app/apikey
   - Check if your key is still active
   - Check if you have credits

3. **Test the API key:**
   - Run api_key_test.py before building
   - It will verify your API key works

---

## Pre-Build Testing

**Before building the .exe, run these tests:**

### Test 1: Component Test
```cmd
python test_before_build.py
```

This checks:
- All modules import correctly
- Dependencies are installed
- Basic configuration is valid

### Test 2: API Key Test
```cmd
python api_key_test.py
```

This tests your API key connections to providers.

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

- [ ] Test the .exe:
  ```cmd
  dist\GamingAIAssistant\GamingAIAssistant.exe
  ```

- [ ] Setup Wizard will launch on first run - enter your API key there

**Note:** API keys are no longer copied to dist folder - they're stored securely by the application!

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

2. **Check these:**
   - requirements.txt (all dependencies installed?)
   - Python version (3.8+ required)
   - API key configured in Setup Wizard or Settings

3. **Common error patterns:**

   **Error:** "ImportError: DLL load failed"
   **Fix:** Install Visual C++ Redistributables

   **Error:** "ValueError: API key not found"
   **Fix:** Run the .exe to launch the Setup Wizard and enter your key

   **Error:** "ModuleNotFoundError: config"
   **Fix:** Rebuild with --paths=src flag

---

## Still Not Working?

Try building a simple test version:

```cmd
python -m PyInstaller --name=Test --console --onefile api_key_test.py
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
│       ├── .env.example             ← Template
│       └── [other files...]
├── BUILD_WINDOWS.bat
├── BUILD_DEBUG.bat
└── main.py
```

---

**Remember:** The .exe no longer needs the .env file! API keys are configured securely through the Setup Wizard on first run.
