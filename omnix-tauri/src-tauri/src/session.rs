//! Session logging: append events to session.jsonl under ~/.gaming_ai_assistant/logs

use serde::Serialize;
use std::path::PathBuf;

const LOGS_DIR: &str = "logs";
const SESSION_FILE: &str = "session.jsonl";

fn log_path() -> PathBuf {
    crate::config::AppConfig::config_dir().join(LOGS_DIR).join(SESSION_FILE)
}

#[derive(Serialize)]
struct LogEntry {
    ts: String,
    event: String,
    payload: String,
}

pub fn log_event(event: &str, payload: &str) {
    let path = log_path();
    if let Some(parent) = path.parent() {
        let _ = std::fs::create_dir_all(parent);
    }
    let ts = std::time::SystemTime::now()
        .duration_since(std::time::UNIX_EPOCH)
        .map(|d| d.as_secs_f64())
        .unwrap_or(0.0);
    let entry = LogEntry {
        ts: format!("{:.3}", ts),
        event: event.to_string(),
        payload: payload.to_string(),
    };
    if let Ok(line) = serde_json::to_string(&entry) {
        let _ = std::fs::OpenOptions::new()
            .create(true)
            .append(true)
            .open(&path)
            .and_then(|mut f| std::io::Write::write_fmt(&mut f, format_args!("{}\n", line)));
    }
}
