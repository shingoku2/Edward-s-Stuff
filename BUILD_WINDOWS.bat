@echo off
REM Gaming AI Assistant - Windows Executable Builder
REM Run this on your Windows machine to create the .exe

echo ======================================================================
echo GAMING AI ASSISTANT - WINDOWS EXECUTABLE BUILDER
echo ======================================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [1/5] Installing dependencies...
pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo    - Dependencies installed

echo.
echo [2/5] Installing PyInstaller...
pip install pyinstaller --quiet
if errorlevel 1 (
    echo ERROR: Failed to install PyInstaller
    pause
    exit /b 1
)
echo    - PyInstaller installed

echo.
echo [3/5] Cleaning previous builds...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "*.spec" del /q "*.spec"
echo    - Cleaned build folders

echo.
echo [4/5] Building executable (this may take 3-5 minutes)...
pyinstaller --name=GamingAIAssistant ^
    --windowed ^
    --onedir ^
    --clean ^
    --noconfirm ^
    --add-data=".env.example;." ^
    --add-data="README.md;." ^
    --add-data="SETUP.md;." ^
    --hidden-import=PyQt6.QtCore ^
    --hidden-import=PyQt6.QtGui ^
    --hidden-import=PyQt6.QtWidgets ^
    --hidden-import=anthropic ^
    --hidden-import=openai ^
    --hidden-import=psutil ^
    --hidden-import=requests ^
    --hidden-import=bs4 ^
    --hidden-import=dotenv ^
    main.py

if errorlevel 1 (
    echo ERROR: Build failed
    pause
    exit /b 1
)
echo    - Build completed successfully!

echo.
echo [5/5] Creating distribution package...

REM Copy additional files
copy ".env.example" "dist\GamingAIAssistant\.env.example" >nul 2>&1
copy "README.md" "dist\GamingAIAssistant\README.md" >nul 2>&1
copy "SETUP.md" "dist\GamingAIAssistant\SETUP.md" >nul 2>&1
copy "TEST_REPORT.md" "dist\GamingAIAssistant\TEST_REPORT.md" >nul 2>&1

REM Create quick start instructions
(
echo GAMING AI ASSISTANT - QUICK START
echo ==================================
echo.
echo 1. SETUP API KEY:
echo    - Copy ".env.example" to ".env"
echo    - Edit .env and add your Anthropic API key
echo    - Get key from: https://console.anthropic.com/
echo.
echo 2. RUN THE APPLICATION:
echo    - Double-click GamingAIAssistant.exe
echo    - Launch a game ^(League of Legends, Minecraft, etc.^)
echo    - Press Ctrl+Shift+G to open the assistant
echo.
echo 3. SUPPORTED GAMES:
echo    - League of Legends, VALORANT, Dota 2
echo    - Minecraft, World of Warcraft, Final Fantasy XIV
echo    - Elden Ring, Dark Souls 3, Skyrim, Cyberpunk 2077
echo    - CS2, Fortnite, Apex Legends, Rocket League
echo    - And 23 more!
echo.
echo For detailed setup, see SETUP.md
) > "dist\GamingAIAssistant\START_HERE.txt"

echo    - Files copied to dist folder

echo.
echo ======================================================================
echo BUILD COMPLETE!
echo ======================================================================
echo.
echo Your executable is ready at:
echo    dist\GamingAIAssistant\GamingAIAssistant.exe
echo.
echo To distribute:
echo    1. Zip the entire "dist\GamingAIAssistant" folder
echo    2. Extract on any Windows PC
echo    3. Add API key to .env file
echo    4. Run GamingAIAssistant.exe
echo.
echo ======================================================================
pause
