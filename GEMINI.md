# Omnix contributor context

Follow [AGENTS.md](AGENTS.md). This repository is the Python 3.11+ and PyQt6
desktop application packaged under `src/omnix`. The Rust/Tauri edition lives in
[Omnix Tauri](https://github.com/shingoku2/Omnix-Tauri); keep its code there.

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for dependency boundaries and
[docs/UPGRADING.md](docs/UPGRADING.md) for persistence migration rules.

The CI contract is the hosted Python 3.11 Ubuntu/Windows/macOS matrix documented
in [docs/CI_CD_GUIDE.md](docs/CI_CD_GUIDE.md). Preserve the Linux `libegl1`
prerequisite, canonical path comparisons, and `setuptools>=83` audit floor.
