# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('src/*.py', 'src'),
        ('.env.example', '.'),
        ('README.md', '.'),
        ('SETUP.md', '.'),
    ],
    hiddenimports=[
        # PyQt6
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets',
        'PyQt6.QtWebEngineCore',
        'PyQt6.QtWebEngineWidgets',
        # Core modules
        'config', 'game_detector', 'ai_assistant', 'info_scraper', 'gui',
        # New secure modules
        'credential_store', 'provider_tester', 'providers', 'ai_router', 'setup_wizard',
        # Settings and UI
        'providers_tab', 'settings_dialog', 'settings_tabs', 'appearance_tabs', 'login_dialog',
        # Managers
        'keybind_manager', 'macro_manager', 'theme_manager',
        # AI providers
        'anthropic',
        'openai',
        'google.generativeai',
        # Utilities
        'psutil',
        'requests',
        'bs4',
        'dotenv',
        'cryptography',
        'keyring',
        'pynput',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='GamingAIAssistant',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # No console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='GamingAIAssistant',
)
