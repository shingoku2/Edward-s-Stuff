use std::path::PathBuf;

fn main() {
    // Generate icon.ico from PNG if missing (required for Windows build)
    let out_dir = PathBuf::from(std::env::var("CARGO_MANIFEST_DIR").unwrap());
    let icons_dir = out_dir.join("icons");
    let ico_path = icons_dir.join("icon.ico");
    let png_path = icons_dir.join("32x32.png");

    if !ico_path.exists() && png_path.exists() {
        if let Ok(png_file) = std::fs::File::open(&png_path) {
            if let Ok(icon_img) = ico::IconImage::read_png(png_file) {
                let mut icon_dir = ico::IconDir::new(ico::ResourceType::Icon);
                if let Ok(entry) = ico::IconDirEntry::encode(&icon_img) {
                    icon_dir.add_entry(entry);
                    if let Ok(ico_file) = std::fs::File::create(&ico_path) {
                        let _ = icon_dir.write(ico_file);
                    }
                }
            }
        }
    }

    tauri_build::build()
}
