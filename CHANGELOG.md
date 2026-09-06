# Changelog

## 3.0.0 - 2026-09-05

- Consolidated the application into the installable `omnix` Python package and
  retired the React and Tauri clients.
- Added atomic, backed-up profile schema migrations.
- Added SQLite FTS5 persistence for knowledge chunks with TF-IDF reranking.
- Added explicit Windows/macOS/X11 capability handling and safe Wayland feature
  disablement.
- Moved license lookup and seat enforcement behind a private Supabase Edge
  Function.
- Refreshed the native desktop theme, wired macro and knowledge settings, and
  added cooperative worker shutdown.
- Added Python 3.11 cross-platform CI, dependency locking, and unsigned desktop
  release bundles.

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Removed

- HRM (Hierarchical Reasoning Model) integration: `src/hrm_integration.py`, the HRM Settings tab, `HRM_ENABLED`/`HRM_MAX_INFERENCE_TIME` config, the vendored `HRM-main/` model source, and the Tauri `hrm.rs` reasoning-prefix module. No longer used by the app.

## [2.0.2] - 2026-08-28

### Added

- Live Ollama model dropdowns on the dashboard's Quick Settings "AI Model" field and the Game Profile editor's Model field, using the same `FetchModelsThread` as the Providers settings tab instead of a static default-only input. (#221)

### Fixed

- **FetchModelsThread response parsing**: the installed `ollama` package returns a `ListResponse`/`Model` pydantic object (`Model.model`), not the `{"models": [{"name": ...}]}` dict shape the parser assumed, so every model fetch silently failed and fell back to the `llama3` placeholder everywhere. (#221)
- `main.py` / `license_dialog.py` called `credential_store.get_credential`/`set_credential` with the old single-arg signature; updated to the current `(service, key)` signature. (#221)
- `gui.py`'s `OverlayWindow` called the renamed `design_system.get_overlay_stylesheet` instead of `generate_overlay_stylesheet`. (#221)
- **credential_store.py**: missing `sys` import crashed the interactive password-prompt fallback; wired up the previously-unused `FileLock` for real cross-process locking; scoped the password-fallback key file per-instance instead of sharing one global temp-dir path across every `CredentialStore`. (#220)
- **gui.py**: escaped sender/text before interpolating into the chat `QTextEdit` HTML — was vulnerable to HTML injection via chat content. (#220)
- **knowledge_ingestion.py**: blocked SSRF in URL-based knowledge pack ingestion by validating scheme and resolved IP (rejects loopback/private/link-local/reserved) on the initial URL and every redirect hop. (#220)
- **keybind_manager.py**: `KeybindManager` is now a `QObject` that dispatches global hotkey callbacks through a queued signal, so they run on the Qt GUI thread instead of the pynput listener thread touching widgets directly. (#220)
- **base_store.py, session_logger.py**: JSON writes are now atomic (temp file + `os.replace`); `session_logger` flushes every event instead of every 10th and fixes session-ID parsing for `game_profile_id` values containing underscores. (#220)
- **config.py**: a plaintext `AI_API_KEY` found in `.env` is migrated into the encrypted `CredentialStore` instead of being written back to disk in plaintext on every settings save. (#220)
- **ai_assistant.py**: `clear_history()` no longer locks the AI into a persona for a game literally named "Unknown Game" when no game is detected. (#220)
- **settings_tabs.py**: added the missing `Config` import — `save_config()` called `Config.save_to_env()` without it, raising `NameError` at runtime. (#220)
- Fixed the Omnix Tauri CI workflow, broken on every run since introduction: wrong action reference, a `WindowConfig.label` type mismatch, unused-variable build failures, missing Linux system deps (`libwebkit2gtk-4.1-dev`, `libxdo-dev`), and a Rust `tauri` crate version mismatch against the npm `@tauri-apps/api` version. (#220)

### Changed

- Bumped React, Vite, ESLint, and other devDependencies in `frontend/` and `omnix-tauri/` to latest compatible versions; ran `npm audit fix` in `omnix-tauri/`. (#220)

### Tests

- Fixed pre-existing bugs in `test_core.py`, `test_gui.py`, `test_imports.py`, `test_overlay_geometry.py`, and `test_session_coaching.py`. Full suite went from 346 passed / 12 failing to 358 passed / 8 skipped (torch not installed) / 0 failing. (#220)

## [2.0.1] - 2026-05-08

### Fixed

- **Thread safety in AIAssistant**: `_add_system_context` and `clear_history` could be called concurrently without proper locking, causing race conditions. Changed `_history_lock` from `Lock()` to `RLock()` (allows re-entry from same thread) and added lock guards to `_add_system_context`.
- **Config.save_to_env preserved other env vars**: When updating only `ollama_host`, the method was regenerating the `.env` file and wiping `AI_API_KEY`, `AI_BASE_URL`, `AI_MODEL`, and other pre-existing values. Fixed by using `setdefault` for values and explicitly preserving AI API settings block.
- **GameWatcher None profile handling**: `_handle_game_active` accessed `profile.display_name` without checking if `profile` was `None` first. Now returns early if `get_profile_by_executable` returns `None`.
- **Hash cache invalidation TypeError**: `KnowledgeIndex` used `hash(tuple(sorted(common_games.items())))` but dict values contain lists which are not hashable. Fixed by using `frozenset(self.common_games.keys())` instead.
- **MacroRunner max_repeat hardcoded default**: `execute_macro` defaulted `max_repeat` to 100 instead of using the `DEFAULT_MAX_MACRO_REPEAT` config constant (10). Fixed to import and use the config constant.
- **Macro update_at field name typo**: `update_macro` was setting `macro.modified_at` instead of `macro.updated_at`, so the timestamp was never actually updated. Fixed the field name.

### Changed

- Updated error message in `main.py` to reference Ollama configuration instead of deprecated Anthropic API key setup.

## [2.0.0] - 2025-12-09

### Added

- HRM (Heuristic Reasoning Model) integration for structured reasoning on puzzle, strategy, and optimization questions
- Intelligent question type detection with game genre-aware routing
- Automatic Ollama model discovery
- Config preservation for environment variables

### Changed

- Migrated from multi-provider AI (OpenAI, Anthropic, Gemini) to Ollama-only for privacy-first, local inference
- Removed API key storage requirement (unless using secured Ollama endpoint)
- Unified token-based design system with backward compatibility

### Fixed

- TF-IDF model persistence - search results now consistent across restarts
