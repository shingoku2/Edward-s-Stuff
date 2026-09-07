# GUI testing

The active GUI is native PyQt6. The minimal smoke test and the full UI tests run
without a display:

```bash
export QT_QPA_PLATFORM=offscreen
export PYNPUT_BACKEND=dummy
export OMNIX_MASTER_PASSWORD=test-only-password
pytest tests/ui/test_gui_minimal.py tests/test_gui.py -q
```

The test suite verifies overlay flags, chat worker dispatch, dashboard polling,
settings navigation, and token-generated stylesheets. For a manual run use
`python -m omnix`; configure Ollama separately if chat responses are required.

Platform behavior is intentional: Windows and macOS use native automation,
Linux X11 supports automation, and Linux Wayland leaves the UI usable while
showing that macros/global hotkeys are unavailable.

On Ubuntu/Debian, install `libegl1` before running the suite. Offscreen mode
removes the display requirement but does not supply PyQt6's native EGL library.
