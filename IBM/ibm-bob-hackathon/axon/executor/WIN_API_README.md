# Windows API Integration - README

## Overview

The `win_api.py` module provides Windows-specific functionality for detecting and interacting with application windows. This enables AXON to know which application is currently active, allowing for app-specific optimizations and handlers.

## Purpose

According to the PRD (lines 213-214), Dev 2 needs Win32 app detection to know which app is active for app-specific handlers. This module fulfills that requirement.

## Dependencies

```bash
pip install pywin32 psutil
```

These are included in `requirements.txt`.

## Core Functions

### 1. `get_active_window()` ⭐ MOST IMPORTANT

**Purpose**: Get information about the currently active window.

**Returns**: Dictionary with:
- `hwnd`: Window handle (int)
- `title`: Window title (str)
- `pid`: Process ID (int)
- `process`: Process name (str, e.g., 'chrome.exe')

**Returns `None`** if error occurs or not on Windows.

**Example**:
```python
from executor.win_api import get_active_window

info = get_active_window()
if info:
    print(f"Active app: {info['process']}")
    print(f"Window title: {info['title']}")
    print(f"PID: {info['pid']}")
    print(f"Handle: {info['hwnd']}")
```

**Usage in app_handlers.py**:
```python
# Detect which app is active
active = get_active_window()
if active and active['process'] == 'chrome.exe':
    # Apply Chrome-specific optimizations
    pass
```

### 2. `get_window_title(hwnd)`

Get the title of a window by its handle.

**Args**: `hwnd` (int) - Window handle

**Returns**: Window title (str) or empty string on error

**Example**:
```python
title = get_window_title(12345)
print(f"Window title: {title}")
```

### 3. `get_process_name(pid)`

Get the process name from a process ID.

**Args**: `pid` (int) - Process ID

**Returns**: Process name (str) or None on error

**Example**:
```python
process = get_process_name(1234)
print(f"Process: {process}")  # e.g., 'notepad.exe'
```

### 4. `list_all_windows()`

List all visible windows on the system.

**Returns**: List of dicts, each containing window info (hwnd, title, pid, process)

**Example**:
```python
windows = list_all_windows()
for win in windows:
    print(f"{win['process']}: {win['title']}")
```

**Use case**: Debugging, understanding what windows are open

### 5. `bring_window_to_front(hwnd)`

Bring a window to the foreground.

**Args**: `hwnd` (int) - Window handle

**Returns**: True if successful, False otherwise

**Example**:
```python
if bring_window_to_front(12345):
    print("Window activated")
```

**Use case**: Future features where AXON might need to switch between apps

### 6. `get_window_at_position(x, y)`

Get the window at specific screen coordinates.

**Args**: 
- `x` (int) - X coordinate
- `y` (int) - Y coordinate

**Returns**: Window handle (int) or None

**Example**:
```python
hwnd = get_window_at_position(100, 200)
if hwnd:
    title = get_window_title(hwnd)
    print(f"Window at (100, 200): {title}")
```

**Use case**: Detecting which window is under the mouse cursor

### 7. `is_window_visible(hwnd)`

Check if a window is visible.

**Args**: `hwnd` (int) - Window handle

**Returns**: True if visible, False otherwise

**Example**:
```python
if is_window_visible(12345):
    print("Window is visible")
```

## Error Handling

All functions handle errors gracefully:
- Return `None`, empty string, empty list, or `False` on error
- Log errors using Python's logging module
- Check if running on Windows before attempting Win32 API calls
- Handle missing dependencies (pywin32, psutil)

## Testing

### Manual Testing

1. **Install dependencies**:
   ```bash
   pip install pywin32 psutil
   ```

2. **Run the test script**:
   ```bash
   cd axon
   python test_win_api.py
   ```

3. **Test scenarios**:
   - Get active window info
   - Switch between apps (Chrome, VS Code, etc.)
   - Verify detection works correctly
   - Test edge cases (no active window, permission issues)

### Quick Test

```python
from executor.win_api import get_active_window

# Get current active window
info = get_active_window()
if info:
    print(f"✓ Active: {info['process']} - {info['title']}")
else:
    print("✗ Failed to detect active window")
```

## Integration with app_handlers.py

The `app_handlers.py` module uses `get_active_window()` to detect which application is currently active:

```python
from executor.win_api import get_active_window

def get_app_specific_handler():
    """Get handler for the currently active app."""
    active = get_active_window()
    
    if not active:
        return None
    
    process = active['process'].lower()
    
    # App-specific handlers
    if 'chrome' in process or 'firefox' in process:
        return browser_handler
    elif 'code' in process or 'pycharm' in process:
        return ide_handler
    elif 'excel' in process or 'word' in process:
        return office_handler
    
    return None
```

## Platform Compatibility

- **Windows**: Full functionality ✓
- **macOS**: Not supported (returns None/False)
- **Linux**: Not supported (returns None/False)

The module checks `sys.platform == 'win32'` before attempting any Win32 API calls.

## Logging

The module uses Python's logging module:

```python
import logging
logger = logging.getLogger(__name__)
```

Log levels:
- `DEBUG`: Successful operations, window info
- `WARNING`: Non-critical issues (e.g., can't get process name)
- `ERROR`: Critical failures (e.g., not on Windows, API call failed)

## Common Issues

### 1. Import Error: No module named 'win32gui'

**Solution**: Install pywin32
```bash
pip install pywin32
```

### 2. Import Error: No module named 'psutil'

**Solution**: Install psutil
```bash
pip install psutil
```

### 3. Access Denied when getting process name

**Cause**: Some system processes require elevated privileges

**Solution**: The code handles this gracefully and returns "unknown" for the process name

### 4. No active window detected

**Cause**: No window has focus (e.g., on lock screen)

**Solution**: The function returns None, which should be handled by the caller

## Performance

- `get_active_window()`: ~1-5ms (very fast)
- `list_all_windows()`: ~10-50ms (depends on number of windows)
- Other functions: <1ms

All functions are lightweight and suitable for frequent polling.

## Future Enhancements

Potential additions:
- Get window position and dimensions
- Detect window state (minimized, maximized, etc.)
- Monitor window events (focus change, close, etc.)
- Get window class name
- Enumerate child windows

## Developer Notes

- **Dev 2 (Ashish)**: Executor & Safety
- **Module**: `axon/executor/win_api.py`
- **Test**: `axon/test_win_api.py`
- **Dependencies**: pywin32, psutil

## Summary

This module provides the foundation for app-specific optimizations in AXON by enabling detection of the currently active application. The core function `get_active_window()` is used by `app_handlers.py` to apply app-specific handlers and optimizations.

---

**Made with Bob** 🤖