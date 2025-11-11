"""
Setup script for Gaming AI Assistant
This script helps users set up the application quickly
"""

import os
import sys
import subprocess
from pathlib import Path


def print_header(text):
    """Print formatted header"""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60 + "\n")


def print_step(step, text):
    """Print step information"""
    print(f"[{step}] {text}")


def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Error: Python 3.8 or higher is required")
        print(f"   Current version: {version.major}.{version.minor}.{version.micro}")
        print("\n   Please install Python 3.8+ from https://python.org")
        return False
    print(f"✓ Python {version.major}.{version.minor}.{version.micro} detected")
    return True


def install_dependencies():
    """Install required dependencies"""
    print_step("1/4", "Installing dependencies...")

    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ])
        print("✓ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        return False


def setup_env_file():
    """Set up .env file"""
    print_step("2/4", "Setting up configuration file...")

    env_example = Path(".env.example")
    env_file = Path(".env")

    if env_file.exists():
        response = input("\n.env file already exists. Overwrite? (y/N): ")
        if response.lower() != 'y':
            print("✓ Using existing .env file")
            return True

    if not env_example.exists():
        print("❌ Error: .env.example not found")
        return False

    try:
        with open(env_example, 'r') as f:
            content = f.read()

        with open(env_file, 'w') as f:
            f.write(content)

        print("✓ Created .env file from template")
        return True
    except Exception as e:
        print(f"❌ Error creating .env file: {e}")
        return False


def configure_api_key():
    """Guide user through API key configuration"""
    print_step("3/4", "Configuring AI provider...")

    print("\nChoose your AI provider:")
    print("  1. Anthropic (Claude) - Recommended")
    print("  2. OpenAI (GPT)")

    while True:
        choice = input("\nEnter choice (1 or 2): ").strip()
        if choice in ['1', '2']:
            break
        print("Invalid choice. Please enter 1 or 2.")

    provider = "anthropic" if choice == "1" else "openai"
    provider_name = "Anthropic" if choice == "1" else "OpenAI"

    print(f"\n✓ Selected {provider_name}")
    print(f"\nTo get your API key:")

    if provider == "anthropic":
        print("  1. Go to https://console.anthropic.com/")
        print("  2. Sign up or log in")
        print("  3. Navigate to API Keys")
        print("  4. Create a new API key")
    else:
        print("  1. Go to https://platform.openai.com/")
        print("  2. Sign up or log in")
        print("  3. Navigate to API Keys")
        print("  4. Create a new API key")

    print("\nDo you have your API key ready?")
    print("  1. Yes, I have my key")
    print("  2. No, I'll add it later")

    response = input("\nEnter choice (1 or 2): ").strip()

    env_file = Path(".env")

    if response == "1":
        api_key = input(f"\nEnter your {provider_name} API key: ").strip()

        try:
            with open(env_file, 'r') as f:
                content = f.read()

            # Update API provider
            content = content.replace(
                "AI_PROVIDER=anthropic",
                f"AI_PROVIDER={provider}"
            )

            # Update API key
            if provider == "anthropic":
                content = content.replace(
                    "ANTHROPIC_API_KEY=your_anthropic_api_key_here",
                    f"ANTHROPIC_API_KEY={api_key}"
                )
            else:
                content = content.replace(
                    "OPENAI_API_KEY=your_openai_api_key_here",
                    f"OPENAI_API_KEY={api_key}"
                )

            with open(env_file, 'w') as f:
                f.write(content)

            print("✓ API key configured successfully")
            return True

        except Exception as e:
            print(f"❌ Error configuring API key: {e}")
            return False
    else:
        print("\n⚠ Remember to add your API key to .env before running the app!")
        print(f"   Edit .env and add your key to {provider.upper()}_API_KEY")
        return True


def verify_setup():
    """Verify the setup is correct"""
    print_step("4/4", "Verifying setup...")

    try:
        # Check if config can be loaded
        env_file = Path(".env")
        if not env_file.exists():
            print("❌ .env file not found")
            return False

        print("✓ Configuration file exists")
        print("✓ Setup complete!")
        return True

    except Exception as e:
        print(f"❌ Setup verification failed: {e}")
        return False


def main():
    """Main setup function"""
    print_header("Gaming AI Assistant - Setup")

    print("This script will help you set up the Gaming AI Assistant.\n")

    # Check Python version
    if not check_python_version():
        sys.exit(1)

    print()

    # Install dependencies
    if not install_dependencies():
        print("\n❌ Setup failed during dependency installation")
        sys.exit(1)

    print()

    # Setup .env file
    if not setup_env_file():
        print("\n❌ Setup failed during .env file creation")
        sys.exit(1)

    print()

    # Configure API key
    if not configure_api_key():
        print("\n❌ Setup failed during API key configuration")
        sys.exit(1)

    print()

    # Verify setup
    if not verify_setup():
        print("\n❌ Setup verification failed")
        sys.exit(1)

    # Success!
    print_header("Setup Complete!")

    print("🎉 You're all set! Here's what to do next:\n")
    print("1. Make sure you have a game installed")
    print("2. Run the application:")
    print("   python main.py")
    print("\n3. Launch a game and the assistant will detect it")
    print("4. Ask questions about the game in real-time!")
    print("\nHotkey: Press Ctrl+Shift+G to toggle the assistant window")
    print("\nNeed help? Check SETUP.md for detailed instructions")
    print("\nHappy Gaming! 🎮\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
