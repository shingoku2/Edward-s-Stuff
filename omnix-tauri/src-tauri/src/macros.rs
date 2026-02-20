//! Macro definitions, store, and execution (enigo). Compatible with Python macro JSON.

use serde::{Deserialize, Serialize};
use std::path::PathBuf;
use std::sync::atomic::{AtomicBool, Ordering};
use std::time::Duration;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MacroStep {
    #[serde(rename = "type")]
    pub step_type: String, // "key_press", "key_down", "key_up", "delay", "mouse_click", "mouse_move", "mouse_scroll"
    #[serde(default)]
    pub key: Option<String>,
    #[serde(default)]
    pub duration_ms: i64,
    #[serde(default)]
    pub button: Option<String>,
    #[serde(default)]
    pub x: Option<i32>,
    #[serde(default)]
    pub y: Option<i32>,
    #[serde(default)]
    pub scroll_amount: i32,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Macro {
    pub id: String,
    pub name: String,
    #[serde(default)]
    pub description: String,
    #[serde(default)]
    pub steps: Vec<MacroStep>,
    #[serde(default)]
    pub game_profile_id: Option<String>,
    #[serde(default)]
    pub repeat: i32,
    #[serde(default)]
    pub enabled: bool,
}

static MACRO_ABORT: AtomicBool = AtomicBool::new(false);

fn config_dir() -> PathBuf {
    crate::config::AppConfig::config_dir()
}

fn macros_dir() -> PathBuf {
    config_dir().join("macros")
}

/// Validates macro ID: only [a-zA-Z0-9_-]+. Rejects path segments and empty.
fn validate_macro_id(id: &str) -> Result<(), String> {
    if id.is_empty() {
        return Err("Macro ID cannot be empty".to_string());
    }
    if id.contains('/') || id.contains('\\') || id.contains("..") || id.starts_with('.') {
        return Err("Macro ID cannot contain path segments (/, \\, or .)".to_string());
    }
    let valid = id.chars().all(|c| c.is_ascii_alphanumeric() || c == '_' || c == '-');
    if !valid {
        return Err("Macro ID may only contain letters, numbers, underscores, and hyphens [a-zA-Z0-9_-]".to_string());
    }
    Ok(())
}

pub fn get_macros() -> Result<Vec<Macro>, String> {
    let dir = macros_dir();
    if !dir.exists() {
        return Ok(Vec::new());
    }
    let mut out = Vec::new();
    for entry in std::fs::read_dir(&dir).map_err(|e| e.to_string())? {
        let entry = entry.map_err(|e| e.to_string())?;
        let path = entry.path();
        if path.extension().map(|e| e == "json").unwrap_or(false) {
            if let Ok(data) = std::fs::read_to_string(&path) {
                if let Ok(m) = serde_json::from_str::<Macro>(&data) {
                    out.push(m);
                }
            }
        }
    }
    Ok(out)
}

pub fn save_macro(macro_data: Macro) -> Result<(), String> {
    validate_macro_id(&macro_data.id)?;
    let dir = macros_dir();
    std::fs::create_dir_all(&dir).map_err(|e| e.to_string())?;
    let path = dir.join(format!("{}.json", macro_data.id));
    let data = serde_json::to_string_pretty(&macro_data).map_err(|e| e.to_string())?;
    std::fs::write(path, data).map_err(|e| e.to_string())?;
    Ok(())
}

pub fn delete_macro(id: &str) -> Result<(), String> {
    validate_macro_id(id)?;
    let dir = macros_dir();
    let path = dir.join(format!("{}.json", id));
    if path.exists() {
        std::fs::remove_file(path).map_err(|e| e.to_string())?;
    }
    Ok(())
}

pub fn execute_macro(macro_data: Macro) -> Result<(), String> {
    MACRO_ABORT.store(false, Ordering::SeqCst);
    let repeat = macro_data.repeat.max(1).min(10);
    for _ in 0..repeat {
        if MACRO_ABORT.load(Ordering::SeqCst) {
            break;
        }
        for step in &macro_data.steps {
            if MACRO_ABORT.load(Ordering::SeqCst) {
                break;
            }
            run_step(step)?;
        }
    }
    Ok(())
}

pub fn abort_macro() {
    MACRO_ABORT.store(true, Ordering::SeqCst);
}

/// Supported step types: delay, key_press, key_down, key_up, mouse_click, mouse_move, mouse_scroll.
/// Unsupported types return an error instead of no-op.
fn run_step(step: &MacroStep) -> Result<(), String> {
    match step.step_type.as_str() {
        "delay" => {
            let ms = step.duration_ms.max(0) as u64;
            std::thread::sleep(Duration::from_millis(ms));
        }
        "key_press" => {
            if let Some(ref key) = step.key {
                key_press(key)?;
            }
        }
        "key_down" => {
            if let Some(ref key) = step.key {
                key_down(key)?;
            }
        }
        "key_up" => {
            if let Some(ref key) = step.key {
                key_up(key)?;
            }
        }
        "mouse_click" => {
            let button = step.button.as_deref().unwrap_or("left");
            mouse_click(button)?;
        }
        "mouse_move" => {
            let x = step.x.unwrap_or(0);
            let y = step.y.unwrap_or(0);
            mouse_move(x, y)?;
        }
        "mouse_scroll" => {
            mouse_scroll(step.scroll_amount)?;
        }
        other => {
            return Err(format!("Unsupported macro step type: {}", other));
        }
    }
    Ok(())
}

fn key_press(key: &str) -> Result<(), String> {
    use enigo::{Direction, Enigo, Keyboard, Settings};
    let mut enigo = Enigo::new(&Settings::default()).map_err(|e| e.to_string())?;
    let (modifiers, main_key) = parse_key(key);
    for m in &modifiers {
        enigo.key(key_from_str(m), Direction::Press).map_err(|e| e.to_string())?;
    }
    enigo.key(key_from_str(&main_key), Direction::Click).map_err(|e| e.to_string())?;
    for m in modifiers.iter().rev() {
        enigo.key(key_from_str(m), Direction::Release).map_err(|e| e.to_string())?;
    }
    Ok(())
}

fn key_down(key: &str) -> Result<(), String> {
    use enigo::{Direction, Enigo, Keyboard, Settings};
    let (modifiers, main_key) = parse_key(key);
    let mut enigo = Enigo::new(&Settings::default()).map_err(|e| e.to_string())?;
    for m in &modifiers {
        enigo.key(key_from_str(m), Direction::Press).map_err(|e| e.to_string())?;
    }
    enigo.key(key_from_str(&main_key), Direction::Press).map_err(|e| e.to_string())?;
    Ok(())
}

fn key_up(key: &str) -> Result<(), String> {
    use enigo::{Direction, Enigo, Keyboard, Settings};
    let (modifiers, main_key) = parse_key(key);
    let mut enigo = Enigo::new(&Settings::default()).map_err(|e| e.to_string())?;
    enigo.key(key_from_str(&main_key), Direction::Release).map_err(|e| e.to_string())?;
    for m in modifiers.iter().rev() {
        enigo.key(key_from_str(m), Direction::Release).map_err(|e| e.to_string())?;
    }
    Ok(())
}

fn parse_key(s: &str) -> (Vec<String>, String) {
    let parts: Vec<&str> = s.split('+').map(str::trim).collect();
    let mut mods = Vec::new();
    let mut main = String::new();
    for p in parts {
        let lower = p.to_lowercase();
        if lower == "ctrl" || lower == "control" {
            mods.push("control".to_string());
        } else if lower == "alt" {
            mods.push("alt".to_string());
        } else if lower == "shift" {
            mods.push("shift".to_string());
        } else if lower == "meta" || lower == "win" || lower == "cmd" {
            mods.push("meta".to_string());
        } else {
            main = p.to_string();
        }
    }
    if main.is_empty() && !mods.is_empty() {
        main = mods.pop().unwrap_or_default();
    }
    (mods, main)
}

fn key_from_str(s: &str) -> enigo::Key {
    use enigo::Key;
    match s.to_lowercase().as_str() {
        "control" | "ctrl" => Key::Control,
        "alt" => Key::Alt,
        "shift" => Key::Shift,
        "meta" | "win" | "cmd" => Key::Meta,
        "enter" | "return" => Key::Return,
        "tab" => Key::Tab,
        "backspace" => Key::Backspace,
        "escape" | "esc" => Key::Escape,
        "space" => Key::Space,
        "up" => Key::UpArrow,
        "down" => Key::DownArrow,
        "left" => Key::LeftArrow,
        "right" => Key::RightArrow,
        other => {
            if other.len() == 1 {
                Key::Unicode(other.chars().next().unwrap())
            } else {
                Key::Unicode('?')
            }
        }
    }
}

fn mouse_click(button: &str) -> Result<(), String> {
    use enigo::{Button, Direction, Enigo, Mouse, Settings};
    let b = match button.to_lowercase().as_str() {
        "right" => Button::Right,
        "middle" => Button::Middle,
        _ => Button::Left,
    };
    let mut enigo = Enigo::new(&Settings::default()).map_err(|e| e.to_string())?;
    enigo.button(b, Direction::Press).map_err(|e| e.to_string())?;
    enigo.button(b, Direction::Release).map_err(|e| e.to_string())?;
    Ok(())
}

/// Moves mouse to absolute coordinates (x, y). Uses platform coordinate system (pixels).
fn mouse_move(x: i32, y: i32) -> Result<(), String> {
    use enigo::{Coordinate, Enigo, Mouse, Settings};
    let mut enigo = Enigo::new(&Settings::default()).map_err(|e| e.to_string())?;
    enigo.move_mouse(x, y, Coordinate::Abs).map_err(|e| e.to_string())?;
    Ok(())
}

/// Scrolls vertically. Positive = down, negative = up (platform-dependent).
fn mouse_scroll(length: i32) -> Result<(), String> {
    use enigo::{Axis, Enigo, Mouse, Settings};
    let mut enigo = Enigo::new(&Settings::default()).map_err(|e| e.to_string())?;
    enigo.scroll(length, Axis::Vertical).map_err(|e| e.to_string())?;
    Ok(())
}
