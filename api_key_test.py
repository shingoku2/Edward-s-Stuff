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
    config = Config(require_keys=False)
except Exception as e:
    print(f"Error loading config: {e}")
    sys.exit(1)

# Test Anthropic API
print("\n[1/3] Testing Anthropic API Key...")
anthropic_key = config.get_api_key('anthropic')

if anthropic_key:
    print(f"  Key found: {anthropic_key[:20]}...{anthropic_key[-10:]}")
    print(f"  Key length: {len(anthropic_key)} characters")
    print(f"  Expected format: sk-ant-api03-...")

    try:
        import anthropic
        client = anthropic.Anthropic(api_key=anthropic_key)

        # Try the simplest possible request
        print("  Attempting minimal API call...")

        response = client.messages.create(
            model="claude-3-haiku-20240307",  # Smallest/cheapest model
            max_tokens=10,
            messages=[{"role": "user", "content": "Hi"}]
        )

        print(f"✓ Anthropic API key is VALID!")
        print(f"  Response: {response.content[0].text}")

    except anthropic.NotFoundError as e:
        print(f"✗ Model not found error: {e}")
        print(f"  This likely means the API key doesn't have model access")
    except anthropic.AuthenticationError as e:
        print(f"✗ Authentication error: {e}")
        print(f"  The API key is invalid or expired")
    except Exception as e:
        print(f"✗ Error: {e}")
else:
    print("✗ No Anthropic API key found in CredentialStore")

# Test OpenAI API
print("\n[2/3] Testing OpenAI API Key...")
openai_key = config.get_api_key('openai')

if openai_key:
    print(f"  Key found: {openai_key[:20]}...{openai_key[-10:]}")
    print(f"  Key length: {len(openai_key)} characters")
    print(f"  Expected format: sk-proj-...")

    try:
        import openai
        client = openai.OpenAI(api_key=openai_key)

        # Try the simplest possible request
        print("  Attempting minimal API call...")

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Cheapest model
            max_tokens=10,
            messages=[{"role": "user", "content": "Hi"}]
        )

        print(f"✓ OpenAI API key is VALID!")
        print(f"  Response: {response.choices[0].message.content}")

    except openai.AuthenticationError as e:
        print(f"✗ Authentication error: {e}")
        print(f"  The API key is invalid")
    except openai.PermissionDeniedError as e:
        print(f"✗ Permission denied: {e}")
        print(f"  The API key doesn't have access to the API")
    except Exception as e:
        print(f"✗ Error: {e}")
else:
    print("✗ No OpenAI API key found in CredentialStore")

# Test Gemini API
print("\n[3/3] Testing Gemini API Key...")
gemini_key = config.get_api_key('gemini')

if gemini_key:
    print(f"  Key found: {gemini_key[:20]}...{gemini_key[-10:]}")
    print(f"  Key length: {len(gemini_key)} characters")
    print(f"  Expected format: AIza...")

    try:
        import google.generativeai as genai
        genai.configure(api_key=gemini_key)
        model = genai.GenerativeModel('gemini-1.5-flash')

        # Try the simplest possible request
        print("  Attempting minimal API call...")

        response = model.generate_content("Hi", stream=False)

        print(f"✓ Gemini API key is VALID!")
        print(f"  Response: {response.text[:50]}...")

    except Exception as e:
        error_msg = str(e).lower()
        if 'unauthorized' in error_msg or 'authentication' in error_msg:
            print(f"✗ Authentication error: {e}")
            print(f"  The API key is invalid or expired")
        else:
            print(f"✗ Error: {e}")
else:
    print("✗ No Gemini API key found in CredentialStore")

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
