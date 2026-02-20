use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::path::PathBuf;
use sysinfo::{ProcessesToUpdate, System};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct GameInfo {
    pub name: String,
    pub exe: String,
    pub process_name: String,
    pub pid: u32,
    pub path: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub version: Option<String>,
}

pub struct GameDetector {
    process_index: HashMap<String, String>,
    sys: System,
    _config_dir: PathBuf,
}

impl GameDetector {
    pub fn new(config_dir: PathBuf) -> Self {
        let mut process_index = HashMap::new();
        let common_games: &[(&str, &[&str])] = &[
            ("League of Legends", &["LeagueClientUx.exe", "League of Legends.exe"][..]),
            ("Valorant", &["VALORANT.exe", "valorant.exe"][..]),
            ("Counter-Strike 2", &["cs2.exe", "csgo.exe"][..]),
            ("Dota 2", &["dota2.exe"][..]),
            ("World of Warcraft", &["Wow.exe", "WowClassic.exe"][..]),
            ("Minecraft", &["Minecraft.exe", "MinecraftLauncher.exe"][..]),
            ("Fortnite", &["FortniteClient-Win64-Shipping.exe"][..]),
            ("PUBG", &["TslGame.exe"][..]),
            ("Elden Ring", &["eldenring.exe"][..]),
            ("Dark Souls III", &["DarkSoulsIII.exe"][..]),
            ("Baldur's Gate 3", &["bg3.exe"][..]),
            ("Cyberpunk 2077", &["Cyberpunk2077.exe"][..]),
            ("GTA V", &["GTA5.exe", "gtavicecity.exe"][..]),
        ];
        for (game_name, process_names) in common_games {
            for process_name in *process_names {
                process_index.insert(process_name.to_lowercase(), (*game_name).to_string());
            }
        }
        Self {
            process_index,
            sys: System::new(), // Don't use new_all() here: it blocks 30+ seconds on Windows
            _config_dir: config_dir,
        }
    }

    pub fn current_game(&mut self) -> Option<GameInfo> {
        self.sys.refresh_processes(ProcessesToUpdate::All);
        for (pid, process) in self.sys.processes() {
            let name = process.name();
            let name_lower = name.to_string_lossy().to_lowercase();
            if let Some(game_name) = self.process_index.get(&name_lower) {
                let exe_path = process.exe().map(|p| p.display().to_string()).unwrap_or_default();
                return Some(GameInfo {
                    name: game_name.clone(),
                    exe: exe_path.clone(),
                    process_name: name.to_string_lossy().into_owned(),
                    pid: pid.as_u32(),
                    path: exe_path,
                    version: None,
                });
            }
        }
        None
    }
}
