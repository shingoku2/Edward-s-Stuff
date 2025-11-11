#!/usr/bin/env python3
"""
Windows Executable Builder
Creates a standalone .exe for Windows
"""

import os
import sys
import subprocess
import shutil

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
print("  This may take several minutes...\n")

cmd = [
    "pyinstaller",
    "--name=GamingAIAssistant",
    "--windowed",  # No console window
    "--onedir",    # Create a folder with the exe
    "--clean",
    "--noconfirm",
    "--add-data=.env.example:.",
    "--add-data=README.md:.",
    "--add-data=SETUP.md:.",
    "--hidden-import=PyQt6.QtCore",
    "--hidden-import=PyQt6.QtGui",
    "--hidden-import=PyQt6.QtWidgets",
    "--hidden-import=anthropic",
    "--hidden-import=openai",
    "--hidden-import=psutil",
    "--hidden-import=requests",
    "--hidden-import=bs4",
    "--hidden-import=dotenv",
    "main.py"
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

1. SETUP API KEY:
   - Copy ".env.example" to ".env"
   - Add your Anthropic API key to the .env file
   - Set AI_PROVIDER=anthropic

2. RUN THE APPLICATION:
   - Double-click GamingAIAssistant.exe
   - Launch a game (League of Legends, Minecraft, etc.)
   - Press Ctrl+Shift+G to open the assistant while in-game

3. GET AN API KEY:
   - Visit: https://console.anthropic.com/
   - Create an account and generate an API key
   - Add credits to your account

For detailed instructions, see SETUP.md

Supported Games: League of Legends, Minecraft, VALORANT,
Dota 2, Elden Ring, Dark Souls 3, and 30+ more!
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
print(f"   2. Copy .env.example to .env and add your API key")
print(f"   3. Run GamingAIAssistant.exe")
print("=" * 70)
