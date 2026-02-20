# Omnix (Tauri)

Omnix Gaming Companion rebuilt with **Rust** and **Tauri 2**. Same data directory as the Python app (`~/.gaming_ai_assistant` on Unix, `%USERPROFILE%\.gaming_ai_assistant` on Windows) for migration.

## Prerequisites

- **Node.js** 18+ and npm
- **Rust** (rustup) and a C++ build toolchain (Windows: Visual Studio Build Tools)
- **Ollama** running locally (e.g. `ollama serve`, `ollama pull llama3`)

## Setup

```bash
cd omnix-tauri
npm install
```

## Development

```bash
npm run tauri:dev
```

This starts the Vite dev server and the Tauri app. Ensure Ollama is running for chat.

## Build

```bash
npm run tauri:build
```

Produces installers in `src-tauri/target/release/bundle/`. For proper app icons, run:

```bash
npm run tauri icon path/to/your/icon.png
```

## Features

- **Config**: Load/save from `~/.gaming_ai_assistant` (same as Python app)
- **Game detection**: Polls running processes and matches known games (sysinfo)
- **Ollama chat**: Send message, with knowledge context and optional HRM reasoning prefix
- **Settings**: AI model, theme, overlay opacity
- **Overlay**: Toggle overlay window (compact second window)
- **Game profiles**: Load/save `game_profiles.json` (compatible with Python)
- **Macros**: Store and run macros (key press, delay, mouse click) via enigo
- **Macro UI**: List, run, delete macros from the Macros modal
- **Keybinds**: Config stored in `keybinds.json` (global hotkey registration can be added later)
- **Knowledge**: TF-IDF index; search and add chunks; context injected into chat
- **Session**: Events logged to `logs/session.jsonl`
- **HRM**: Template-based reasoning prefix for complex questions

## Commands (Rust)

- `get_config`, `save_settings` – config
- `send_message` – send to Ollama (response via `message-received` event); uses knowledge context and HRM when applicable
- `get_detected_game`, `list_ollama_models`
- `get_game_profiles`, `save_game_profile`
- `get_macros`, `save_macro`, `delete_macro`, `execute_macro`
- `knowledge_search`, `knowledge_add_chunks`
- `toggle_overlay`

## Events

- `message-received` – AI response text (string)

## Project layout

- `src/` – Vite + React frontend
- `src-tauri/` – Rust backend
  - `src/config.rs` – config and user data dir
  - `src/game.rs` – game detection (sysinfo)
  - `src/ollama.rs` – Ollama API client (list models)
  - `src/profile.rs` – game profiles (game_profiles.json)
  - `src/macros.rs` – macro store and execution (enigo)
  - `src/keybind.rs` – keybind config
  - `src/knowledge.rs` – TF-IDF index and search
  - `src/session.rs` – session event log
  - `src/hrm.rs` – reasoning template for complex questions
  - `src/lib.rs` – Tauri commands and app state
