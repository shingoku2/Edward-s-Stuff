# -*- mode: python ; coding: utf-8 -*-
# Omnix Gaming Companion - PyInstaller Build Specification
# Version 3.0 (Pure PyQt6 desktop application)
#
# Recent Updates:
# - Removed React HUD (frontend/dist) — pure PyQt6 UI (2026-05)
# - Removed PyQt6-WebEngine dependency (2026-05)
# - Knowledge index persistence fix (2025-11-19)

import os
import sys

_SPEC_DIR = os.path.dirname(os.path.abspath(SPEC))
_PYNPUT_IMPORTS = {
    'win32': ['pynput.keyboard._win32', 'pynput.mouse._win32'],
    'darwin': ['pynput.keyboard._darwin', 'pynput.mouse._darwin'],
}.get(sys.platform, ['pynput.keyboard._xorg', 'pynput.mouse._xorg'])

a = Analysis(
    ['main.py'],
    pathex=['src'],
    binaries=[],
    datas=[
        ('.env.example', '.'),
        ('README.md', '.'),
        ('SETUP.md', '.'),
        ('src/omnix/ui/omnix.qss', 'omnix/ui'),
    ],
    hiddenimports=_PYNPUT_IMPORTS + [
        # PyQt6
        'PyQt6.QtCore', 'PyQt6.QtGui', 'PyQt6.QtWidgets',
        # Core modules
        'omnix.config', 'omnix.game_detector', 'omnix.ai_assistant', 'omnix.gui',
        # New secure modules
        'omnix.credential_store', 'omnix.provider_tester', 'omnix.providers',
        'omnix.ai_router', 'omnix.setup_wizard', 'omnix.migrations', 'omnix.capabilities',
        # Settings and UI
        'omnix.providers_tab', 'omnix.settings_dialog', 'omnix.settings_tabs', 'omnix.appearance_tabs',
        # Game profiles and macros
        'omnix.game_profile', 'omnix.game_profiles_tab', 'omnix.game_watcher', 'omnix.overlay_modes',
        'omnix.macro_store', 'omnix.macro_runner', 'omnix.macro_ai_generator',
        # Knowledge and session management
        'omnix.knowledge_pack', 'omnix.knowledge_store', 'omnix.knowledge_index', 'omnix.knowledge_ingestion',
        'omnix.knowledge_integration', 'omnix.knowledge_packs_tab', 'omnix.session_logger',
        'omnix.session_coaching', 'omnix.session_recap_dialog',
        # Managers
        'omnix.keybind_manager', 'omnix.macro_manager', 'omnix.ui.theme_manager',
        # Utilities
        'psutil', 'requests', 'bs4', 'dotenv', 'cryptography', 'keyring', 'pynput',
        # UI Design System
        'omnix.ui.design_system', 'omnix.ui.tokens', 'omnix.ui.icons',
        'omnix.ui.components.buttons', 'omnix.ui.components.inputs', 'omnix.ui.components.cards',
        'omnix.ui.components.layouts', 'omnix.ui.components.navigation', 'omnix.ui.components.modals',
        'omnix.ui.components.dashboard_button', 'omnix.ui.components.avatar_display',
        'omnix.ui.components.overlay', 'omnix.ui.components.dashboard'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['IPython', 'black', 'isort', 'mypy', 'pylint', 'pytest', 'tkinter'],
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
