//! Game profile load/save compatible with Python app (game_profiles.json).

use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::path::PathBuf;

const PROFILES_FILE: &str = "game_profiles.json";

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct GameProfile {
    pub id: String,
    pub display_name: String,
    #[serde(default)]
    pub exe_names: Vec<String>,
    #[serde(default)]
    pub system_prompt: String,
    #[serde(default = "default_provider")]
    pub default_provider: String,
    #[serde(default)]
    pub default_model: Option<String>,
    #[serde(default = "default_overlay_mode")]
    pub overlay_mode_default: String,
    #[serde(default)]
    pub extra_settings: HashMap<String, serde_json::Value>,
    #[serde(default)]
    pub is_builtin: bool,
}

fn default_provider() -> String {
    "ollama".to_string()
}
fn default_overlay_mode() -> String {
    "compact".to_string()
}

impl GameProfile {
    pub fn matches_executable(&self, exe_name: &str) -> bool {
        let exe_lower = exe_name.to_lowercase();
        self.exe_names
            .iter()
            .any(|e| e.to_lowercase() == exe_lower)
    }
}

#[derive(Debug, Default, Serialize, Deserialize)]
pub struct GameProfileStore {
    #[serde(default)]
    pub profiles: Vec<GameProfile>,
}

impl GameProfileStore {
    pub fn path(config_dir: &PathBuf) -> PathBuf {
        config_dir.join(PROFILES_FILE)
    }

    pub fn load(config_dir: &PathBuf) -> Result<Self, String> {
        let path = Self::path(config_dir);
        if !path.exists() {
            return Ok(Self::default());
        }
        let data = std::fs::read_to_string(&path).map_err(|e| e.to_string())?;
        let store: GameProfileStore = serde_json::from_str(&data).map_err(|e| e.to_string())?;
        Ok(store)
    }

    pub fn save(&self, config_dir: &PathBuf) -> Result<(), String> {
        std::fs::create_dir_all(config_dir).map_err(|e| e.to_string())?;
        let path = Self::path(config_dir);
        let data = serde_json::to_string_pretty(self).map_err(|e| e.to_string())?;
        std::fs::write(path, data).map_err(|e| e.to_string())?;
        Ok(())
    }

    pub fn get_by_id(&self, id: &str) -> Option<&GameProfile> {
        self.profiles.iter().find(|p| p.id == id)
    }

    pub fn get_by_exe(&self, exe_name: &str) -> Option<&GameProfile> {
        self.profiles.iter().find(|p| p.matches_executable(exe_name))
    }
}
