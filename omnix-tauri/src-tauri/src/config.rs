use serde::{Deserialize, Serialize};
use std::path::PathBuf;

const CONFIG_DIR_NAME: &str = ".gaming_ai_assistant";
const CONFIG_FILE: &str = "config.json";
const DEFAULT_OLLAMA_URL: &str = "http://localhost:11434";
const DEFAULT_OLLAMA_MODEL: &str = "llama3";
const DEFAULT_OVERLAY_OPACITY: f32 = 0.95;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AppConfig {
    pub ai_provider: String,
    pub ollama_base_url: String,
    pub ollama_model: String,
    pub overlay_opacity: f32,
    pub theme: String,
}

impl Default for AppConfig {
    fn default() -> Self {
        Self {
            ai_provider: "ollama".to_string(),
            ollama_base_url: DEFAULT_OLLAMA_URL.to_string(),
            ollama_model: DEFAULT_OLLAMA_MODEL.to_string(),
            overlay_opacity: DEFAULT_OVERLAY_OPACITY,
            theme: "dark".to_string(),
        }
    }
}

impl AppConfig {
    pub fn config_dir() -> PathBuf {
        let home = std::env::var("HOME")
            .or_else(|_| std::env::var("USERPROFILE"))
            .unwrap_or_else(|_| ".".to_string());
        PathBuf::from(home).join(CONFIG_DIR_NAME)
    }

    pub fn load() -> Result<Self, Box<dyn std::error::Error + Send + Sync>> {
        let _ = dotenvy::dotenv();
        let mut config = Self::default();
        if let Ok(v) = std::env::var("OLLAMA_HOST") {
            config.ollama_base_url = v;
        }
        if let Ok(v) = std::env::var("OLLAMA_BASE_URL") {
            config.ollama_base_url = v;
        }
        if let Ok(v) = std::env::var("OLLAMA_MODEL") {
            config.ollama_model = v;
        }
        let path = Self::config_dir().join(CONFIG_FILE);
        if path.exists() {
            let data = std::fs::read_to_string(&path)?;
            if let Ok(loaded) = serde_json::from_str::<AppConfig>(&data) {
                config = loaded;
            }
        }
        Ok(config)
    }

    pub fn save(&self) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
        let dir = Self::config_dir();
        std::fs::create_dir_all(&dir)?;
        let path = dir.join(CONFIG_FILE);
        let data = serde_json::to_string_pretty(self)?;
        std::fs::write(path, data)?;
        Ok(())
    }
}
