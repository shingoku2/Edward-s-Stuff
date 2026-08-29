# Omnix (Tauri)

Omnix Gaming Companion rebuilt with **Rust** and **Tauri 2**. It uses the same user data directory as the Python app (`~/.gaming_ai_assistant` on Unix, `%USERPROFILE%\.gaming_ai_assistant` on Windows) so you can migrate or share data between versions.

---

## Prerequisites

- **Node.js** 20.19+ (or 22.12+) and npm - required by the installed Vite version
- **Rust** (rustup) and a C++ build toolchain (Windows: Visual Studio Build Tools)
- **Ollama** running locally (e.g. `ollama serve`, `ollama pull llama3`)

---

## Setup

```bash
cd omnix-tauri
npm install
```

---

## Development

```bash
npm run tauri:dev
```

This starts the Vite dev server and the Tauri app. Ensure Ollama is running for chat.

---

## Build

```bash
npm run tauri:build
```

Produces installers in `src-tauri/target/release/bundle/`. To set app icons:

```bash
npm run tauri icon path/to/your/icon.png
```

---

## Features

| Area | Description |
|------|-------------|
| **Config** | Load/save from `~/.gaming_ai_assistant`; Ollama base URL and model, theme, overlay opacity. URL validated (http/https, no metadata hosts). |
| **Game detection** | Polls running processes (sysinfo) and matches exe names to game profiles. |
| **Ollama chat** | Send message; response via `message-received` event. Uses knowledge context to inform the answer. |
| **Settings** | Tabbed modal: General (AI), Game Profiles, Knowledge Packs, Keybindings, Macros, App Appearance, Overlay Appearance. |
| **Game profiles** | CRUD for `game_profiles.json` (compatible with Python app). |
| **Macros** | Store and run macros (delay, key press, key down/up, mouse click, move, scroll) via enigo. List, create, edit, run, delete from Settings or Macros modal. Events: `macro-finished`, `macro-error`. |
| **Keybinds** | Overlay hotkey stored in `keybinds.json`; saved for future use (global hotkey registration not yet implemented). |
| **Knowledge** | Per-game TF-IDF index; add chunks from Settings → Knowledge Packs; search augments chat context. |
| **Session** | Events logged to `logs/session.jsonl`. |
| **Overlay** | Toggle a second window. Currently loads the full app (same `index.html`); a minimal overlay route can be added later. |
| **Exit** | Closing the main window exits the app. |

---

## Tauri API

**Commands:** `get_config`, `save_settings`, `send_message`, `get_detected_game`, `list_ollama_models`, `get_game_profiles`, `save_game_profile`, `delete_game_profile`, `get_macros`, `save_macro`, `delete_macro`, `execute_macro`, `knowledge_search`, `knowledge_add_chunks`, `get_keybinds`, `save_keybinds`, `toggle_overlay`.

**Events:** `message-received` (AI response string), `macro-finished` (macro id), `macro-error` (id, message).

---

## Project layout

| Path | Purpose |
|------|---------|
| `src/` | Vite + React frontend (`App.tsx`, `App.css`, `main.tsx`) |
| `src-tauri/src/lib.rs` | Tauri commands, app state, window lifecycle |
| `src-tauri/src/config.rs` | Config, config dir, Ollama URL validation |
| `src-tauri/src/game.rs` | Game detection (sysinfo) |
| `src-tauri/src/ollama.rs` | Ollama API client (list models) |
| `src-tauri/src/profile.rs` | Game profiles (game_profiles.json) |
| `src-tauri/src/macros.rs` | Macro store and execution (enigo) |
| `src-tauri/src/keybind.rs` | Keybind config |
| `src-tauri/src/knowledge.rs` | TF-IDF index and search |
| `src-tauri/src/session.rs` | Session event log |

---

## For AI assistants and contributors

See **[CLAUDE.md](./CLAUDE.md)** in this directory for an AI-oriented guide: architecture, backend modules, frontend structure, commands/events, data paths, and conventions.

---

## Related

- Legacy Python/PyQt6 Omnix: see repository root `README.md`, `CLAUDE.md`, and `AGENTS.md`.
- CI: `.github/workflows/omnix-tauri-ci.yml` (Rust check, frontend build).
