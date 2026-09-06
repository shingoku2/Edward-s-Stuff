# Debounced Overlay Position Saving

## Overview

This feature implements debounced saving of overlay window position and size to reduce I/O operations during drag/resize events.

## Problem

Previously, the overlay window did not automatically save its position and size when moved or resized. This meant:
- User position/size preferences were lost between sessions
- No automatic persistence of window geometry

## Solution

Implemented debounced position/size saving with the following characteristics:

### Key Features

1. **Automatic Saving**: Window position and size are automatically saved when the user moves or resizes the overlay window
2. **Debouncing**: Save operations are debounced with a 500ms delay to prevent excessive I/O during drag operations
3. **Efficient**: Only one save operation occurs after the user stops dragging/resizing

### Technical Implementation

#### Added Components

1. **Debounce Timer** (`_save_timer`):
   - QTimer instance configured as single-shot
   - 500ms delay before triggering save
   - Restarted on each move/resize event

2. **Event Handlers**:
   - `moveEvent()`: Triggered when window is moved
   - `resizeEvent()`: Triggered when window is resized
   - Both handlers restart the debounce timer

3. **Save Method** (`_save_position_and_size()`):
   - Updates config with current geometry
   - Persists configuration to disk
   - Includes error handling and debug logging

#### Code Changes

**File**: `src/omnix/gui.py`

**Changes**:
- Added `QTimer` import
- Added `_save_timer` initialization in `OverlayWindow.__init__()`
- Added `_save_delay_ms = 500` configuration
- Implemented `moveEvent()` handler
- Implemented `resizeEvent()` handler
- Implemented `_save_position_and_size()` method

### How It Works

```
User Drags Window
       ↓
moveEvent() triggered
       ↓
Timer restarted (500ms)
       ↓
User continues dragging
       ↓
moveEvent() triggered again
       ↓
Timer restarted (500ms) ← Cancels previous timer
       ↓
User stops dragging
       ↓
500ms passes
       ↓
Timer fires → _save_position_and_size()
       ↓
Config updated and saved to disk
```

### Benefits

1. **Reduced I/O**: Prevents excessive disk writes during continuous drag operations
2. **User Experience**: Seamless saving without performance impact
3. **Reliability**: Position/size preferences persist across sessions
4. **Efficiency**: Only saves once per drag operation instead of hundreds of times

### Configuration

The debounce delay can be adjusted by modifying `_save_delay_ms` in the `OverlayWindow.__init__()` method:

```python
self._save_delay_ms = 500  # Milliseconds (default: 500ms)
```

### Testing

The feature can be tested by:
1. Running the application
2. Moving or resizing the overlay window
3. Checking the debug logs for save confirmations
4. Restarting the application and verifying the window appears in the last position

### Future Enhancements

Potential improvements:
- Make debounce delay configurable via settings UI
- Add visual feedback when position is saved
- Implement position presets for quick switching
- Add multi-monitor position management

## Related Files

- `src/omnix/gui.py` - Main implementation
- `src/omnix/config.py` - Configuration persistence
- `test_debounce_save.py` - Unit tests

## Author

Implemented by: Claude Code
Date: 2025-11-21
Branch: claude/debounce-save-game-detection-01PA5hbrs3rzfNL98zpLSvmT
