# GUI Testing Guide for Omnix Gaming Companion

This guide explains how to test the Omnix Gaming Companion GUI in a headless/CLI environment.

## Overview

The application uses PyQt6 for its graphical interface. In headless environments (servers, Docker, CI/CD), we use Qt's **offscreen platform** to run and test the GUI without a physical display.

## Prerequisites

All dependencies are already installed:
- ✅ PyQt6 and all Python dependencies
- ✅ Qt platform libraries (EGL, XCB, etc.)
- ✅ Xvfb (X Virtual Framebuffer) - optional
- ✅ Offscreen rendering support

## Testing Methods

### Method 1: Offscreen Platform (Recommended)

The offscreen platform renders GUI components in memory without requiring a display server. This is the fastest and most reliable method for headless testing.

```bash
# Run with offscreen platform
export QT_QPA_PLATFORM=offscreen
python main.py
```

**Advantages:**
- No display server required
- Fast startup
- Reliable and stable
- Works in any environment

**Limitations:**
- Cannot capture screenshots
- No visual debugging
- Some platform-specific features may not work

### Method 2: Virtual Display (Xvfb)

Xvfb creates a virtual X11 display server that can be used for more complete GUI testing.

```bash
# Start Xvfb
Xvfb :99 -screen 0 1920x1080x24 &

# Set display
export DISPLAY=:99

# Run application
python main.py

# Clean up
pkill Xvfb
```

**Advantages:**
- Full X11 support
- Can capture screenshots
- More complete GUI testing

**Limitations:**
- Requires X11 libraries
- Slower startup
- More resource intensive

## Quick Start

### Run Minimal GUI Test

Test that the GUI environment is working:

```bash
export QT_QPA_PLATFORM=offscreen
python test_gui_minimal.py
```

Expected output:
```
Initializing QApplication...
Creating main window...
Window created successfully!
Display:
Resolution: 800x800
GUI test passed! ✓
```

### Run Full Application

```bash
# Option 1: Using offscreen platform (recommended)
export QT_QPA_PLATFORM=offscreen
python main.py

# Option 2: Using test script with virtual display
./test_gui.sh
```

## Environment Variables

### Required

```bash
# Use offscreen rendering (recommended for headless)
export QT_QPA_PLATFORM=offscreen

# OR use virtual display
export DISPLAY=:99
```

### Optional

```bash
# Disable Qt warnings
export QT_LOGGING_RULES='*.debug=false;qt.qpa.*=false'

# Force software rendering
export QT_XCB_GL_INTEGRATION=none

# Debug Qt platform loading
export QT_DEBUG_PLUGINS=1
```

## Available Test Scripts

### 1. `test_gui_minimal.py`
Minimal PyQt6 test that verifies the GUI environment.
- Creates a simple window
- Auto-closes after 2 seconds
- Prints system information

```bash
export QT_QPA_PLATFORM=offscreen
python test_gui_minimal.py
```

### 2. `test_gui.sh`
Full application test with virtual display setup.
- Starts Xvfb automatically
- Runs the full application
- Cleans up on exit

```bash
./test_gui.sh
```

### 3. `main.py`
The full Omnix Gaming Companion application.

```bash
export QT_QPA_PLATFORM=offscreen
python main.py
```

## Troubleshooting

### Error: "libEGL.so.1: cannot open shared object file"

**Solution:** Install EGL libraries (already done in this environment)
```bash
apt-get install -y libegl1 libegl-mesa0
```

### Error: "Could not load the Qt platform plugin 'xcb'"

**Solution:** Use offscreen platform instead
```bash
export QT_QPA_PLATFORM=offscreen
```

### Error: "No Qt platform plugin could be initialized"

**Solution:** Check available platforms and choose one
```bash
# List available platforms
python -c "from PyQt6.QtWidgets import QApplication; import sys; app = QApplication(sys.argv)" 2>&1 | grep "Available platform plugins"

# Use offscreen
export QT_QPA_PLATFORM=offscreen
```

### Application hangs or freezes

**Issue:** Qt event loop waiting for user input

**Solution:** The application may be waiting for user interaction. Consider:
- Adding timeout mechanisms for automated testing
- Using QTimer.singleShot() to auto-close dialogs
- Mocking user interactions in tests

## Testing Specific Features

### Test Application Launch

```bash
export QT_QPA_PLATFORM=offscreen
timeout 10 python main.py &
PID=$!
sleep 5
ps -p $PID > /dev/null && echo "✓ Application running" || echo "✗ Application failed"
kill $PID 2>/dev/null
```

### Test UI Components

```python
from PyQt6.QtWidgets import QApplication
from src.gui import OmnixMainWindow

app = QApplication([])
app.setAttribute(Qt.AA_Use96Dpi)

window = OmnixMainWindow()
window.show()

# Test specific features
print(f"Window title: {window.windowTitle()}")
print(f"Window size: {window.size()}")

app.quit()
```

### Test Setup Wizard

```bash
# Remove config to trigger setup wizard
rm -f .env
rm -rf ~/.gaming_ai_assistant/

# Run with offscreen platform
export QT_QPA_PLATFORM=offscreen
python main.py
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: GUI Tests

on: [push, pull_request]

jobs:
  test-gui:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Install dependencies
        run: |
          sudo apt-get update
          sudo apt-get install -y libegl1 libegl-mesa0 libxcb-cursor0
          pip install -r requirements.txt

      - name: Run GUI tests
        env:
          QT_QPA_PLATFORM: offscreen
        run: |
          python test_gui_minimal.py
```

### Docker Example

```dockerfile
FROM python:3.11-slim

# Install Qt dependencies
RUN apt-get update && apt-get install -y \
    libegl1 \
    libegl-mesa0 \
    libxcb-cursor0 \
    libxkbcommon-x11-0 \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Set offscreen platform
ENV QT_QPA_PLATFORM=offscreen

# Copy application
COPY . /app
WORKDIR /app

# Run tests
CMD ["python", "test_gui_minimal.py"]
```

## Best Practices

### For Automated Testing

1. **Always use offscreen platform**
   ```bash
   export QT_QPA_PLATFORM=offscreen
   ```

2. **Add timeouts to prevent hangs**
   ```python
   QTimer.singleShot(5000, app.quit)  # Auto-quit after 5 seconds
   ```

3. **Mock user interactions**
   ```python
   # Simulate button click
   button.click()

   # Process events
   QApplication.processEvents()
   ```

4. **Verify window state**
   ```python
   assert window.isVisible()
   assert window.windowTitle() == "Expected Title"
   ```

### For Manual Testing

1. **Use virtual display for visual debugging**
2. **Capture screenshots with Xvfb**
3. **Use VNC for remote viewing**

## Performance Considerations

### Offscreen Platform
- **Startup:** ~1-2 seconds
- **Memory:** ~50-100 MB
- **CPU:** Minimal

### Xvfb Platform
- **Startup:** ~3-5 seconds
- **Memory:** ~100-200 MB
- **CPU:** Low to moderate

## Platform Support

| Platform | Status | Notes |
|----------|--------|-------|
| **Offscreen** | ✅ Working | Recommended for headless testing |
| **Xvfb (X11)** | ⚠️ Partial | Requires additional setup |
| **Wayland** | ❌ Not tested | May work with wayland-egl |
| **VNC** | ✅ Available | Good for remote debugging |

## Summary

For most headless testing scenarios, use:

```bash
export QT_QPA_PLATFORM=offscreen
python main.py
```

This provides the best balance of compatibility, performance, and reliability.

## Additional Resources

- [Qt Platform Abstraction](https://doc.qt.io/qt-6/qpa.html)
- [PyQt6 Documentation](https://www.riverbankcomputing.com/static/Docs/PyQt6/)
- [Xvfb Manual](https://www.x.org/releases/X11R7.6/doc/man/man1/Xvfb.1.xhtml)

---

**Last Updated:** 2025-11-18
**Environment:** Ubuntu 24.04 (Noble), Python 3.11, PyQt6 6.10.0
