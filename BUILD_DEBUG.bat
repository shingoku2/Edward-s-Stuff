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
