# Omnix contributor context

Follow [AGENTS.md](AGENTS.md). This repository's canonical 3.0 application is
the Python 3.11+ PyQt6 package in `src/omnix`. Keep Tauri code in the separate
[Omnix Tauri](https://github.com/shingoku2/Omnix-Tauri) repository and do not
recreate it here. Do not add flat `src.<module>` imports.

Architecture and data-migration contracts live in
[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) and
[docs/UPGRADING.md](docs/UPGRADING.md).

CI uses GitHub-hosted Python 3.11 runners on Ubuntu, Windows, and macOS. Read
[docs/CI_CD_GUIDE.md](docs/CI_CD_GUIDE.md) before changing runner packages,
headless Qt setup, path-sensitive tests, or dependency auditing.
