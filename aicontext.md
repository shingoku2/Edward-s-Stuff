# Omnix 3.0 context

- Runtime: Python 3.11+, PyQt6, Ollama.
- Package: `src/omnix`; entry point: `omnix.__main__:main`.
- UI: native PyQt6 only in this repository. The Rust/Tauri edition is maintained
  separately at https://github.com/shingoku2/Omnix-Tauri.
- Storage: atomic JSON stores, encrypted credential vault, SQLite FTS5 knowledge index.
- Platforms: Windows, macOS, and Linux X11; Wayland automation is disabled explicitly.
- Quality: GitHub-hosted Python 3.11 pytest CI on Ubuntu/Windows/macOS, fatal
  flake8 checks, Bandit, pip-audit, and unsigned PyInstaller bundles.
- CI prerequisites: Ubuntu installs `libegl1` for PyQt6; CI upgrades the audited
  environment to `setuptools>=83`.
- Filesystem security: knowledge ingestion compares resolved candidate paths
  against resolved allowed roots so platform aliases remain safe and portable.

Contributor rules are in [AGENTS.md](AGENTS.md). See
[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) and
[docs/UPGRADING.md](docs/UPGRADING.md) before structural or persistence changes;
use [docs/CI_CD_GUIDE.md](docs/CI_CD_GUIDE.md) for CI changes.
