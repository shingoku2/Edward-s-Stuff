# Windows Python setup

Omnix 3.0 requires Python 3.11 or newer. Install Python from
[python.org](https://www.python.org/downloads/windows/) and select **Add Python
to PATH**.

```powershell
py -3.11 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev,build]"
python -m omnix
```

Build the desktop bundle from the repository root:

```powershell
python -m PyInstaller GamingAIAssistant.spec --clean --noconfirm
```

The output is `dist\GamingAIAssistant\GamingAIAssistant.exe`. The spec is the
single source of truth; do not maintain a second list of hidden imports.

If PowerShell blocks activation, run
`Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` once, or invoke
`.venv\Scripts\python.exe` directly. Keep `.env`, credentials, and license
keys out of the repository.
