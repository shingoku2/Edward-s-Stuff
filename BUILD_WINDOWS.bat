@echo off
REM Gaming AI Assistant - Windows Executable Builder (Enhanced)
REM Run this on your Windows machine to create the .exe

echo ======================================================================
echo GAMING AI ASSISTANT - WINDOWS EXECUTABLE BUILDER
echo ======================================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo.
    echo SOLUTION:
    echo 1. Download Python from: https://www.python.org/downloads/
    echo 2. During installation, CHECK THE BOX: "Add Python to PATH"
    echo 3. After installation, restart Command Prompt and run this script again
    echo.
    pause
    exit /b 1
)

echo [✓] Python found
python --version
echo.

REM Check if pip is available
python -m pip --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: pip is not available
    echo.
    echo SOLUTION:
    echo Run this command:
    echo python -m ensurepip --upgrade
    echo.
    pause
    exit /b 1
)

echo [✓] pip found
python -m pip --version
echo.

echo [1/5] Installing dependencies...
echo This may take 2-3 minutes...
python -m pip install -r requirements.txt --quiet --upgrade
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    echo.
    echo SOLUTION:
    echo Try running manually:
    echo python -m pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)
echo    [✓] Dependencies installed

echo.
echo [2/5] Installing PyInstaller...
python -m pip install pyinstaller --quiet --upgrade
if errorlevel 1 (
    echo ERROR: Failed to install PyInstaller
    pause
    exit /b 1
)
echo    [✓] PyInstaller installed

echo.
echo [3/5] Cleaning previous builds...
if exist "build" rmdir /s /q "build" 2>nul
if exist "dist" rmdir /s /q "dist" 2>nul
if exist "*.spec" del /q "*.spec" 2>nul
echo    [✓] Cleaned build folders

echo.
echo [4/5] Building executable...
echo This will take 3-5 minutes. Please wait...
echo.

python -m PyInstaller --name=GamingAIAssistant ^
    --windowed ^
    --onedir ^
    --clean ^
    --noconfirm ^
    --paths=src ^
    --hidden-import=PyQt6.QtCore ^
    --hidden-import=PyQt6.QtGui ^
    --hidden-import=PyQt6.QtWidgets ^
    --hidden-import=PyQt6.QtWebEngineCore ^
    --hidden-import=PyQt6.QtWebEngineWidgets ^
    --hidden-import=config ^
    --hidden-import=game_detector ^
    --hidden-import=ai_assistant ^
    --hidden-import=info_scraper ^
    --hidden-import=gui ^
    --hidden-import=credential_store ^
    --hidden-import=provider_tester ^
    --hidden-import=providers ^
    --hidden-import=ai_router ^
    --hidden-import=setup_wizard ^
    --hidden-import=providers_tab ^
    --hidden-import=settings_dialog ^
    --hidden-import=settings_tabs ^
    --hidden-import=appearance_tabs ^
    --hidden-import=login_dialog ^
    --hidden-import=keybind_manager ^
    --hidden-import=macro_manager ^
    --hidden-import=theme_manager ^
    --hidden-import=game_profile ^
    --hidden-import=game_profiles_tab ^
    --hidden-import=game_watcher ^
    --hidden-import=overlay_modes ^
    --hidden-import=macro_store ^
    --hidden-import=macro_runner ^
    --hidden-import=macro_ai_generator ^
    --hidden-import=knowledge_pack ^
    --hidden-import=knowledge_store ^
    --hidden-import=knowledge_index ^
    --hidden-import=knowledge_ingestion ^
    --hidden-import=knowledge_integration ^
    --hidden-import=knowledge_packs_tab ^
    --hidden-import=session_logger ^
    --hidden-import=session_coaching ^
    --hidden-import=session_recap_dialog ^
    --hidden-import=anthropic ^
    --hidden-import=openai ^
    --hidden-import=google.generativeai ^
    --hidden-import=psutil ^
    --hidden-import=requests ^
    --hidden-import=bs4 ^
    --hidden-import=dotenv ^
    --hidden-import=cryptography ^
    --hidden-import=keyring ^
    --hidden-import=pynput ^
    main.py

if errorlevel 1 (
    echo.
    echo ERROR: Build failed
    echo.
    echo TROUBLESHOOTING:
    echo 1. Make sure all dependencies are installed
    echo 2. Check if antivirus is blocking PyInstaller
    echo 3. Try running as Administrator
    echo 4. Check the error messages above
    echo.
    pause
    exit /b 1
)

echo.
echo    [✓] Build completed successfully!

echo.
echo [5/5] Creating distribution package...

REM Copy additional files
if not exist "dist\GamingAIAssistant" (
    echo ERROR: dist\GamingAIAssistant folder not found
    pause
    exit /b 1
)

copy ".env.example" "dist\GamingAIAssistant\.env.example" >nul 2>&1
copy "README.md" "dist\GamingAIAssistant\README.md" >nul 2>&1
copy "SETUP.md" "dist\GamingAIAssistant\SETUP.md" >nul 2>&1
copy "TEST_REPORT.md" "dist\GamingAIAssistant\TEST_REPORT.md" >nul 2>&1
copy "WINDOWS_RELEASE_README.md" "dist\GamingAIAssistant\WINDOWS_README.md" >nul 2>&1

REM Create quick start instructions
(
echo =====================================================
echo GAMING AI ASSISTANT - QUICK START
echo =====================================================
echo.
echo STEP 1: First Run - Setup Wizard
echo --------------------------------
echo 1. Double-click: GamingAIAssistant.exe
echo 2. The Setup Wizard will appear automatically
echo 3. Select your preferred AI provider (Anthropic, OpenAI, or Gemini)
echo 4. Enter your API key securely (stored encrypted, NOT in .env)
echo.
echo You can get API keys from:
echo - Anthropic: https://console.anthropic.com/
echo - OpenAI: https://platform.openai.com/api-keys
echo - Gemini: https://aistudio.google.com/app/apikey
echo.
echo STEP 2: Use While Gaming
echo ------------------------
echo 1. Launch any supported game
echo 2. Press Ctrl+Shift+G to open the AI assistant
echo 3. Ask questions about the game!
echo.
echo SUPPORTED GAMES (37+):
echo - League of Legends, VALORANT, Dota 2
echo - Minecraft, World of Warcraft, Final Fantasy XIV
echo - Elden Ring, Dark Souls 3, Skyrim, Cyberpunk 2077
echo - CS2, Fortnite, Apex Legends, Rocket League
echo - And many more!
echo.
echo For detailed setup, see SETUP.md
echo.
echo =====================================================
) > "dist\GamingAIAssistant\START_HERE.txt"

echo    [✓] Files copied to dist folder

echo.
echo ======================================================================
echo BUILD COMPLETE! SUCCESS!
echo ======================================================================
echo.
echo Your executable is ready at:
echo    dist\GamingAIAssistant\GamingAIAssistant.exe
echo.
echo File size: ~150-200 MB (includes all dependencies)
echo.
echo NEXT STEPS:
echo -----------
echo 1. Test the .exe by double-clicking it
echo    - The Setup Wizard will launch automatically on first run
echo    - Your API keys will be stored securely in encrypted CredentialStore
echo.
echo 2. To distribute:
echo    - Zip the entire "dist\GamingAIAssistant" folder
echo    - Share with friends/users
echo    - They extract and run GamingAIAssistant.exe
echo    - Each user runs the Setup Wizard with their own API keys
echo.
echo SECURITY: API keys are stored encrypted in CredentialStore, NOT in .env files!
echo.
echo ======================================================================
echo.
pause
