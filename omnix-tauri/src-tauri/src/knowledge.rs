//! Simple TF-IDF knowledge index per game. Store chunks and search for relevant context.

use regex::Regex;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::path::PathBuf;

const INDEX_DIR: &str = "knowledge_index";
const INDEX_FILE: &str = "index.json";

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

fn index_dir() -> PathBuf {
    crate::config::AppConfig::config_dir().join(INDEX_DIR)
}

fn load_index() -> IndexData {
    let path = index_dir().join(INDEX_FILE);
    if path.exists() {
        if let Ok(data) = std::fs::read_to_string(&path) {
            if let Ok(idx) = serde_json::from_str::<IndexData>(&data) {
                return idx;
            }
        }
    }
    IndexData::default()
}

fn save_index(data: &IndexData) -> Result<(), String> {
    let dir = index_dir();
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

pub fn add_chunks(_game_profile_id: &str, chunks: Vec<KnowledgeChunk>) -> Result<(), String> {
    let mut data = load_index();
    let mut vocab = data.vocabulary.clone();
    let mut next_idx = vocab.len();
    for token in chunks.iter().flat_map(|c| tokenize(&c.text)) {
        vocab.entry(token).or_insert_with(|| {
            let i = next_idx;
            next_idx += 1;
            i
        });
    }
    let idf = build_idf(&data.docs, &vocab);
    for chunk in chunks {
        let tokens = tokenize(&chunk.text);
        let tf_map = tf(&tokens);
        let mut vec = vec![0.0; vocab.len()];
        for (token, tf_val) in tf_map {
            if let Some(&idx) = vocab.get(&token) {
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
        data.docs.push((chunk, vec));
    }
    data.vocabulary = vocab;
    data.idf = build_idf(&data.docs, &data.vocabulary);
    save_index(&data)
}

pub fn search(query: &str, top_k: usize) -> Result<Vec<String>, String> {
    let data = load_index();
    if data.docs.is_empty() {
        return Ok(Vec::new());
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
    Ok(scored.into_iter().take(top_k).map(|(_, t)| t).collect())
}
