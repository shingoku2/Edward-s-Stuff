#!/usr/bin/env python3
"""
API Key Diagnostic Script
Tests if the API keys are valid and have proper access
"""

import os
from dotenv import load_dotenv

load_dotenv()

print("=" * 70)
print("API KEY DIAGNOSTIC TEST")
print("=" * 70)

# Test Anthropic API
print("\n[1/2] Testing Anthropic API Key...")
anthropic_key = os.getenv("ANTHROPIC_API_KEY")

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
    print("✗ No Anthropic API key found in .env")

# Test OpenAI API
print("\n[2/2] Testing OpenAI API Key...")
openai_key = os.getenv("OPENAI_API_KEY")

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
    print("✗ No OpenAI API key found in .env")

print("\n" + "=" * 70)
print("DIAGNOSTIC COMPLETE")
print("=" * 70)
print("\nIf both keys are invalid, please:")
print("1. Verify the keys haven't been revoked")
print("2. Check if the accounts have credits/access")
print("3. Generate new API keys from:")
print("   - Anthropic: https://console.anthropic.com/")
print("   - OpenAI: https://platform.openai.com/api-keys")
print("=" * 70)
