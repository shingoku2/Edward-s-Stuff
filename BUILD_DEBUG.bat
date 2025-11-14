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
    echo Build failed!
    pause
    exit /b 1
)

echo.
echo ====================================
echo DEBUG BUILD COMPLETE!
echo ====================================
echo.
echo Your DEBUG .exe is at:
echo dist\GamingAIAssistant_DEBUG\GamingAIAssistant_DEBUG.exe
echo.
echo IMPORTANT: Copy your .env file to the same folder:
echo copy .env dist\GamingAIAssistant_DEBUG\.env
echo.
echo This version shows a console window with error messages.
echo Run it to see what's wrong!
echo.
pause
