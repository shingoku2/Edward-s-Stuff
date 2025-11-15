#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API Key Diagnostic Script
Tests if the API keys are valid and have proper access
"""

import sys
import os
from pathlib import Path

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Add src to path
src_path = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_path))

print("=" * 70)
print("API KEY DIAGNOSTIC TEST")
print("=" * 70)

# Load API keys from CredentialStore
try:
    from config import Config
    from provider_tester import ProviderTester
    config = Config(require_keys=False)
except Exception as e:
    print(f"Error loading config: {e}")
    sys.exit(1)

# Test Anthropic API
print("\n[1/3] Testing Anthropic API Key...")
anthropic_key = config.get_api_key('anthropic')

if anthropic_key:
    print(f"  Key found: {anthropic_key[:20]}...{anthropic_key[-10:]}")

    try:
        success, message = ProviderTester.test_anthropic(anthropic_key)
        if success:
            print(f"✓ Anthropic Test SUCCESSFUL!")
            print(f"  {message.splitlines()[0]}")
        else:
            print(f"✗ Anthropic Test FAILED:")
            print(f"  {message}")
    except Exception as e:
        print(f"✗ Error: {e}")
else:
    print("  No Anthropic API key found in CredentialStore")

# Test OpenAI API
print("\n[2/3] Testing OpenAI API Key...")
openai_key = config.get_api_key('openai')

if openai_key:
    print(f"  Key found: {openai_key[:20]}...{openai_key[-10:]}")

    try:
        success, message = ProviderTester.test_openai(openai_key)
        if success:
            print(f"✓ OpenAI Test SUCCESSFUL!")
            print(f"  {message.splitlines()[0]}")
        else:
            print(f"✗ OpenAI Test FAILED:")
            print(f"  {message}")
    except Exception as e:
        print(f"✗ Error: {e}")
else:
    print("  No OpenAI API key found in CredentialStore")

# Test Gemini API
print("\n[3/3] Testing Gemini API Key...")
gemini_key = config.get_api_key('gemini')

if gemini_key:
    print(f"  Key found: {gemini_key[:20]}...{gemini_key[-10:]}")

    try:
        success, message = ProviderTester.test_gemini(gemini_key)
        if success:
            print(f"✓ Gemini Test SUCCESSFUL!")
            print(f"  {message.splitlines()[0]}")
        else:
            print(f"✗ Gemini Test FAILED:")
            print(f"  {message}")
    except Exception as e:
        print(f"✗ Error: {e}")
else:
    print("  No Gemini API key found in CredentialStore")

print("\n" + "=" * 70)
print("DIAGNOSTIC COMPLETE")
print("=" * 70)
print("\nIf keys are invalid, please:")
print("1. Verify the keys haven't been revoked")
print("2. Check if the accounts have credits/access")
print("3. Use the Setup Wizard to add new API keys:")
print("   - Anthropic: https://console.anthropic.com/")
print("   - OpenAI: https://platform.openai.com/api-keys")
print("   - Gemini: https://aistudio.google.com/app/apikey")
print("=" * 70)
