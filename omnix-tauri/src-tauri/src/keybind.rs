//! Keybind config storage. Global hotkey registration (e.g. overlay toggle) can be
//! added later via rdev or platform crates.
//!
//! Note: The overlay hotkey is saved for future use and is not yet active; overlay
//! is opened via the UI button until global hotkey support is implemented.

use serde::{Deserialize, Serialize};
use std::path::PathBuf;

const KEYBINDS_FILE: &str = "keybinds.json";

#[derive(Debug, Default, Clone, Serialize, Deserialize)]
pub struct KeybindConfig {
    #[serde(default)]
    pub overlay_hotkey: String,
}

impl KeybindConfig {
    pub fn path() -> PathBuf {
        crate::config::AppConfig::config_dir().join(KEYBINDS_FILE)
    }

    pub fn load() -> Self {
        let path = Self::path();
        if path.exists() {
            if let Ok(data) = std::fs::read_to_string(&path) {
                if let Ok(c) = serde_json::from_str::<KeybindConfig>(&data) {
                    return c;
                }
            }
        }
        Self {
            overlay_hotkey: "ctrl+shift+g".to_string(),
        }
    }

    pub fn save(&self) -> Result<(), String> {
        let dir = crate::config::AppConfig::config_dir();
        std::fs::create_dir_all(&dir).map_err(|e| e.to_string())?;
        let data = serde_json::to_string_pretty(self).map_err(|e| e.to_string())?;
        std::fs::write(Self::path(), data).map_err(|e| e.to_string())?;
        Ok(())
    }
}
