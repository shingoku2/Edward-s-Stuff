# GUI testing setup

The test suite uses PyQt6 in headless mode. Install the development extra and
set the documented test environment:

```bash
sudo apt-get update && sudo apt-get install --yes libegl1  # Ubuntu/Debian
python -m pip install --upgrade "setuptools>=83" ".[dev,build]"
export QT_QPA_PLATFORM=offscreen
export PYNPUT_BACKEND=dummy
export OMNIX_MASTER_PASSWORD=test-only-password
pytest tests/ui tests/test_gui.py -q
```

Windows PowerShell equivalent:

```powershell
$env:QT_QPA_PLATFORM = "offscreen"
$env:PYNPUT_BACKEND = "dummy"
$env:OMNIX_MASTER_PASSWORD = "test-only-password"
pytest tests/ui tests/test_gui.py -q
```

Use Xvfb when testing X11-specific behavior. Never point tests at a real user
profile; `conftest.py` provisions a disposable `OMNIX_CONFIG_DIR`.
