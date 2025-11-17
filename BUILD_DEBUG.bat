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
echo.

python -m PyInstaller ^
    --name=GamingAIAssistant_DEBUG ^
    --onedir ^
    --console ^
    --clean ^
    --noconfirm ^
    --paths=src ^
    --hidden-import=PyQt6.QtCore ^
    --hidden-import=PyQt6.QtGui ^
    --hidden-import=PyQt6.QtWidgets ^
    --hidden-import=config ^
    --hidden-import=game_detector ^
    --hidden-import=ai_assistant ^
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
    --hidden-import=ui.design_system ^
    --hidden-import=ui.tokens ^
    --hidden-import=ui.icons ^
    --hidden-import=ui.components.buttons ^
    --hidden-import=ui.components.inputs ^
    --hidden-import=ui.components.cards ^
    --hidden-import=ui.components.layouts ^
    --hidden-import=ui.components.navigation ^
    --hidden-import=ui.components.modals ^
    --hidden-import=ui.components.dashboard_button ^
    --hidden-import=ui.components.avatar_display ^
    --hidden-import=ui.components.overlay ^
    main.py

if errorlevel 1 (
    echo Build failed!
    pause
    exit /b 1
)

REM Copy example configuration
if exist ".env.example" (
    copy ".env.example" "dist\GamingAIAssistant_DEBUG\.env.example" >nul 2>&1
    echo Copied .env.example
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
