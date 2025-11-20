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
echo Using GamingAIAssistant.spec for build configuration...
echo Please wait...
echo.

python -m PyInstaller GamingAIAssistant.spec --clean --noconfirm

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
