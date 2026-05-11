@echo off
REM Omnix Gaming Companion - Consolidated Build Script
REM Version 2.1.0 (January 2026)
REM Usage: BUILD.bat [debug|simple]

set MODE=release
if /i "%1"=="debug" set MODE=debug
if /i "%1"=="simple" set MODE=simple

echo ======================================================================
echo OMNIX GAMING COMPANION - BUILDER (%MODE%)
echo Version 2.1.0 (January 2026)
echo ======================================================================
echo.

REM 1. Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo.
    echo SOLUTION:
    echo 1. Download Python from: https://www.python.org/downloads/
    echo 2. During installation, CHECK THE BOX: "Add Python to PATH"
    echo 3. After installation, restart Command Prompt
    echo.
    pause
    exit /b 1
)
echo [✓] Python found
python --version
echo.

REM 2. Check pip
python -m pip --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: pip is not available
    echo.
    echo SOLUTION:
    echo Run: python -m ensurepip --upgrade
    echo.
    pause
    exit /b 1
)
echo [✓] pip found
python -m pip --version
echo.

REM 3. Install dependencies
echo [1/5] Installing dependencies...
python -m pip install -r requirements.txt --quiet --upgrade
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo    [✓] Dependencies installed

echo.
echo [2/5] React frontend removed - pure PyQt6 UI (see feature/pure-pyqt6-migration)
REM React frontend removed - pure PyQt6 UI (see feature/pure-pyqt6-migration)

echo.
echo [3/5] Installing PyInstaller...
python -m pip install pyinstaller --quiet --upgrade
if errorlevel 1 (
    echo ERROR: Failed to install PyInstaller
    pause
    exit /b 1
)
echo    [✓] PyInstaller installed

REM 4. Clean
echo.
echo [4/5] Cleaning previous builds...
if exist "build" rmdir /s /q "build" 2>nul
if exist "dist" rmdir /s /q "dist" 2>nul
echo    [✓] Cleaned build folders

REM 5. Build
echo.
echo [5/5] Building executable...

if /i "%MODE%"=="debug" (
    echo Using GamingAIAssistant_DEBUG.spec...
    python -m PyInstaller GamingAIAssistant_DEBUG.spec --clean --noconfirm
    set "DIST_DIR=dist\GamingAIAssistant_DEBUG"
    set "EXE_NAME=GamingAIAssistant_DEBUG.exe"
) else (
    echo Using GamingAIAssistant.spec...
    python -m PyInstaller GamingAIAssistant.spec --clean --noconfirm
    set "DIST_DIR=dist\GamingAIAssistant"
    set "EXE_NAME=GamingAIAssistant.exe"
)

if errorlevel 1 (
    echo.
    echo ERROR: Build failed
    echo.
    pause
    exit /b 1
)

echo.
echo    [✓] Build completed successfully!

REM 6. Post-build setup
echo.
echo [Post-Build] Copying files...

if not exist "%DIST_DIR%" (
    echo ERROR: Dist folder not found: %DIST_DIR%
    pause
    exit /b 1
)

copy ".env.example" "%DIST_DIR%\.env.example" >nul 2>&1
copy "README.md" "%DIST_DIR%\README.md" >nul 2>&1
copy "SETUP.md" "%DIST_DIR%\SETUP.md" >nul 2>&1

if /i "%MODE%"=="release" (
    if exist "TEST_REPORT.md" copy "TEST_REPORT.md" "%DIST_DIR%\TEST_REPORT.md" >nul 2>&1
    if exist "WINDOWS_RELEASE_README.md" copy "WINDOWS_RELEASE_README.md" "%DIST_DIR%\WINDOWS_README.md" >nul 2>&1
    
    REM Create START_HERE.txt
    (
        echo =====================================================
        echo OMNIX GAMING COMPANION - QUICK START
        echo Version 2.1.0 (January 2026)
        echo =====================================================
        echo.
        echo STEP 1: First Run
        echo --------------------------------
        echo 1. Double-click: GamingAIAssistant.exe
        echo 2. Ensure Ollama is running in the background
        echo 3. The app will automatically connect and be ready
        echo.
        echo STEP 2: Use While Gaming
        echo ------------------------
        echo 1. Launch any supported game
        echo 2. Press Ctrl+Shift+G to open the AI assistant
        echo 3. Ask questions about the game!
        echo.
        echo For detailed setup, see SETUP.md
        echo.
    ) > "%DIST_DIR%\START_HERE.txt"
)

echo    [✓] Files copied

echo.
echo ======================================================================
echo BUILD COMPLETE!
echo ======================================================================
echo.
echo Your executable is ready at:
echo    %DIST_DIR%\%EXE_NAME%
echo.
pause
