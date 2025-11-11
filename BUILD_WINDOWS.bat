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
    --add-data=".env.example;." ^
    --add-data="README.md;." ^
    --add-data="SETUP.md;." ^
    --hidden-import=PyQt6.QtCore ^
    --hidden-import=PyQt6.QtGui ^
    --hidden-import=PyQt6.QtWidgets ^
    --hidden-import=config ^
    --hidden-import=game_detector ^
    --hidden-import=ai_assistant ^
    --hidden-import=info_scraper ^
    --hidden-import=gui ^
    --hidden-import=anthropic ^
    --hidden-import=openai ^
    --hidden-import=psutil ^
    --hidden-import=requests ^
    --hidden-import=bs4 ^
    --hidden-import=dotenv ^
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
echo STEP 1: Setup API Key
echo ---------------------
echo 1. Copy ".env.example" to ".env"
echo 2. Edit .env in Notepad
echo 3. Get API key from: https://console.anthropic.com/
echo 4. Replace "your_anthropic_api_key_here" with your actual key
echo.
echo STEP 2: Run the Application
echo ---------------------------
echo Double-click: GamingAIAssistant.exe
echo.
echo STEP 3: Use While Gaming
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
echo 2. Make sure to add your API key to .env file
echo 3. To distribute:
echo    - Zip the entire "dist\GamingAIAssistant" folder
echo    - Share with friends/users
echo    - They extract and run GamingAIAssistant.exe
echo.
echo IMPORTANT: Do NOT include your .env file with your API key!
echo            Only include .env.example for distribution.
echo.
echo ======================================================================
echo.
pause
