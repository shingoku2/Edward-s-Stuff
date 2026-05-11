#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use std::process::Command;
use tauri::{
    menu::{Menu, MenuItem, PredefinedMenuItem},
    tray::{TrayIconBuilder, TrayIconEvent},
    Manager,
};

fn main() {
    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .plugin(tauri_plugin_notification::init())
        .plugin(tauri_plugin_global_shortcut::Builder::new().build())
        .setup(|app| {
            let show = MenuItem::with_id(app, "show", "Show / Hide", true, None::<&str>)?;
            let overlay = MenuItem::with_id(app, "overlay", "Toggle Overlay", true, None::<&str>)?;
            let quit = MenuItem::with_id(app, "quit", "Quit Omnix", true, None::<&str>)?;
            let sep = PredefinedMenuItem::separator(app)?;
            let menu = Menu::with_items(app, &[&show, &overlay, &sep, &quit])?;

            let _tray = TrayIconBuilder::new()
                .tooltip("OMNIX Gaming Companion")
                .menu(&menu)
                .on_menu_event(|app, event| match event.id.as_ref() {
                    "quit" => std::process::exit(0),
                    "show" => {
                        if let Some(win) = app.get_webview_window("main") {
                            if win.is_visible().unwrap_or(false) {
                                let _ = win.hide();
                            } else {
                                let _ = win.show();
                                let _ = win.set_focus();
                            }
                        }
                    }
                    "overlay" => {
                        if let Some(win) = app.get_webview_window("main") {
                            let _ = win.emit("toggle-overlay", ());
                        }
                    }
                    _ => {}
                })
                .on_tray_icon_event(|tray, event| {
                    if let TrayIconEvent::DoubleClick { .. } = event {
                        let app = tray.app_handle();
                        if let Some(win) = app.get_webview_window("main") {
                            let _ = win.show();
                            let _ = win.set_focus();
                        }
                    }
                })
                .build(app)?;

            let port = std::env::var("OMNIX_PORT").unwrap_or_else(|_| "7432".to_string());
            let dev_mode = std::env::var("OMNIX_DEV_MODE").unwrap_or_default();

            match Command::new("python")
                .args(["-m", "backend.server"])
                .env("OMNIX_PORT", &port)
                .env("OMNIX_DEV_MODE", &dev_mode)
                .spawn()
            {
                Ok(_) => println!("[Omnix] Backend started on port {}", port),
                Err(e) => eprintln!("[Omnix] Failed to start backend: {}", e),
            }

            std::thread::sleep(std::time::Duration::from_millis(2000));
            Ok(())
        })
        .on_window_event(|window, event| {
            if let tauri::WindowEvent::CloseRequested { api, .. } = event {
                let _ = window.hide();
                api.prevent_close();
            }
        })
        .invoke_handler(tauri::generate_handler![])
        .run(tauri::generate_context!())
        .expect("error while running Omnix");
}
