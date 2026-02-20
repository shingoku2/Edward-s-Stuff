# CLAUDE.md – AI Assistant Guide for Omnix (Tauri)

**Last Updated:** 2026-02
**Stack:** Tauri 2, Rust backend, Vite + React + TypeScript frontend
**User Data:** `~/.gaming_ai_assistant` (Unix) / `%USERPROFILE%\.gaming_ai_assistant` (Windows)

---

## Quick Navigation

1. [Project Overview](#project-overview)
2. [Architecture](#architecture)
3. [Backend (Rust)](#backend-rust)
4. [Frontend (React)](#frontend-react)
5. [Tauri Commands & Events](#tauri-commands--events)
6. [Data & Config](#data--config)
7. [Development & Build](#development--build)
8. [Conventions & Troubleshooting](#conventions--troubleshooting)

---

## Project Overview

### What is Omnix (Tauri)?

Omnix is a desktop AI gaming companion rebuilt with **Rust** and **Tauri 2**. It replicates the behavior of the Python/PyQt6 Omnix app with:

- **Game detection** via sysinfo (process list, match exe names to game profiles)
- **Ollama chat** with optional knowledge context and HRM-style reasoning prefix
- **Game profiles** (CRUD) and **macros** (store, run: key press, delay, mouse click, etc.)
- **Knowledge system** – per-game TF-IDF index, add chunks, search, inject into prompts
- **Session logging** to `logs/session.jsonl`
- **Overlay window** (second window; currently loads full app; minimal overlay route can be added later)
- **Settings** – tabbed modal: General (Ollama URL/model), Game Profiles, Knowledge Packs, Keybindings, Macros, App Appearance, Overlay Appearance

### Project Structure

```
omnix-tauri/
├── src/                    # Frontend (Vite + React + TypeScript)
│   ├── App.tsx             # Main UI: chat, game panel, settings panel, modals
│   ├── App.css             # Neon/cyan theme, panels, modals
│   ├── main.tsx            # Entry
│   └── index.html
├── src-tauri/              # Rust backend
│   ├── src/
│   │   ├── lib.rs          # Tauri commands, app state, window events (exit on main close)
│   │   ├── config.rs       # AppConfig, config_dir(), validate_ollama_base_url()
│   │   ├── game.rs         # GameDetector (sysinfo), current_game()
│   │   ├── ollama.rs       # OllamaClient (list models; chat in send_message via reqwest)
│   │   ├── profile.rs      # GameProfile, GameProfileStore (game_profiles.json)
│   │   ├── macros.rs       # Macro store (macros/<id>.json), execute (enigo), validate_macro_id
│   │   ├── keybind.rs      # KeybindConfig (keybinds.json); overlay hotkey saved, not yet active
│   │   ├── knowledge.rs    # Per-game TF-IDF index (knowledge_index/<game_id>/), search, add_chunks
│   │   ├── session.rs      # log_event() → logs/session.jsonl
│   │   └── hrm.rs          # reasoning_prefix_for_question() (template-based)
│   ├── capabilities/       # Tauri 2 permissions
│   ├── tauri.conf.json
│   └── Cargo.toml
├── package.json            # npm scripts: tauri:dev, tauri:build, build, dev
├── CLAUDE.md               # This file
└── README.md
```

---

## Architecture

- **Frontend:** Single-page React app; all backend access via `invoke('command_name', payload)` and `listen('event_name', handler)` from `@tauri-apps/api`.
- **Backend:** Tauri 2 with managed state (`AppState`: config, game_detector, ollama). Long work (Ollama chat, macro execution) runs in async/spawn_blocking; results communicated via `app.emit()`.
- **Data:** All persistence under `config_dir()` = `~/.gaming_ai_assistant` (same as Python app for migration). JSON files: `config.json`, `game_profiles.json`, `keybinds.json`; `macros/<id>.json`; `knowledge_index/<safe_game_id>/index.json`; `logs/session.jsonl`.

---

## Backend (Rust)

| Module      | Purpose |
|------------|---------|
| **config** | `AppConfig` load/save, `config_dir()`, `validate_ollama_base_url()` (http/https, block metadata hosts). |
| **game**   | `GameDetector`: sysinfo process list, match exe names against loaded game profiles; `current_game()`. |
| **ollama** | `OllamaClient::list_models()` (blocking; called from lib via spawn_blocking in async command). |
| **profile**| `GameProfile`, `GameProfileStore` load/save `game_profiles.json`; `delete_game_profile` in lib. |
| **macros** | `save_macro`, `delete_macro` (validate_macro_id: only `[a-zA-Z0-9_-]+`); `execute_macro` (enigo: delay, key_press, key_down, key_up, mouse_click, mouse_move, mouse_scroll); emits `macro-finished` / `macro-error`. |
| **keybind**| `KeybindConfig` load/save `keybinds.json`; overlay hotkey stored but not yet registered globally. |
| **knowledge** | Per-game index under `knowledge_index/<safe_game_id>/`; `add_chunks` (recompute IDF/vectors); `search()` across games. |
| **session** | `log_event(typ, payload)` appends to `logs/session.jsonl`. |
| **hrm**    | `reasoning_prefix_for_question(&str)` → optional template string for system prompt. |

**Security:** Macro IDs sanitized (no path traversal). Ollama URL validated before use (SSRF mitigation).

---

## Frontend (React)

- **App.tsx:** State for config, game, messages, loading, settings/macros modals, settings tab index, keybinds, game profiles, profile/macro edit, etc. `openSettings(tab)` loads config, keybinds, game profiles; shows error state if config load fails.
- **Settings:** Tabbed modal (General, Game Profiles, Knowledge Packs, Keybindings, Macros, App Appearance, Overlay Appearance). General: Ollama URL + model. Keybindings: overlay hotkey (hint: saved for future use). Macros: list, create/edit (steps as JSON), run, delete; listen for `macro-finished` / `macro-error` for feedback.
- **Right panel:** Overlay Mode → tab 6, General → tab 0, Notifications/Privacy → “(coming soon)” and tab 0.
- **Styling:** `App.css` – dark theme, cyan accent, panels, modals; `role="dialog"` and Escape to close modals.

---

## Tauri Commands & Events

**Commands:** `get_config` | `save_settings` | `send_message` | `get_detected_game` | `list_ollama_models` | `get_game_profiles` | `save_game_profile` | `delete_game_profile` | `get_macros` | `save_macro` | `delete_macro` | `execute_macro` | `knowledge_search` | `knowledge_add_chunks` | `get_keybinds` | `save_keybinds` | `toggle_overlay`.

**Events:** `message-received` (string) | `macro-finished` (macro id) | `macro-error` (id, message).

**Exit:** Closing the main window triggers `app_handle().exit(0)` in `on_window_event`.

---

## Data & Config

- **Paths:** `config_dir()` from `HOME`/`USERPROFILE` + `/.gaming_ai_assistant`. Same layout as Python app.
- **Config:** `config.json` – ai_provider, ollama_base_url, ollama_model, overlay_opacity, theme. Validated on save and before send_message.
- **Game profiles:** `game_profiles.json`; compatible shape with Python.
- **Macros:** One JSON file per macro under `macros/<id>.json`; ID must be `[a-zA-Z0-9_-]+`.

---

## Development & Build

- **Prerequisites:** Node.js 18+, Rust (rustup), C++ build tools (Windows: VS Build Tools), Ollama.
- **Dev:** `npm install` then `npm run tauri:dev` (Vite dev server + Tauri app).
- **Build:** `npm run tauri:build`; output in `src-tauri/target/release/bundle/`.
- **CI:** `.github/workflows/omnix-tauri-ci.yml` – rust-check (cargo check --locked), frontend-build (setup-node with npm cache, npm ci \|\| npm install, npm run build).

---

## Conventions & Troubleshooting

- **Rust:** Standard naming; serde for (de)serialization; errors as `Result<T, String>` or `map_err(|e| e.to_string())`. Use `config::AppConfig::config_dir()` for paths.
- **Frontend:** Invoke with camelCase args where needed; listen for events for async results (message-received, macro-finished, macro-error).
- **Game detection:** Polling in frontend (e.g. every 5s) via `get_detected_game`; backend uses sysinfo and profile exe_names.
- **Overlay:** Currently opens same `index.html`; for a minimal overlay, add a separate route or HTML entry and point overlay window to it in lib.rs.
- **Keybinds:** Overlay hotkey is saved only; global hotkey registration (e.g. rdev or platform API) can be added later.

---

For the legacy Python Omnix codebase, see the repository root `CLAUDE.md` and `AGENTS.md`.
