#!/usr/bin/env python3
"""
Analyze test coverage by mapping source files to test files
"""
import sys
from pathlib import Path

# Source modules to analyze
src_dir = Path('src')
test_dir = Path('tests')

# Core modules from src/
core_modules = [
    'config.py',
    'credential_store.py',
    'game_detector.py',
    'game_watcher.py',
    'game_profile.py',
    'ai_assistant.py',
    'ai_router.py',
    'providers.py',
    'provider_tester.py',
    'knowledge_pack.py',
    'knowledge_store.py',
    'knowledge_index.py',
    'knowledge_integration.py',
    'knowledge_ingestion.py',
    'macro_manager.py',
    'macro_store.py',
    'macro_runner.py',
    'macro_ai_generator.py',
    'keybind_manager.py',
    'session_logger.py',
    'session_coaching.py',
    'gui.py',
    'overlay_modes.py',
    'settings_dialog.py',
    'settings_tabs.py',
    'providers_tab.py',
    'game_profiles_tab.py',
    'knowledge_packs_tab.py',
    'appearance_tabs.py',
    'setup_wizard.py',
    'session_recap_dialog.py',
    'theme_manager.py',
    'theme_compat.py',
    'utils.py',
    'error_recovery.py',
    'filelock.py',
]

ui_modules = [
    'ui/design_system.py',
    'ui/tokens.py',
    'ui/theme_manager.py',
    'ui/components/buttons.py',
    'ui/components/inputs.py',
    'ui/components/cards.py',
    'ui/components/layouts.py',
    'ui/components/navigation.py',
    'ui/components/modals.py',
    'ui/components/overlay.py',
    'ui/components/dashboard.py',
    'ui/components/dashboard_button.py',
]

# Map module names to potential test files
def get_test_file_for_module(module_name):
    """Get potential test file names for a module"""
    base_name = Path(module_name).stem
    potential_tests = [
        f'test_{base_name}.py',
        f'tests/unit/test_{base_name}.py',
        f'tests/test_{base_name}.py',
    ]
    return potential_tests

# Check which modules have tests
print("=" * 80)
print("OMNIX TEST COVERAGE ANALYSIS")
print("=" * 80)
print()

tested_modules = []
untested_modules = []
partial_modules = []

all_modules = core_modules + ui_modules

for module in all_modules:
    potential_tests = get_test_file_for_module(module)
    has_test = False

    for test_file in potential_tests:
        if Path(test_file).exists():
            has_test = True
            tested_modules.append((module, test_file))
            break

    if not has_test:
        untested_modules.append(module)

print(f"✅ TESTED MODULES ({len(tested_modules)}/{len(all_modules)}):")
print("-" * 80)
for module, test_file in sorted(tested_modules):
    print(f"  {module:40} → {test_file}")

print()
print(f"❌ UNTESTED MODULES ({len(untested_modules)}/{len(all_modules)}):")
print("-" * 80)
for module in sorted(untested_modules):
    print(f"  {module}")

# Calculate coverage percentage
coverage_pct = (len(tested_modules) / len(all_modules)) * 100
print()
print("=" * 80)
print(f"OVERALL COVERAGE: {coverage_pct:.1f}% ({len(tested_modules)}/{len(all_modules)} modules)")
print("=" * 80)

# Analyze test organization
print()
print("TEST ORGANIZATION:")
print("-" * 80)

unit_tests = list(Path('tests/unit').glob('test_*.py')) if Path('tests/unit').exists() else []
integration_tests = list(Path('tests/integration').glob('test_*.py')) if Path('tests/integration').exists() else []
root_tests = list(Path('.').glob('test_*.py'))

print(f"  Unit tests:        {len(unit_tests)}")
print(f"  Integration tests: {len(integration_tests)}")
print(f"  Root tests:        {len(root_tests)}")
print(f"  Total test files:  {len(unit_tests) + len(integration_tests) + len(root_tests)}")

sys.exit(0)
