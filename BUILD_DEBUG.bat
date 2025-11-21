@echo off
REM Build DEBUG version with console to see errors

echo ====================================
echo Building DEBUG version with console
echo ====================================
echo.

echo Cleaning old builds...
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"
echo.

echo Installing dependencies...
python -m pip install -r requirements.txt --quiet --upgrade
python -m pip install pyinstaller --quiet --upgrade
echo.

echo Building DEBUG .exe (with console window)...
echo This lets you see error messages!
echo Using GamingAIAssistant_DEBUG.spec for build configuration...
echo.

python -m PyInstaller GamingAIAssistant_DEBUG.spec --clean --noconfirm

if errorlevel 1 (
    echo Build failed!
    pause
    exit /b 1
)

REM Copy example configuration and documentation
if exist ".env.example" (
    copy ".env.example" "dist\GamingAIAssistant_DEBUG\.env.example" >nul 2>&1
    echo Copied .env.example
)
if exist "README.md" (
    copy "README.md" "dist\GamingAIAssistant_DEBUG\README.md" >nul 2>&1
    echo Copied README.md
)
if exist "SETUP.md" (
    copy "SETUP.md" "dist\GamingAIAssistant_DEBUG\SETUP.md" >nul 2>&1
    echo Copied SETUP.md
)

echo.
echo ====================================
echo DEBUG BUILD COMPLETE!
echo ====================================
echo.
echo Your DEBUG .exe is at:
echo dist\GamingAIAssistant_DEBUG\GamingAIAssistant_DEBUG.exe
echo.
echo FIRST RUN SETUP:
echo 1. Run GamingAIAssistant_DEBUG.exe
echo 2. The Setup Wizard will guide you through configuration
echo 3. Your API keys will be stored securely (encrypted)
echo.
echo This debug version shows a console window with detailed error messages.
echo Use it to diagnose issues or see what's happening under the hood.
echo.
pause
