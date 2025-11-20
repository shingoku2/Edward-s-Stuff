# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py'],
    pathex=['src'],
    binaries=[],
    datas=[
        ('.env.example', '.'),
        ('README.md', '.'),
        ('SETUP.md', '.'),
        ('src/ui/omnix.qss', 'ui'),
    ],
    hiddenimports=[
        # PyQt6
        'PyQt6.QtCore', 'PyQt6.QtGui', 'PyQt6.QtWidgets',
        # Core modules
        'config', 'game_detector', 'ai_assistant', 'gui',
        # New secure modules
        'credential_store', 'provider_tester', 'providers', 'ai_router', 'setup_wizard',
        # Settings and UI
        'providers_tab', 'settings_dialog', 'settings_tabs', 'appearance_tabs',
        # Game profiles and macros
        'game_profile', 'game_profiles_tab', 'game_watcher', 'overlay_modes',
        'macro_store', 'macro_runner', 'macro_ai_generator',
        # Knowledge and session management
        'knowledge_pack', 'knowledge_store', 'knowledge_index', 'knowledge_ingestion',
        'knowledge_integration', 'knowledge_packs_tab', 'session_logger', 'session_coaching', 'session_recap_dialog',
        # Managers
        'keybind_manager', 'macro_manager', 'theme_manager',
        # AI providers
        'anthropic', 'openai', 'google.generativeai',
        # Utilities
        'psutil', 'requests', 'bs4', 'dotenv', 'cryptography', 'keyring', 'pynput',
        # UI Design System
        'ui.design_system', 'ui.tokens', 'ui.icons',
        'ui.components.buttons', 'ui.components.inputs', 'ui.components.cards',
        'ui.components.layouts', 'ui.components.navigation', 'ui.components.modals',
        'ui.components.dashboard_button', 'ui.components.avatar_display', 'ui.components.overlay',
        'ui.components.dashboard'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

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
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='GamingAIAssistant',
)
