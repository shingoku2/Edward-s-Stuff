# Desktop bundle troubleshooting

Omnix 3.0 bundles are native PyQt6 applications. They use local Ollama by
default and do not require OpenAI, Anthropic, or Gemini API keys.

## Start with the debug build

```powershell
python -m PyInstaller GamingAIAssistant_DEBUG.spec --clean --noconfirm
dist\GamingAIAssistant_DEBUG\GamingAIAssistant_DEBUG.exe
```

The console shows the startup log and the exact missing dependency or Qt
platform error. Rebuild after installing dependencies with:

```powershell
python -m pip install --upgrade "setuptools>=83" ".[dev,build]"
python -m PyInstaller GamingAIAssistant.spec --clean --noconfirm
```

## Common fixes

- **Qt platform plugin:** install the current Microsoft Visual C++ x64 runtime,
  then rebuild. Do not copy random Qt DLLs into the bundle.
- **Ollama unavailable:** install Ollama, run it, and verify `ollama list`.
- **Credentials unavailable:** configure the OS keyring or set
  `OMNIX_MASTER_PASSWORD` for a controlled headless environment.
- **Macros/global hotkeys unavailable:** grant macOS Accessibility permission;
  use an X11 session on Linux. Wayland intentionally disables automation.
- **Profile problems:** inspect the latest backup under the profile's
  `backups/schema-*` directory and follow [docs/UPGRADING.md](docs/UPGRADING.md).

Run the debug executable from a writable directory. Logs are written beside the
process when possible, otherwise under the configured Omnix profile.
