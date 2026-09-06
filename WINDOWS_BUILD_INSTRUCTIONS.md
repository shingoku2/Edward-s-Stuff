# Windows build instructions

Use Python 3.11+ and build from a clean virtual environment:

```powershell
py -3.11 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[build]"
python -m PyInstaller GamingAIAssistant.spec --clean --noconfirm
```

The output is an unsigned onedir bundle under
`dist\GamingAIAssistant`. Test it on a Windows machine with Ollama installed.
Signing, notarization, and automatic updates are intentionally outside the 3.0
build; the release workflow produces unsigned artifacts for Windows, macOS, and
Linux.
