#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Windows Executable Builder
Creates a standalone .exe for Windows
"""

import os
import sys
import subprocess
import shutil

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

print("=" * 70)
print("GAMING AI ASSISTANT - WINDOWS EXECUTABLE BUILDER")
print("=" * 70)

# Check if PyInstaller is installed
try:
    import PyInstaller
    print("\n✓ PyInstaller found")
except ImportError:
    print("\n✗ PyInstaller not found. Installing...")
    subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"])
    print("✓ PyInstaller installed")

# Clean previous builds
print("\n[1/4] Cleaning previous builds...")
if os.path.exists("build"):
    shutil.rmtree("build")
    print("  - Removed build/")
if os.path.exists("dist"):
    shutil.rmtree("dist")
    print("  - Removed dist/")

# Build the executable
print("\n[2/4] Building Windows executable...")
print("  Using GamingAIAssistant.spec for build configuration...")
print("  This may take several minutes...\n")

cmd = [
    "pyinstaller",
    "GamingAIAssistant.spec",
    "--clean",
    "--noconfirm"
]

result = subprocess.run(cmd, capture_output=True, text=True)

if result.returncode != 0:
    print("✗ Build failed!")
    print(result.stderr)
    sys.exit(1)

print("✓ Build completed!")

# Copy necessary files to dist
print("\n[3/4] Copying additional files...")
dist_dir = "dist/GamingAIAssistant"
if os.path.exists(dist_dir):
    # Copy .env.example
    if os.path.exists(".env.example"):
        shutil.copy(".env.example", os.path.join(dist_dir, ".env.example"))
        print("  ✓ Copied .env.example")

    # Copy documentation
    for doc in ["README.md", "SETUP.md", "TEST_REPORT.md", "API_TEST_RESULTS.md"]:
        if os.path.exists(doc):
            shutil.copy(doc, os.path.join(dist_dir, doc))
            print(f"  ✓ Copied {doc}")

    # Create instructions
    instructions = """
GAMING AI ASSISTANT - QUICK START
==================================

1. RUN THE APPLICATION:
   - Double-click GamingAIAssistant.exe
   - The Setup Wizard will launch automatically on first run

2. CONFIGURE YOUR AI PROVIDER:
   - Select your preferred AI provider (Anthropic Claude, OpenAI, or Gemini)
   - Enter your API key (it will be stored securely in encrypted CredentialStore)
   - Test the connection

3. START GAMING:
   - Launch a game (League of Legends, Minecraft, VALORANT, Elden Ring, etc.)
   - Press Ctrl+Shift+G to open the assistant while in-game
   - Ask questions, get tips, and enhance your gameplay!

4. GET AN API KEY (if you don't have one):
   - Anthropic Claude: https://console.anthropic.com/
   - OpenAI: https://platform.openai.com/api-keys
   - Gemini: https://aistudio.google.com/app/apikey

SECURITY NOTE:
- Your API key is stored securely in your system's credential manager
- API keys are NOT stored in .env files
- No data is sent to anyone except your chosen AI provider

For detailed instructions, see SETUP.md

Supported Games: 50+ games including League of Legends, Minecraft, VALORANT,
Dota 2, Elden Ring, Dark Souls 3, Cyberpunk 2077, and more!
"""

    with open(os.path.join(dist_dir, "START_HERE.txt"), "w") as f:
        f.write(instructions)
    print("  ✓ Created START_HERE.txt")

print("\n[4/4] Creating distribution package...")

# Create a zip file for easy distribution
dist_name = "GamingAIAssistant_Windows"
if os.path.exists(f"{dist_name}.zip"):
    os.remove(f"{dist_name}.zip")

shutil.make_archive(dist_name, 'zip', 'dist', 'GamingAIAssistant')
print(f"  ✓ Created {dist_name}.zip")

# Summary
print("\n" + "=" * 70)
print("BUILD COMPLETE!")
print("=" * 70)
print(f"\n📦 Windows executable created:")
print(f"   Location: dist/GamingAIAssistant/GamingAIAssistant.exe")
print(f"\n📦 Distribution package:")
print(f"   File: {dist_name}.zip")
print(f"\n💡 To use on Windows:")
print(f"   1. Extract {dist_name}.zip")
print(f"   2. Run GamingAIAssistant.exe")
print(f"   3. Setup Wizard will guide you through API key configuration")
print(f"\n🔒 Security:")
print(f"   - API keys are stored securely in system credential manager")
print(f"   - NOT stored in .env files!")
print("=" * 70)
