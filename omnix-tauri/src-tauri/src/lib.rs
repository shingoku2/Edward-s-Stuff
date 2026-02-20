#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

mod config;
mod game;
mod keybind;
mod knowledge;
mod macros;
mod ollama;
mod profile;
mod session;
mod hrm;

use config::AppConfig;
use game::GameDetector;
use keybind::KeybindConfig;
use ollama::OllamaClient;
use std::sync::Mutex;
use tauri::{AppHandle, Emitter, Manager, State};

pub struct AppState {
    pub config: Mutex<AppConfig>,
    pub game_detector: Mutex<GameDetector>,
    pub ollama: Mutex<OllamaClient>,
}

#[tauri::command]
fn get_config(state: State<AppState>) -> Result<AppConfig, String> {
    state.config.lock().map_err(|e| e.to_string()).map(|g| g.clone())
}

#[tauri::command]
fn save_settings(state: State<AppState>, settings: serde_json::Value) -> Result<(), String> {
    let mut config = state.config.lock().map_err(|e| e.to_string())?;
    if let Some(ai) = settings.get("ai") {
        if let Some(v) = ai.get("provider") {
            config.ai_provider = v.as_str().unwrap_or(&config.ai_provider).to_string();
        }
        if let Some(v) = ai.get("model") {
            config.ollama_model = v.as_str().unwrap_or(&config.ollama_model).to_string();
        }
        if let Some(v) = ai.get("base_url") {
            if let Some(s) = v.as_str() {
                config::validate_ollama_base_url(s)?;
                config.ollama_base_url = s.to_string();
            }
        }
    }
    if let Some(ui) = settings.get("ui") {
        if let Some(v) = ui.get("opacity") {
            if let Some(f) = v.as_f64() {
                config.overlay_opacity = f as f32;
            }
        }
        if let Some(v) = ui.get("theme") {
            config.theme = v.as_str().unwrap_or(&config.theme).to_string();
        }
    }
    config.save().map_err(|e| e.to_string())
}

#[tauri::command]
async fn send_message(
    state: State<'_, AppState>,
    app: AppHandle,
    message: String,
) -> Result<(), String> {
    let config = state.config.lock().map_err(|e| e.to_string())?.clone();
    config::validate_ollama_base_url(&config.ollama_base_url)
        .map_err(|e| format!("Invalid Ollama URL: {}", e))?;
    let ollama_url = config.ollama_base_url.clone();
    let model = config.ollama_model.clone();
    let current_game = state.game_detector.lock().ok().and_then(|mut d| d.current_game());
    let game_context = current_game
        .as_ref()
        .map(|g| format!("The user is currently playing: {}. Give relevant, game-specific advice when possible.", g.name))
        .unwrap_or_else(|| "The user may or may not be in a game; answer generally as a gaming assistant.".to_string());

    let context_chunks = knowledge::search(&message, 5).unwrap_or_default();
    let context = if context_chunks.is_empty() {
        message.clone()
    } else {
        let ctx = context_chunks.join("\n\n");
        format!("Relevant context from knowledge base:\n{ctx}\n\nUser question: {message}")
    };
    let system_prompt = match hrm::reasoning_prefix_for_question(&message) {
        Some(prefix) => format!("You are a helpful gaming assistant. {game_context} Use any provided context to inform your answer. {prefix}"),
        None => format!("You are a helpful gaming assistant. {game_context} Use any provided context to inform your answer."),
    };
    session::log_event("user_message", &message);
    tauri::async_runtime::spawn(async move {
        let client = reqwest::Client::new();
        let url = format!("{}/api/chat", ollama_url.trim_end_matches('/'));
        let body = serde_json::json!({
            "model": model,
            "messages": [
                { "role": "system", "content": system_prompt },
                { "role": "user", "content": context }
            ],
            "stream": false
        });
        match client.post(&url).json(&body).send().await {
            Ok(resp) => {
                if resp.status().is_success() {
                    if let Ok(json) = resp.json::<serde_json::Value>().await {
                        let content = json
                            .get("message")
                            .and_then(|m| m.get("content"))
                            .and_then(|c| c.as_str())
                            .unwrap_or("")
                            .to_string();
                        let _ = app.emit("message-received", content.clone());
                        session::log_event("assistant_response", &content);
                    }
                } else {
                    let _ = app.emit("message-received", format!("Error: {}", resp.status()));
                }
            }
            Err(e) => {
                let _ = app.emit("message-received", format!("Error: {}", e));
            }
        }
    });
    Ok(())
}

#[tauri::command]
fn get_detected_game(state: State<AppState>) -> Result<Option<game::GameInfo>, String> {
    let mut detector = state.game_detector.lock().map_err(|e| e.to_string())?;
    Ok(detector.current_game())
}

#[tauri::command]
fn get_running_processes(state: State<AppState>) -> Result<Vec<String>, String> {
    let mut detector = state.game_detector.lock().map_err(|e| e.to_string())?;
    Ok(detector.running_process_names())
}

#[tauri::command]
async fn list_ollama_models(state: State<'_, AppState>) -> Result<Vec<String>, String> {
    let url = state.config.lock().map_err(|e| e.to_string())?.ollama_base_url.clone();
    let inner = tauri::async_runtime::spawn_blocking(move || {
        let client = OllamaClient::new(url);
        client.list_models().map_err(|e| e.to_string())
    })
    .await
    .map_err(|e| e.to_string())?;
    inner
}

#[tauri::command]
fn get_game_profiles() -> Result<Vec<profile::GameProfile>, String> {
    let dir = config::AppConfig::config_dir();
    let store = profile::GameProfileStore::load(&dir)?;
    Ok(store.profiles)
}

#[tauri::command]
fn save_game_profile(profile: profile::GameProfile) -> Result<(), String> {
    let dir = config::AppConfig::config_dir();
    let mut store = profile::GameProfileStore::load(&dir)?;
    if let Some(pos) = store.profiles.iter().position(|p| p.id == profile.id) {
        store.profiles[pos] = profile;
    } else {
        store.profiles.push(profile);
    }
    store.save(&dir)
}

#[tauri::command]
fn delete_game_profile(id: String) -> Result<(), String> {
    let dir = config::AppConfig::config_dir();
    let mut store = profile::GameProfileStore::load(&dir)?;
    store.profiles.retain(|p| p.id != id);
    store.save(&dir)
}

#[tauri::command]
fn get_macros() -> Result<Vec<macros::Macro>, String> {
    macros::get_macros()
}

#[tauri::command]
fn save_macro(macro_data: macros::Macro) -> Result<(), String> {
    macros::save_macro(macro_data)
}

#[tauri::command]
fn delete_macro(id: String) -> Result<(), String> {
    macros::delete_macro(&id)
}

#[tauri::command]
fn execute_macro(app: AppHandle, macro_data: macros::Macro) -> Result<(), String> {
    let id = macro_data.id.clone();
    tauri::async_runtime::spawn_blocking(move || {
        let result = macros::execute_macro(macro_data);
        let _ = match result {
            Ok(()) => app.emit("macro-finished", id),
            Err(e) => app.emit("macro-error", (id, e)),
        };
    });
    Ok(())
}

#[tauri::command]
fn knowledge_search(query: String, top_k: Option<usize>) -> Result<Vec<String>, String> {
    knowledge::search(&query, top_k.unwrap_or(5))
}

#[tauri::command]
fn knowledge_add_chunks(game_profile_id: String, chunks: Vec<knowledge::KnowledgeChunk>) -> Result<(), String> {
    knowledge::add_chunks(&game_profile_id, chunks)
}

#[tauri::command]
fn get_keybinds() -> Result<KeybindConfig, String> {
    Ok(KeybindConfig::load())
}

#[tauri::command]
fn save_keybinds(config: KeybindConfig) -> Result<(), String> {
    config.save()
}

#[tauri::command]
async fn toggle_overlay(app: AppHandle) -> Result<(), String> {
    if let Some(overlay) = app.get_webview_window("overlay") {
        if overlay.is_visible().unwrap_or(false) {
            overlay.hide().map_err(|e| e.to_string())?;
        } else {
            overlay.show().map_err(|e| e.to_string())?;
            overlay.set_focus().map_err(|e| e.to_string())?;
        }
    } else {
        // Overlay loads the full app (index.html); a minimal overlay route could be used for a lighter window.
        tauri::WebviewWindowBuilder::new(&app, "overlay", tauri::WebviewUrl::App("index.html".into()))
            .title("Omnix Overlay")
            .inner_size(400.0, 300.0)
            .decorations(false)
            .transparent(true)
            .set_always_on_top(true)
            .build()
            .map_err(|e| e.to_string())?;
    }
    Ok(())
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    let config = AppConfig::load().unwrap_or_else(|_| AppConfig::default());
    let config_dir = AppConfig::config_dir();
    let game_detector = GameDetector::new(config_dir.clone());
    let ollama = OllamaClient::new(config.ollama_base_url.clone());

    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .manage(AppState {
            config: Mutex::new(config),
            game_detector: Mutex::new(game_detector),
            ollama: Mutex::new(ollama),
        })
        .invoke_handler(tauri::generate_handler![
            get_config,
            save_settings,
            send_message,
            get_detected_game,
            get_running_processes,
            list_ollama_models,
            get_game_profiles,
            save_game_profile,
            delete_game_profile,
            get_macros,
            save_macro,
            delete_macro,
            execute_macro,
            knowledge_search,
            knowledge_add_chunks,
            get_keybinds,
            save_keybinds,
            toggle_overlay,
        ])
        .setup(|_app| Ok(()))
        .on_window_event(|window, event| {
            if let tauri::WindowEvent::CloseRequested { .. } = event {
                if window.label() == "main" {
                    window.app_handle().exit(0);
                }
            }
        })
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
