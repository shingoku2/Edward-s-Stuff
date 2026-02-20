use serde::Deserialize;

pub struct OllamaClient {
    base_url: String,
}

#[derive(Deserialize)]
struct ModelsResponse {
    models: Option<Vec<ModelInfo>>,
}

#[derive(Deserialize)]
struct ModelInfo {
    name: Option<String>,
}

impl OllamaClient {
    pub fn new(base_url: String) -> Self {
        Self {
            base_url: base_url.trim_end_matches('/').to_string(),
        }
    }

    pub fn list_models(&self) -> Result<Vec<String>, String> {
        let client = reqwest::blocking::Client::new();
        let url = format!("{}/api/tags", self.base_url);
        let resp = client.get(&url).send().map_err(|e: reqwest::Error| e.to_string())?;
        if !resp.status().is_success() {
            return Err(format!("Ollama returned {}", resp.status()));
        }
        let body: ModelsResponse = resp.json().map_err(|e: reqwest::Error| e.to_string())?;
        let names = body
            .models
            .unwrap_or_default()
            .into_iter()
            .filter_map(|m| m.name)
            .collect();
        Ok(names)
    }
}
