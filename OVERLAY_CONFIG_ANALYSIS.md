# Overlay Configuration Persistence Analysis

## Investigation Date: 2025-11-21

## Summary
✅ **Config persistence is working correctly**

The overlay position and size persistence system is functioning as designed. The initial concern about `config.save()` not working due to unset `config_path` is not an issue because the overlay uses the static method `Config.save_to_env()` which writes directly to `.env`.

## How It Works

### 1. Overlay Event Handlers (src/gui.py)

The `OverlayWindow` class has three event handlers that track changes:

```python
def moveEvent(self, event: QEvent) -> None:
    """Save overlay position when moved"""
    super().moveEvent(event)
    self.config.overlay_x = self.x()
    self.config.overlay_y = self.y()
    # Don't save immediately to avoid excessive I/O during drag
    logger.debug(f"Overlay moved to ({self.x()}, {self.y()})")

def resizeEvent(self, event: QEvent) -> None:
    """Save overlay size when resized"""
    super().resizeEvent(event)
    if not self.minimized:
        self.config.overlay_width = self.width()
        self.config.overlay_height = self.height()
        logger.debug(f"Overlay resized to ({self.width()}x{self.height()})")

def closeEvent(self, event: QEvent) -> None:
    """Save config when overlay is closed"""
    super().closeEvent(event)
    self._save_overlay_config()
```

### 2. Configuration Persistence (src/gui.py)

The `_save_overlay_config()` method persists settings to disk:

```python
def _save_overlay_config(self) -> None:
    """Persist overlay configuration to .env"""
    try:
        Config.save_to_env(
            provider=self.config.ai_provider,
            session_tokens=self.config.session_tokens,
            overlay_hotkey=self.config.overlay_hotkey,
            check_interval=self.config.check_interval,
            overlay_x=self.config.overlay_x,
            overlay_y=self.config.overlay_y,
            overlay_width=self.config.overlay_width,
            overlay_height=self.config.overlay_height,
            overlay_minimized=self.config.overlay_minimized,
            overlay_opacity=self.config.overlay_opacity
        )
        logger.info("Overlay configuration saved")
    except Exception as e:
        logger.error(f"Failed to save overlay config: {e}")
```

### 3. Config.save_to_env() Implementation (src/config.py)

This is a **static method** that writes directly to `.env`:

```python
@staticmethod
def save_to_env(provider: str, session_tokens: Optional[Dict[str, dict]] = None,
                overlay_hotkey: str = 'ctrl+shift+g', check_interval: int = 5,
                overlay_x: int = None, overlay_y: int = None,
                overlay_width: int = None, overlay_height: int = None,
                overlay_minimized: bool = None, overlay_opacity: float = None):
    """Save configuration to .env file"""
    # Determines .env location (project root or exe directory)
    env_path = Path(__file__).parent.parent / '.env'

    # Writes all settings to .env file
    # Including overlay_x, overlay_y, overlay_width, overlay_height, etc.
```

### 4. Configuration Loading (src/config.py)

On application start, `Config.__init__()` loads settings from `.env`:

```python
def __init__(self, env_file: Optional[str] = None, require_keys: bool = False,
             config_path: Optional[str] = None, config_dir: Optional[str] = None):
    # Loads .env file
    load_dotenv(env_path, override=True)

    # Loads overlay settings from environment variables
    self.overlay_x = int(os.getenv('OVERLAY_X', '100'))
    self.overlay_y = int(os.getenv('OVERLAY_Y', '100'))
    self.overlay_width = int(os.getenv('OVERLAY_WIDTH', '900'))
    self.overlay_height = int(os.getenv('OVERLAY_HEIGHT', '700'))
    self.overlay_minimized = os.getenv('OVERLAY_MINIMIZED', 'false').lower() == 'true'
    self.overlay_opacity = max(0.0, min(1.0, float(os.getenv('OVERLAY_OPACITY', '0.95'))))
```

## Testing

### Test 1: Persistence Test
✅ **Passed** - `test_config_persistence.py`

Verified that `Config.save_to_env()` correctly writes overlay settings to `.env`:

```
OVERLAY_X=100
OVERLAY_Y=200
OVERLAY_WIDTH=800
OVERLAY_HEIGHT=600
OVERLAY_MINIMIZED=false
OVERLAY_OPACITY=0.95
```

### Test 2: Loading Test
✅ **Passed** - `test_config_loading.py`

Verified that `Config.__init__()` correctly loads overlay settings from `.env`:

```
Loaded config:
  overlay_x: 100
  overlay_y: 200
  overlay_width: 800
  overlay_height: 600
  overlay_minimized: False
  overlay_opacity: 0.95
```

### Test 3: GUI Tests
✅ **Passed** - `tests/test_gui.py`

The existing GUI tests use `pytest-qt` which automatically provides a `QApplication` instance via the `qtbot` fixture. No changes needed.

## Architecture Notes

### Why Two Save Methods?

The `Config` class has two different save mechanisms:

1. **`config.save()`** - Instance method that requires `config_path` to be set
   - Used for JSON-based configuration
   - Returns `False` if `config_path` is not set
   - This is the method that logs "No config_path set, cannot save configuration"

2. **`Config.save_to_env()`** - Static method that writes to `.env`
   - Used by overlay and settings dialog
   - Always writes to `.env` file
   - Does NOT require `config_path`
   - **This is the method actually used by the overlay**

### When Settings Are Saved

The overlay saves settings in `closeEvent()` only, not during `moveEvent()` or `resizeEvent()`. This is intentional:

```python
# moveEvent and resizeEvent update config object but DON'T save to disk
def moveEvent(self, event: QEvent) -> None:
    self.config.overlay_x = self.x()
    self.config.overlay_y = self.y()
    # Don't save immediately to avoid excessive I/O during drag

# Only closeEvent triggers disk write
def closeEvent(self, event: QEvent) -> None:
    self._save_overlay_config()  # <-- Saves to .env
```

**Rationale:** Saving on every move/resize event would cause excessive disk I/O during dragging. Instead, settings are updated in memory and persisted only when the window closes.

## Recommendations

### Current Implementation: ✅ Working Correctly

The current implementation is sound and follows best practices:
- ✅ Minimal disk I/O (only on close)
- ✅ Settings persist across restarts
- ✅ Uses appropriate save method (static `save_to_env()`)
- ✅ Proper error handling

### Optional Enhancements (Not Required)

If you want to make the system more robust, consider these optional improvements:

1. **Auto-save timer** (low priority):
   ```python
   # Add periodic auto-save every 30 seconds
   self.autosave_timer = QTimer()
   self.autosave_timer.timeout.connect(self._save_overlay_config)
   self.autosave_timer.start(30000)  # 30 seconds
   ```

2. **Save on minimize** (low priority):
   ```python
   def toggle_minimize(self) -> None:
       self.minimized = not self.minimized
       self.config.overlay_minimized = self.minimized
       # ... existing code ...
       self._save_overlay_config()  # Save when minimized state changes
   ```

3. **Debounced save during resize** (low priority):
   ```python
   # Save 1 second after last resize
   self.resize_timer = QTimer()
   self.resize_timer.setSingleShot(True)
   self.resize_timer.timeout.connect(self._save_overlay_config)

   def resizeEvent(self, event: QEvent) -> None:
       super().resizeEvent(event)
       if not self.minimized:
           self.config.overlay_width = self.width()
           self.config.overlay_height = self.height()
           self.resize_timer.start(1000)  # Debounce 1 second
   ```

## Conclusion

**No bugs found.** The overlay configuration persistence system is working as designed.

The initial concern about `config.save()` not working due to unset `config_path` is not applicable because the overlay uses the static method `Config.save_to_env()`, which does not require `config_path` and writes directly to the `.env` file.

### What Actually Happens:

1. User moves/resizes overlay → Config object updated in memory
2. User closes overlay → `closeEvent()` triggered
3. `_save_overlay_config()` called → `Config.save_to_env()` executed
4. Settings written to `.env` file
5. Next app start → Config loads settings from `.env`
6. Overlay opens at saved position/size ✅

---

**Tested by:** Claude (AI Assistant)
**Date:** 2025-11-21
**Status:** ✅ System working correctly, no changes needed
