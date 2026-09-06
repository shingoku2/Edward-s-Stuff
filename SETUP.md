# Omnix 3.0 setup

## Requirements

- Python 3.11 or newer
- Ollama
- Windows 10/11, macOS 13+, or modern Linux

Linux users need an X11 session for macros and global hotkeys. The desktop UI
and game detection continue to work on Wayland.

## Install

```bash
python -m venv .venv
```

Activate the environment:

```bash
# Linux/macOS
source .venv/bin/activate

# Windows PowerShell
.venv\Scripts\Activate.ps1
```

Install and run:

```bash
python -m pip install --upgrade pip
python -m pip install -e .
ollama pull llama3
python -m omnix
```

For a contributor environment, use `python -m pip install -e ".[dev,build]"`.

## Configuration

The default Ollama endpoint is `http://localhost:11434`, and the default model
is `llama3`. Override them with `OLLAMA_HOST` and `OLLAMA_MODEL` or use Settings
in the app.

User data is stored in `~/.gaming_ai_assistant`. Set `OMNIX_CONFIG_DIR` to use a
different profile. Systems without an OS keyring must set
`OMNIX_MASTER_PASSWORD`; never commit that value or place it in shell history.

Older profiles migrate automatically at startup. Review
[docs/UPGRADING.md](docs/UPGRADING.md) before upgrading a production install.

## Verify

```bash
OMNIX_MASTER_PASSWORD=test-only-password QT_QPA_PLATFORM=offscreen pytest
python -m pip check
```

On Windows PowerShell, set variables with `$env:NAME = "value"` before running
pytest.

## Build

```bash
python -m pip install -e ".[build]"
pyinstaller GamingAIAssistant.spec --clean --noconfirm
```

CI creates unsigned Windows, macOS, and Linux bundles. Production distributors
must add platform code signing separately.
