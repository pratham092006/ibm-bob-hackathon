# AXON Action Execution Module

## Overview

The `actions.py` module is the core executor component that receives action dictionaries from the Computer Use API and executes them using PyAutoGUI. This module provides safe, validated, and logged execution of all mouse, keyboard, and system control actions.

## Architecture

```
Computer Use API → execute_action() → Specific Action Functions → PyAutoGUI
                         ↓
                   Validation & Logging
                         ↓
                   Success/Failure Status
```

## Functions

### 1. `validate_coordinates(x, y)`

Validates that coordinates are within screen bounds before executing mouse actions.

**Parameters:**
- `x` (int): X coordinate to validate
- `y` (int): Y coordinate to validate

**Returns:**
- `bool`: True if coordinates are valid, False otherwise

**Example:**
```python
if validate_coordinates(100, 200):
    # Coordinates are safe to use
    pass
```

### 2. `mouse_move(x, y, duration=0.1)`

Moves the mouse cursor to specified coordinates with smooth animation.

**Parameters:**
- `x` (int): Target x coordinate
- `y` (int): Target y coordinate
- `duration` (float): Animation duration in seconds (default: 0.1)

**Returns:**
- `bool`: True if successful, False otherwise

**Features:**
- Validates coordinates before moving
- Smooth animation using duration parameter
- Comprehensive error handling and logging

**Example:**
```python
mouse_move(500, 300, duration=0.2)  # Smooth move to (500, 300)
```

### 3. `click(x, y, button='left', clicks=1)`

Performs click actions at specified coordinates.

**Parameters:**
- `x` (int): Click x coordinate
- `y` (int): Click y coordinate
- `button` (str): Button type - 'left', 'right', or 'middle' (default: 'left')
- `clicks` (int): Number of clicks - 1 for single, 2 for double (default: 1)

**Returns:**
- `bool`: True if successful, False otherwise

**Features:**
- Supports left, right, and middle mouse buttons
- Supports single and double clicks
- Validates coordinates and button type
- Comprehensive logging

**Examples:**
```python
click(100, 200)                      # Left click
click(100, 200, button='right')      # Right click
click(100, 200, clicks=2)            # Double click
click(100, 200, button='middle')     # Middle click
```

### 4. `type_text(text, interval=0.03)`

Types text with realistic timing between keystrokes.

**Parameters:**
- `text` (str): Text to type
- `interval` (float): Delay between keystrokes in seconds (default: 0.03)

**Returns:**
- `bool`: True if successful, False otherwise

**Features:**
- Uses `pyautogui.write()` for better special character handling
- Realistic typing speed with configurable interval
- Handles special characters and unicode
- Error handling and logging

**Example:**
```python
type_text("Hello, World!")           # Type with default interval
type_text("Fast typing", interval=0.01)  # Faster typing
```

### 5. `scroll(x, y, direction='down', amount=3)`

Scrolls at specified coordinates in the given direction.

**Parameters:**
- `x` (int): X coordinate to scroll at
- `y` (int): Y coordinate to scroll at
- `direction` (str): Scroll direction - 'up' or 'down' (default: 'down')
- `amount` (int): Scroll amount in clicks (default: 3)

**Returns:**
- `bool`: True if successful, False otherwise

**Features:**
- Moves cursor to coordinates before scrolling
- Converts direction to appropriate scroll value
- Validates coordinates
- Error handling and logging

**Examples:**
```python
scroll(500, 500, direction='down', amount=5)  # Scroll down
scroll(500, 500, direction='up', amount=3)    # Scroll up
```

### 6. `press_key(key_combination)`

Presses a single key or key combination.

**Parameters:**
- `key_combination` (str): Key name or combination (e.g., 'enter', 'ctrl+c', 'alt+tab')

**Returns:**
- `bool`: True if successful, False otherwise

**Features:**
- Supports single key presses
- Supports key combinations with '+' separator
- Automatically parses and executes combinations
- Case-insensitive key names
- Error handling and logging

**Examples:**
```python
press_key('enter')           # Single key
press_key('ctrl+c')          # Copy
press_key('ctrl+shift+s')    # Save As
press_key('alt+tab')         # Switch window
```

### 7. `execute_action(action_dict)` ⭐ MAIN DISPATCHER

The primary function that Dev 1's loop calls. Routes action dictionaries from the Computer Use API to appropriate handler functions.

**Parameters:**
- `action_dict` (dict): Action specification from Computer Use API

**Returns:**
- `bool`: True if action executed successfully, False otherwise

**Supported Action Types:**

| Action Type | Required Fields | Example |
|------------|----------------|---------|
| `mouse_move` | `coordinate` [x, y] | `{"action": "mouse_move", "coordinate": [200, 150]}` |
| `left_click` | `coordinate` [x, y] | `{"action": "left_click", "coordinate": [420, 310]}` |
| `right_click` | `coordinate` [x, y] | `{"action": "right_click", "coordinate": [420, 310]}` |
| `middle_click` | `coordinate` [x, y] | `{"action": "middle_click", "coordinate": [420, 310]}` |
| `double_click` | `coordinate` [x, y] | `{"action": "double_click", "coordinate": [420, 310]}` |
| `type` | `text` | `{"action": "type", "text": "Hello World"}` |
| `key` | `text` | `{"action": "key", "text": "ctrl+s"}` |
| `scroll` | `coordinate` [x, y], `direction`, `amount` | `{"action": "scroll", "coordinate": [340, 400], "direction": "down", "amount": 3}` |
| `done` | None | `{"action": "done"}` |

**Features:**
- Comprehensive action routing
- Validates action structure
- Handles the "done" action by setting kill_event
- Detailed error logging
- Returns success/failure status for each action

**Example Usage:**
```python
from executor.actions import execute_action

# Execute various actions
execute_action({"action": "mouse_move", "coordinate": [500, 300]})
execute_action({"action": "left_click", "coordinate": [500, 300]})
execute_action({"action": "type", "text": "Hello AXON"})
execute_action({"action": "key", "text": "ctrl+s"})
execute_action({"action": "scroll", "coordinate": [500, 500], "direction": "down", "amount": 5})
execute_action({"action": "done"})  # Sets kill_event to stop the loop
```

## Safety Features

### PyAutoGUI Safety Settings

```python
pyautogui.FAILSAFE = True   # Move mouse to corner to abort
pyautogui.PAUSE = 0.1       # Small delay between actions
```

### Coordinate Validation

All mouse actions validate coordinates before execution to prevent out-of-bounds errors.

### Error Handling

Every function includes comprehensive try-except blocks to catch and log errors without crashing the system.

### Logging

All actions are logged with timestamps and status information for debugging and monitoring.

## Integration with AXON System

### Kill Event Integration

The `execute_action()` function imports `kill_event` from `config.py` and sets it when receiving a "done" action, allowing Dev 1's loop to gracefully terminate.

```python
from axon.config import kill_event

# In execute_action()
elif action_type == "done":
    logger.info("Task complete - setting kill_event")
    kill_event.set()
    return True
```

### Status Queue Integration

While not directly implemented in this module, actions can be logged to the status queue for UI updates:

```python
from axon.config import status_queue

# After executing action
status_queue.put({"action": action_type, "status": "success"})
```

## Testing

Run the test suite to verify all functions:

```bash
cd axon
python test_actions.py
```

**Warning:** Tests will move your mouse and type text. Ensure you're in a safe environment.

## Error Handling

All functions return `bool` status:
- `True`: Action executed successfully
- `False`: Action failed (logged with details)

Check logs for detailed error information:

```python
import logging
logging.basicConfig(level=logging.INFO)
```

## Performance Considerations

- **Mouse Movement**: Default duration of 0.1s provides smooth movement without being too slow
- **Text Typing**: Default interval of 0.03s mimics realistic typing speed
- **Scrolling**: Moves cursor to position before scrolling for reliability
- **Key Presses**: Minimal delay for responsive keyboard actions

## Dependencies

- `pyautogui`: Core automation library
- `logging`: Built-in Python logging
- `time`: Built-in Python time utilities
- `axon.config`: Shared configuration (kill_event)

## Future Enhancements

Potential improvements for future versions:

1. **Screenshot Verification**: Capture screenshots before/after actions
2. **Action Recording**: Record all actions for replay/debugging
3. **Retry Logic**: Automatic retry on failure with exponential backoff
4. **Action Queuing**: Queue multiple actions for batch execution
5. **Performance Metrics**: Track action execution times
6. **Advanced Validation**: OCR-based verification of action results

## Troubleshooting

### Mouse Not Moving
- Check if coordinates are valid using `validate_coordinates()`
- Verify screen resolution matches expected values
- Check PyAutoGUI FAILSAFE isn't triggered (mouse in corner)

### Text Not Typing
- Ensure a text input field has focus
- Check for special characters that might need escaping
- Verify keyboard layout matches expected input

### Clicks Not Working
- Validate coordinates are within screen bounds
- Check if target element is visible and clickable
- Verify button parameter is correct ('left', 'right', 'middle')

### Scroll Not Working
- Ensure coordinates are over a scrollable area
- Check scroll direction and amount parameters
- Verify the application window has focus

## Made with Bob

This module was implemented as part of the AXON project by Dev 2 (Ashish) - Executor & Safety.