@echo off
REM Simple Gaming AI Assistant Builder
REM This version checks Python first

echo ====================================
echo Gaming AI Assistant - Simple Builder
echo ====================================
echo.

REM Test Python
echo Testing Python installation...
python --version
if errorlevel 1 (
    echo.
    echo ERROR: Python not found!
    echo.
    echo Please install Python from: https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

echo OK - Python is working
echo.

REM Test pip
echo Testing pip...
python -m pip --version
if errorlevel 1 (
    echo.
    echo ERROR: pip not found!
    echo Try: python -m ensurepip --upgrade
    echo.
    pause
    exit /b 1
)

echo OK - pip is working
echo.
echo ====================================
echo Starting build process...
echo ====================================
echo.

REM Clean old builds
echo Cleaning old builds...
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"
echo Done.
echo.

REM Install dependencies
echo Installing dependencies (this takes 2-3 minutes)...
python -m pip install -r requirements.txt --quiet --upgrade
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo Done.
echo.

REM Install PyInstaller
echo Installing PyInstaller...
python -m pip install pyinstaller --quiet --upgrade
if errorlevel 1 (
    echo ERROR: Failed to install PyInstaller
    pause
    exit /b 1
)
echo Done.
echo.

REM Build
echo Building executable (this takes 3-5 minutes)...
echo Please wait...
echo.

python -m PyInstaller ^
    --name=GamingAIAssistant ^
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
    echo ERROR: Build failed!
    echo Check the error messages above.
    pause
    exit /b 1
)

echo.
echo ====================================
echo BUILD SUCCESSFUL!
echo ====================================
echo.
echo Your .exe is at: dist\GamingAIAssistant\GamingAIAssistant.exe
echo.
echo NEXT STEPS:
echo 1. Run GamingAIAssistant.exe
echo    - The Setup Wizard will launch automatically on first run
echo    - Select your AI provider (Anthropic, OpenAI, or Gemini)
echo    - Enter your API key securely (stored encrypted in CredentialStore)
echo.
echo 2. Your API keys are stored securely - NOT in .env files!
echo.
echo Get your API key from:
echo   - Anthropic: https://console.anthropic.com/
echo   - OpenAI: https://platform.openai.com/api-keys
echo   - Gemini: https://aistudio.google.com/app/apikey
echo.
pause
