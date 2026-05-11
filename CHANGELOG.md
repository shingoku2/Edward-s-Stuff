# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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