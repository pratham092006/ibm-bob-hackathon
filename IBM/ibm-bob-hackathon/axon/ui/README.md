# AXON UI Components

**Developer:** Dev 3 (Pratham)  
**Module:** UI & Demo

This directory contains all UI components for the AXON desktop agent.

## Components Overview

### 1. **reticle.py** (PRIORITY #1 - "Money Shot")
The animated glowing reticle that shows where the cursor will move BEFORE it moves.

**Features:**
- Glowing animated circle at predicted cursor position
- Pulsing/breathing animation effect for visual appeal
- State-based colors:
  - `IDLE` (blue): Agent is idle
  - `THINKING` (orange): Agent is processing
  - `MOVING` (green): Cursor is moving
  - `CLICKING` (red): Performing click action
- Smooth position interpolation
- Crosshair overlay for precision
- Optimized for 60 FPS rendering

**Usage:**
```python
from ui.reticle import Reticle

reticle = Reticle()
reticle.set_position(x=500, y=300, animate=True)
reticle.set_state(Reticle.STATE_MOVING)
reticle.update(delta_time=0.016)  # Call every frame
reticle.draw(painter, current_time)
```

### 2. **overlay.py**
Transparent fullscreen window that displays the reticle and status HUD.

**Features:**
- Fullscreen transparent window
- Always on top, click-through
- Displays reticle at predicted positions
- Status HUD showing:
  - Current task
  - Current step
  - Response time
  - Action count
- Multi-monitor support
- Minimal CPU usage (~1-2%)

**Usage:**
```python
from ui.overlay import create_overlay

overlay = create_overlay()
overlay.set_reticle_position(x=500, y=300)
overlay.set_reticle_state("moving")
overlay.set_task_info(
    task="Open Notepad",
    step="Clicking Start menu",
    response_time=1.2,
    action_count=3
)
```

### 3. **input_dialog.py**
Floating task input window with voice support.

**Features:**
- Modern floating dialog design
- Text input field for typing tasks
- Voice input toggle button
- Integration with faster-whisper for transcription
- Real-time transcription display
- Recording indicator
- Draggable window
- Submit/Cancel buttons

**Usage:**
```python
from ui.input_dialog import show_task_input_dialog

task = show_task_input_dialog()
if task:
    print(f"User task: {task}")
```

### 4. **tray.py**
System tray icon with status menu.

**Features:**
- System tray integration using pystray
- State-based icon colors (idle/running/error/stopped)
- Context menu:
  - Start/Stop Agent
  - Toggle Overlay
  - New Task
  - Status
  - Exit
- System notifications for events
- Monitors status_queue for updates

**Usage:**
```python
from ui.tray import create_tray_icon
from ui.input_dialog import show_task_input_dialog

tray = create_tray_icon(
    overlay=overlay,
    input_dialog_callback=show_task_input_dialog
)
```

## Integration Contract

All UI components integrate with the main agent through:

### Status Queue (from config.py)
```python
from config import status_queue

# Dev 1 puts status updates
status_queue.put({
    'type': 'task_start',
    'task': 'Open Notepad'
})

status_queue.put({
    'type': 'action',
    'action': 'click',
    'x': 500,
    'y': 300
})

status_queue.put({
    'type': 'task_complete'
})
```

### Kill Event (from config.py)
```python
from config import kill_event

# Dev 2 checks this to halt execution
if kill_event.is_set():
    # Stop current action
    break
```

## Testing

Run the test script to verify all components:

```bash
cd axon
python test_ui.py
```

This will test:
- Reticle animation and state changes
- Overlay display and updates
- Input dialog functionality
- Tray icon creation and menu

## Dependencies

Required packages (in requirements.txt):
- PyQt6 >= 6.4.0
- pystray >= 0.19.0
- Pillow >= 9.0.0
- faster-whisper >= 0.9.0 (optional, for voice input)
- pyaudio >= 0.2.13 (optional, for voice input)

## Architecture

```
ui/
├── __init__.py          # Module exports
├── reticle.py           # Animated cursor prediction indicator
├── overlay.py           # Transparent fullscreen window
├── input_dialog.py      # Task input with voice support
├── tray.py              # System tray integration
└── README.md            # This file
```

## Performance Notes

- **Reticle**: Renders at 60 FPS with minimal CPU usage
- **Overlay**: Uses Qt's efficient painting system
- **Input Dialog**: Lightweight, only active when shown
- **Tray Icon**: Runs in background thread, negligible overhead

## Demo Scenarios

The UI components are designed to shine in these demo scenarios:

### Scenario 1: Browser + Writing
> "Search Google for the top 3 AI coding tools and paste a summary into Notepad."

**UI Highlights:**
- Reticle shows predicted clicks on Chrome icon, search bar, Notepad
- Status HUD displays current step
- Smooth animations between actions

### Scenario 2: File Management
> "Rename all the screenshots in this folder to include today's date."

**UI Highlights:**
- Reticle precisely indicates file selections
- State changes (thinking → moving → clicking)
- Action count increments in HUD

### Scenario 3: Video Editor (Hero Moment)
> "Trim the first 30 seconds off this video and export it."

**UI Highlights:**
- Complex multi-step visualization
- Reticle shows timeline navigation
- Real-time status updates

## Troubleshooting

### PyQt6 not found
```bash
pip install PyQt6
```

### Overlay not click-through
Ensure `Qt.WindowTransparentForInput` flag is set in overlay.py

### Tray icon not showing
Check if pystray is installed and system tray is enabled

### Voice input not working
Install optional dependencies:
```bash
pip install faster-whisper pyaudio
```

## Future Enhancements

- [ ] Add settings dialog for customization
- [ ] Support multiple reticles for multi-action preview
- [ ] Add replay/history viewer
- [ ] Implement dark/light theme toggle
- [ ] Add keyboard shortcuts overlay

---

**Made with Bob** 🤖

For questions or issues, contact Dev 3 (Pratham) or check the main AXON_PRD.md