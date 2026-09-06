# Omnix 3.0 context

- Runtime: Python 3.11+, PyQt6, Ollama.
- Package: `src/omnix`; entry point: `omnix.__main__:main`.
- UI: native PyQt6 only. React and Tauri have been retired.
- Storage: atomic JSON stores, encrypted credential vault, SQLite FTS5 knowledge index.
- Platforms: Windows, macOS, and Linux X11; Wayland automation is disabled explicitly.
- Quality: cross-platform pytest CI, fatal flake8 checks, Bandit, and unsigned PyInstaller bundles.

Contributor rules are in [AGENTS.md](AGENTS.md). See
[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) and
[docs/UPGRADING.md](docs/UPGRADING.md) before structural or persistence changes.
