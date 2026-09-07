# Omnix 3.0

Omnix is a privacy-first desktop gaming companion. It detects active games, adds
game-specific local knowledge to Ollama conversations, runs opt-in macros, and
provides a movable in-game assistant overlay.

The 3.0 application in this repository has one interface and one runtime:
native PyQt6 on Python 3.11+. The Rust/Tauri edition is maintained separately
in [Omnix Tauri](https://github.com/shingoku2/Omnix-Tauri).

## Features

- Local AI through Ollama, with no cloud AI account required.
- Passive game detection and custom game profiles.
- PDF, web, text, and note knowledge packs with SQLite FTS5 and TF-IDF ranking.
- Explicitly enabled keyboard and mouse macros with repeat and timeout limits.
- Native dashboard, settings, and always-on-top overlay.
- Encrypted credential storage using the operating-system keyring, with a
  password-derived fallback where a keyring is unavailable.
- Versioned, automatic profile migrations with timestamped recovery backups.

## Install and run

Install Python 3.11 or newer and [Ollama](https://ollama.com/), then run:

```bash
python -m venv .venv
# Linux/macOS
source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install --upgrade pip "setuptools>=83"
python -m pip install -e .
ollama pull llama3
python -m omnix
```

For development:

```bash
python -m pip install -e ".[dev,build]"
pre-commit install
pytest
```

`python main.py` remains available as a source-checkout compatibility entry
point. The installed command is `omnix`.

## Desktop support

| Platform | Dashboard/overlay | Game detection | Macros/global hotkeys |
| --- | --- | --- | --- |
| Windows 10/11 | Supported | Supported | Supported |
| macOS 13+ | Supported | Supported | Supported after Accessibility permission |
| Linux X11 | Supported | Supported | Supported |
| Linux Wayland | Supported | Supported | Disabled with an explanation |

Wayland intentionally blocks synthetic global input in Omnix. Use an X11
session if macros or global hotkeys are required. Games with anti-cheat rules
may prohibit automation regardless of operating-system support; users are
responsible for the rules of each game.

## Configuration and upgrades

User data remains in `~/.gaming_ai_assistant` by default. Override it with
`OMNIX_CONFIG_DIR`. On startup, Omnix upgrades older profiles before loading
them and places recovery copies in `backups/schema-<version>-<timestamp>`.
See [UPGRADING.md](docs/UPGRADING.md) for the 3.0 migration contract.

Important environment variables:

- `OLLAMA_HOST` and `OLLAMA_MODEL`
- `OMNIX_CONFIG_DIR`
- `OMNIX_MASTER_PASSWORD` for headless systems without a keyring
- `SUPABASE_URL`, `SUPABASE_ANON_KEY`, and `OMNIX_LICENSE_KEY` for licensed builds
- `OMNIX_DEV_MODE=1` to bypass licensing in local development

Do not commit `.env`, license keys, API credentials, or encrypted user vaults.

## Quality and releases

```bash
pytest
black --check src tests
isort --check-only src tests
flake8 src/omnix --select=E9,F63,F7,F82
bandit -r src/omnix -ll
pyinstaller GamingAIAssistant.spec --clean --noconfirm
```

CI uses GitHub-hosted Python 3.11 runners for Windows, macOS, and Linux. Ubuntu
installs `libegl1` for headless PyQt6, and the lint job audits the active
dependency environment with pip-audit. Tag builds and manual release runs create
unsigned PyInstaller bundles for all three operating systems. See
[CI_CD_GUIDE.md](docs/CI_CD_GUIDE.md) for reproduction and troubleshooting.
Code signing and automatic updates are intentionally outside the 3.0 release
scope.

## Architecture

The installable package lives in `src/omnix`. UI code depends on application
services and stores; persistence and integrations do not depend on PyQt. See
[ARCHITECTURE.md](docs/ARCHITECTURE.md).

Licensing clients call only the `validate-license` Supabase Edge Function. The
license tables are denied to anonymous and authenticated clients; deploy the SQL
migration and Edge Function under `supabase/` for production licensing.

## License

MIT. See [LICENSE](LICENSE).
