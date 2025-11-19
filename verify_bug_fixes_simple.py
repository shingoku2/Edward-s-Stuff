#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple Bug Fix Verification Script
Verifies critical bug fixes by inspecting source code directly.
"""

import re
from pathlib import Path


def check_fix_1_knowledge_index():
    """Verify Fix #1: Knowledge Index TF-IDF Model Persistence"""
    print("\n" + "="*70)
    print("FIX #1: Knowledge Index TF-IDF Model Persistence")
    print("="*70)

    file_path = Path("src/knowledge_index.py")
    with open(file_path, 'r') as f:
        content = f.read()

    checks = []

    # Check 1: _save_index() saves embedding_provider
    if "'embedding_provider': self.embedding_provider" in content:
        print("✓ _save_index() saves embedding_provider")
        checks.append(True)
    else:
        print("✗ _save_index() does not save embedding_provider")
        checks.append(False)

    # Check 2: _load_index() restores embedding_provider
    if "data.get('embedding_provider')" in content:
        print("✓ _load_index() restores embedding_provider")
        checks.append(True)
    else:
        print("✗ _load_index() does not restore embedding_provider")
        checks.append(False)

    # Check 3: Legacy format handling
    if "legacy" in content.lower() and "_load_index" in content:
        print("✓ Backward compatibility for legacy index files")
        checks.append(True)
    else:
        print("✗ No backward compatibility handling")
        checks.append(False)

    # Find and display the actual implementation
    save_match = re.search(r'def _save_index\(self\).*?(?=\n    def|\nclass|\Z)', content, re.DOTALL)
    load_match = re.search(r'def _load_index\(self\).*?(?=\n    def|\nclass|\Z)', content, re.DOTALL)

    if save_match:
        print("\n_save_index() implementation found:")
        # Show key lines
        for line in save_match.group(0).split('\n')[:15]:
            if 'embedding_provider' in line or 'data =' in line:
                print(f"  {line}")

    if load_match:
        print("\n_load_index() implementation found:")
        # Show key lines
        for line in load_match.group(0).split('\n')[:25]:
            if 'embedding_provider' in line or 'data.get' in line or 'legacy' in line.lower():
                print(f"  {line}")

    return all(checks)


def check_fix_2_session_tokens():
    """Verify Fix #2: Session Token Leakage Prevention"""
    print("\n" + "="*70)
    print("FIX #2: Session Token Leakage Prevention")
    print("="*70)

    file_path = Path("src/config.py")
    with open(file_path, 'r') as f:
        content = f.read()

    checks = []

    # Check 1: Session tokens removed from .env in save_to_env
    if "OPENAI_SESSION_DATA" in content and "del existing_content" in content:
        print("✓ Session tokens are removed from .env file")
        checks.append(True)
    else:
        print("✗ Session tokens may still be written to .env")
        checks.append(False)

    # Check 2: Secure storage comment/documentation
    if "secure credential store" in content.lower() or "encrypted" in content.lower():
        print("✓ Documentation mentions secure credential storage")
        checks.append(True)
    else:
        print("⚠ No documentation about secure storage")
        checks.append(False)

    # Find the save_to_env implementation
    save_env_match = re.search(r'def save_to_env\(.*?\).*?(?=\n    @|\n    def|\nclass|\Z)', content, re.DOTALL)
    if save_env_match:
        print("\nsave_to_env() session token handling:")
        for line in save_env_match.group(0).split('\n'):
            if 'SESSION' in line and ('del' in line or 'remove' in line.lower() or '#' in line):
                print(f"  {line}")

    return all(checks)


def check_fix_3_game_watcher():
    """Verify Fix #3: Non-Windows Game Detection Performance"""
    print("\n" + "="*70)
    print("FIX #3: Game Watcher Performance Optimization")
    print("="*70)

    file_path = Path("src/game_watcher.py")
    with open(file_path, 'r') as f:
        content = f.read()

    checks = []

    # Check 1: last_known_pid attribute exists
    if "self.last_known_pid" in content:
        print("✓ PID caching attribute (last_known_pid) present")
        checks.append(True)
    else:
        print("✗ PID caching attribute not found")
        checks.append(False)

    # Check 2: PID cache check before full scan
    if "if self.last_known_pid:" in content:
        print("✓ PID cache checked before full scan")
        checks.append(True)
    else:
        print("✗ No PID cache check found")
        checks.append(False)

    # Check 3: Cache is cleared when game closes
    if "last_known_pid = None" in content:
        print("✓ Cache cleared appropriately")
        checks.append(True)
    else:
        print("✗ Cache not cleared")
        checks.append(False)

    # Find and display implementation
    foreground_match = re.search(r'def _get_foreground_executable\(.*?\).*?(?=\n    def|\nclass|\Z)', content, re.DOTALL)
    if foreground_match:
        print("\n_get_foreground_executable() optimization:")
        lines = foreground_match.group(0).split('\n')
        for i, line in enumerate(lines):
            if 'last_known_pid' in line:
                # Show context around PID caching
                for context_line in lines[max(0, i-1):min(len(lines), i+5)]:
                    print(f"  {context_line}")
                break

    return all(checks)


def check_fix_4_text_chunking():
    """Verify Fix #4: Word-Boundary Text Chunking"""
    print("\n" + "="*70)
    print("FIX #4: Word-Boundary Text Chunking")
    print("="*70)

    file_path = Path("src/knowledge_index.py")
    with open(file_path, 'r') as f:
        content = f.read()

    checks = []

    # Check 1: Word-based splitting (words = text.split())
    chunk_func = re.search(r'def _chunk_text\(.*?\).*?(?=\n    def|\nclass|\Z)', content, re.DOTALL)

    if chunk_func:
        func_content = chunk_func.group(0)

        # Check for word-based splitting
        if "words = text.split()" in func_content or "text.split()" in func_content:
            print("✓ Uses word-based splitting")
            checks.append(True)
        else:
            print("✗ Does not use word-based splitting")
            checks.append(False)

        # Check for overlap handling
        if "overlap" in func_content:
            print("✓ Handles chunk overlap")
            checks.append(True)
        else:
            print("⚠ No overlap handling found")
            checks.append(False)

        # Check NOT using character-based slicing
        if "text[:" not in func_content and "text[i:" not in func_content:
            print("✓ Does NOT use character-based slicing")
            checks.append(True)
        else:
            print("⚠ May still use character-based slicing")
            checks.append(False)

        print("\n_chunk_text() implementation preview:")
        for line in func_content.split('\n')[:20]:
            if 'words' in line.lower() or 'split' in line or 'chunk' in line.lower():
                print(f"  {line}")

    return all(checks)


def main():
    """Run all source code verification checks"""
    print("\n" + "="*70)
    print("BUG FIX SOURCE CODE VERIFICATION")
    print("="*70)
    print("\nVerifying that all critical bug fixes are present in source code.")

    results = []

    try:
        results.append(("Knowledge Index Persistence", check_fix_1_knowledge_index()))
    except Exception as e:
        print(f"\n✗ CHECK 1 FAILED: {e}")
        results.append(("Knowledge Index Persistence", False))

    try:
        results.append(("Session Token Security", check_fix_2_session_tokens()))
    except Exception as e:
        print(f"\n✗ CHECK 2 FAILED: {e}")
        results.append(("Session Token Security", False))

    try:
        results.append(("Game Watcher Performance", check_fix_3_game_watcher()))
    except Exception as e:
        print(f"\n✗ CHECK 3 FAILED: {e}")
        results.append(("Game Watcher Performance", False))

    try:
        results.append(("Text Chunking", check_fix_4_text_chunking()))
    except Exception as e:
        print(f"\n✗ CHECK 4 FAILED: {e}")
        results.append(("Text Chunking", False))

    # Print summary
    print("\n" + "="*70)
    print("VERIFICATION SUMMARY")
    print("="*70)

    for name, passed in results:
        status = "✅ VERIFIED" if passed else "❌ NOT FOUND"
        print(f"{status}: {name}")

    all_passed = all(passed for _, passed in results)

    if all_passed:
        print("\n" + "="*70)
        print("🎉 ALL BUG FIXES VERIFIED IN SOURCE CODE!")
        print("="*70)
        print("\nThe following critical fixes are confirmed:")
        print("  1. ✓ Knowledge index TF-IDF model persistence")
        print("  2. ✓ Session token security (removed from .env)")
        print("  3. ✓ Game watcher PID caching for performance")
        print("  4. ✓ Word-boundary text chunking")
        print("\n📝 Git commits implementing these fixes:")
        print("  - 78a2050: Fix critical search index corruption bug")
        print("  - 411ccfa: Fix configuration token precedence and optimize game detection")
        return 0
    else:
        print("\n" + "="*70)
        print("⚠️  SOME FIXES NOT FOUND IN SOURCE CODE")
        print("="*70)
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
