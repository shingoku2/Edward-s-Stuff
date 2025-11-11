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

python -m PyInstaller --name=GamingAIAssistant --windowed --onedir --clean --noconfirm --paths=src --add-data=".env.example;." --add-data="README.md;." --add-data="SETUP.md;." --hidden-import=PyQt6.QtCore --hidden-import=PyQt6.QtGui --hidden-import=PyQt6.QtWidgets --hidden-import=config --hidden-import=game_detector --hidden-import=ai_assistant --hidden-import=info_scraper --hidden-import=gui --hidden-import=anthropic --hidden-import=openai --hidden-import=psutil --hidden-import=requests --hidden-import=bs4 --hidden-import=dotenv main.py

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
echo Don't forget to:
echo 1. Copy .env.example to .env
echo 2. Add your Anthropic API key to .env
echo 3. Run GamingAIAssistant.exe
echo.
pause
