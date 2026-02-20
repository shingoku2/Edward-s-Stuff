//! Simple TF-IDF knowledge index per game. Store chunks and search for relevant context.

use regex::Regex;
use serde::{Deserialize, Serialize};
use std::collections::{HashMap, HashSet};
use std::path::PathBuf;

const INDEX_DIR: &str = "knowledge_index";
const INDEX_FILE: &str = "index.json";

/// Safe subdir name for game_profile_id: [a-zA-Z0-9_-]+ only.
fn safe_game_id(game_profile_id: &str) -> Result<String, String> {
    if game_profile_id.is_empty() {
        return Err("game_profile_id cannot be empty".to_string());
    }
    let ok = game_profile_id
        .chars()
        .all(|c| c.is_ascii_alphanumeric() || c == '_' || c == '-');
    if !ok {
        return Err("game_profile_id may only contain [a-zA-Z0-9_-]".to_string());
    }
    if game_profile_id.contains("..") {
        return Err("game_profile_id cannot contain ..".to_string());
    }
    Ok(game_profile_id.to_string())
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct KnowledgeChunk {
    pub id: String,
    pub text: String,
    pub source_id: String,
    pub pack_id: String,
}

#[derive(Debug, Default, Serialize, Deserialize)]
struct IndexData {
    vocabulary: HashMap<String, usize>,
    idf: HashMap<String, f64>,
    docs: Vec<(KnowledgeChunk, Vec<f64>)>,
}

fn tokenize(text: &str) -> Vec<String> {
    let re = Regex::new(r"\w+").unwrap_or_else(|_| Regex::new(r"[a-zA-Z0-9]+").unwrap());
    re.find_iter(text)
        .map(|m| m.as_str().to_lowercase())
        .filter(|s| s.len() > 1)
        .collect()
}

fn tf(tokens: &[String]) -> HashMap<String, f64> {
    let n = tokens.len() as f64;
    if n == 0.0 {
        return HashMap::new();
    }
    let mut counts: HashMap<String, u32> = HashMap::new();
    for t in tokens {
        *counts.entry(t.clone()).or_insert(0) += 1;
    }
    counts
        .into_iter()
        .map(|(k, v)| (k, v as f64 / n))
        .collect()
}

fn index_base_dir() -> PathBuf {
    crate::config::AppConfig::config_dir().join(INDEX_DIR)
}

fn index_dir_for_game(game_profile_id: &str) -> Result<PathBuf, String> {
    let id = safe_game_id(game_profile_id)?;
    Ok(index_base_dir().join(id))
}

fn load_index_for_game(game_profile_id: &str) -> Result<IndexData, String> {
    let dir = index_dir_for_game(game_profile_id)?;
    let path = dir.join(INDEX_FILE);
    if path.exists() {
        if let Ok(data) = std::fs::read_to_string(&path) {
            if let Ok(idx) = serde_json::from_str::<IndexData>(&data) {
                return Ok(idx);
            }
        }
    }
    Ok(IndexData::default())
}

fn save_index_for_game(game_profile_id: &str, data: &IndexData) -> Result<(), String> {
    let dir = index_dir_for_game(game_profile_id)?;
    std::fs::create_dir_all(&dir).map_err(|e| e.to_string())?;
    let path = dir.join(INDEX_FILE);
    let json = serde_json::to_string_pretty(data).map_err(|e| e.to_string())?;
    std::fs::write(path, json).map_err(|e| e.to_string())?;
    Ok(())
}

fn build_idf(docs: &[(KnowledgeChunk, Vec<f64>)], vocabulary: &HashMap<String, usize>) -> HashMap<String, f64> {
    let n = docs.len() as f64;
    if n == 0.0 {
        return HashMap::new();
    }
    let mut df: HashMap<String, u32> = HashMap::new();
    for (_, vec) in docs {
        for (i, &v) in vec.iter().enumerate() {
            if v > 0.0 {
                if let Some(token) = vocabulary.iter().find(|(_, &idx)| idx == i).map(|(k, _)| k.clone()) {
                    *df.entry(token).or_insert(0) += 1;
                }
            }
        }
    }
    df.into_iter()
        .map(|(k, f)| (k, (n / (f as f64 + 1.0)).ln()))
        .collect()
}

/// Build IDF from chunk texts (so new chunks are included when recomputing).
fn build_idf_from_chunks(docs: &[(KnowledgeChunk, Vec<f64>)], vocabulary: &HashMap<String, usize>) -> HashMap<String, f64> {
    let n = docs.len() as f64;
    if n == 0.0 {
        return HashMap::new();
    }
    let mut df: HashMap<String, u32> = HashMap::new();
    for (chunk, _) in docs {
        let tokens: HashSet<String> = tokenize(&chunk.text).into_iter().collect();
        for token in tokens {
            if vocabulary.contains_key(&token) {
                *df.entry(token).or_insert(0) += 1;
            }
        }
    }
    df.into_iter()
        .map(|(k, f)| (k, (n / (f as f64 + 1.0)).ln()))
        .collect()
}

fn doc_vector(chunk: &KnowledgeChunk, vocabulary: &HashMap<String, usize>, idf: &HashMap<String, f64>) -> Vec<f64> {
    let tokens = tokenize(&chunk.text);
    let tf_map = tf(&tokens);
    let mut vec = vec![0.0; vocabulary.len()];
    for (token, tf_val) in tf_map {
        if let Some(&idx) = vocabulary.get(&token) {
            let idf_val = idf.get(&token).copied().unwrap_or(0.0);
            vec[idx] = tf_val * idf_val;
        }
    }
    let norm: f64 = vec.iter().map(|x| x * x).sum::<f64>().sqrt();
    if norm > 0.0 {
        for v in &mut vec {
            *v /= norm;
        }
    }
    vec
}

pub fn add_chunks(game_profile_id: &str, chunks: Vec<KnowledgeChunk>) -> Result<(), String> {
    if chunks.is_empty() {
        return Ok(());
    }
    let mut data = load_index_for_game(game_profile_id)?;
    let mut vocab = data.vocabulary.clone();
    let mut next_idx = vocab.len();
    for token in chunks.iter().flat_map(|c| tokenize(&c.text)) {
        vocab.entry(token).or_insert_with(|| {
            let i = next_idx;
            next_idx += 1;
            i
        });
    }
    for chunk in chunks {
        data.docs.push((chunk, vec![0.0; vocab.len()]));
    }
    data.vocabulary = vocab.clone();
    data.idf = build_idf_from_chunks(&data.docs, &data.vocabulary);
    let idf = &data.idf;
    for (chunk, vec) in &mut data.docs {
        let new_vec = doc_vector(chunk, &data.vocabulary, idf);
        *vec = new_vec;
    }
    save_index_for_game(game_profile_id, &data)
}

/// Search one game index; returns (score, text).
fn search_one(data: &IndexData, query: &str) -> Vec<(f64, String)> {
    if data.docs.is_empty() {
        return Vec::new();
    }
    let tokens = tokenize(query);
    let tf_map = tf(&tokens);
    let mut qvec = vec![0.0; data.vocabulary.len()];
    for (token, tf_val) in tf_map {
        if let Some(&idx) = data.vocabulary.get(&token) {
            let idf_val = data.idf.get(&token).copied().unwrap_or(0.0);
            qvec[idx] = tf_val * idf_val;
        }
    }
    let norm: f64 = qvec.iter().map(|x| x * x).sum::<f64>().sqrt();
    if norm > 0.0 {
        for v in &mut qvec {
            *v /= norm;
        }
    }
    let mut scored: Vec<(f64, String)> = data
        .docs
        .iter()
        .map(|(chunk, vec)| {
            let sim: f64 = qvec.iter().zip(vec.iter()).map(|(a, b)| a * b).sum();
            (sim, chunk.text.clone())
        })
        .collect();
    scored.sort_by(|a, b| b.0.partial_cmp(&a.0).unwrap_or(std::cmp::Ordering::Equal));
    scored
}

/// Search all game indices and return top_k results globally.
pub fn search(query: &str, top_k: usize) -> Result<Vec<String>, String> {
    let base = index_base_dir();
    if !base.exists() {
        return Ok(Vec::new());
    }
    let mut all: Vec<(f64, String)> = Vec::new();
    for entry in std::fs::read_dir(&base).map_err(|e| e.to_string())? {
        let entry = entry.map_err(|e| e.to_string())?;
        let path = entry.path();
        if path.is_dir() {
            let index_path = path.join(INDEX_FILE);
            if index_path.exists() {
                if let Ok(data) = std::fs::read_to_string(&index_path) {
                    if let Ok(idx) = serde_json::from_str::<IndexData>(&data) {
                        all.extend(search_one(&idx, query));
                    }
                }
            }
        }
    }
    all.sort_by(|a, b| b.0.partial_cmp(&a.0).unwrap_or(std::cmp::Ordering::Equal));
    Ok(all.into_iter().take(top_k).map(|(_, t)| t).collect())
}
