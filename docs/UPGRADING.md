# Upgrading to Omnix 3.0

Omnix 3.0 requires Python 3.11 or newer. Recreate the virtual environment and
install the project itself; importing standalone modules from `src/` is no
longer supported.

```bash
python -m venv .venv
python -m pip install --upgrade pip "setuptools>=83"
python -m pip install --upgrade ".[dev,build]"
```

The first launch runs ordered, idempotent data migrations. Existing settings,
keybindings, macros, profiles, knowledge packs, and encrypted credentials are
copied to a timestamped backup before a migration changes them. Do not delete
the `backups` directory until the updated profile has been verified.

The v3 migration:

- converts legacy list-shaped macro files to ID-keyed objects;
- records the schema version in configuration and migration state;
- resets removed cloud-provider selections to the supported Ollama provider;
- introduces a SQLite FTS5 knowledge database while retaining the legacy JSON
  index for compatibility and model metadata.

If a profile reports a schema newer than the application supports, Omnix stops
instead of attempting a downgrade. Install the newer application or restore a
matching backup.

React/Tauri assets and their workflows were removed from this repository. The
Tauri edition is now maintained independently in
[Omnix Tauri](https://github.com/shingoku2/Omnix-Tauri); Python 3.0 upgrades do
not install or migrate that application.
