# AXON Architecture Documentation

## Table of Contents
1. [Overview](#overview)
2. [Project Structure](#project-structure)
3. [Complete Workflow](#complete-workflow)
4. [Component Details](#component-details)
5. [Data Flow](#data-flow)
6. [Sequence Diagrams](#sequence-diagrams)
7. [Example: "Open Chrome and Search FitGirl"](#example-open-chrome-and-search-fitgirl)

---

## Overview

**AXON** is a Live AI Desktop Agent that uses vision-language models (VLMs) to control a Windows desktop by analyzing screenshots and executing actions. It operates in a continuous loop, observing the screen, making decisions, and performing actions until the user's task is complete.

### Key Features
- **Vision-based control**: Uses LLM with screen captures to understand UI
- **OCR-enhanced grounding**: EasyOCR provides text anchor coordinates for reliable clicking
- **Multi-LLM support**: Gemini, Claude, OpenRouter, NVIDIA models
- **Real-time UI feedback**: Animated cursor overlay shows AI's actions
- **Safety features**: Stuck-loop detection, emergency kill switch (F12)
- **Action logging**: All actions logged to `session_log.json`

### Architecture Philosophy
- **Modular design**: Separate concerns (vision, brain, execution, UI)
- **Thread-safe communication**: Queues for inter-module messaging
- **Fail-safe mechanisms**: Multiple layers of error handling and recovery

---

## Project Structure

```
axon/
├── main.py                      # Entry point, application orchestration
├── config.py                    # Shared configuration and state
├── requirements.txt             # Python dependencies
│
├── core/                        # Vision & Brain (Dev 1 - Joshua)
│   ├── __init__.py
│   ├── loop.py                  # Main agent control loop
│   ├── llm.py                   # LLM integration (Gemini/Claude/etc.)
│   ├── capture.py               # Screen capture using mss
│   └── planner.py               # Task planning (future)
│
├── executor/                    # Action Execution & Safety (Dev 2 - Ashish)
│   ├── __init__.py
│   ├── actions.py               # Action execution (mouse, keyboard)
│   ├── kill_switch.py           # Emergency stop (F12 key)
│   ├── win_api.py               # Windows API integration
│   └── app_handlers.py          # Application-specific handlers
│
├── ui/                          # User Interface (Dev 3 - Pratham)
│   ├── __init__.py
│   ├── input_dialog.py          # Task input dialog with voice
│   ├── overlay.py               # Transparent cursor overlay
│   ├── reticle.py               # Animated cursor reticle
│   └── tray.py                  # System tray icon
│
└── bob-reports/                 # Debug outputs
    └── debug_screenshots/       # Annotated action screenshots
```

### File Responsibilities

| File | Lines | Purpose |
|------|-------|---------|
| `main.py` | 253 | Application initialization, UI coordination |
| `config.py` | 80 | Shared state (queues, events), configuration |
| `core/loop.py` | 373 | Main agent loop, task execution orchestration |
| `core/llm.py` | 1096 | LLM API calls, OCR text extraction, prompt engineering |
| `core/capture.py` | 63 | Screen capture and compression |
| `executor/actions.py` | 606 | Action execution, stuck-loop detection |
| `ui/input_dialog.py` | 505 | Task input UI with model selection |
| `ui/overlay.py` | 335 | Floating cursor overlay widget |

---

## Complete Workflow

### High-Level Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INTERACTION                         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  1. User enters task in TaskInputDialog                         │
│     Example: "open chrome and search fitgirl"                   │
│     - Can select model (Flash/Pro)                              │
│     - Can use voice input (optional)                            │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  2. Task submitted via PyQt6 signal                             │
│     main.py: on_task_submitted(task)                            │
│     - Shows overlay cursor                                       │
│     - Calls activate_agent(task)                                │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  3. Task queued for background thread                           │
│     loop.py: activate_agent(task)                               │
│     - Clears kill_event                                         │
│     - Puts task in task_queue                                   │
│     - Broadcasts task_start status                              │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  4. Monitoring thread picks up task                             │
│     loop.py: start_monitoring() → run_agent_loop(task)          │
│     - Runs in background daemon thread                          │
│     - Starts main agent loop                                    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────────┐
        │     MAIN AGENT LOOP (Iterative)         │
        │     Continues until done or error       │
        └─────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  5. CAPTURE: Take screenshot                                    │
│     capture.py: capture_screen()                                │
│     - Uses mss library for fast capture                         │
│     - Captures primary monitor                                  │
│     - Resizes to 1600x900 (FRAME_WIDTH x FRAME_HEIGHT)         │
│     - Compresses to JPEG (quality 85)                           │
│     - Returns bytes for LLM                                     │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  6. OCR: Extract text anchors (optional, cached)                │
│     llm.py: get_screen_elements(image)                          │
│     - Uses EasyOCR to detect text on screen                     │
│     - Extracts bounding boxes and center coordinates            │
│     - Scales coordinates from 1600x900 to native resolution     │
│     - Caches results for 2 seconds (OCR_CACHE_DURATION)        │
│     - Returns: [{"text": "Chrome", "center_coordinate": [x,y]}] │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  7. LLM: Analyze and decide action                              │
│     llm.py: call_llm(screen_image, task, history)               │
│     - Builds system instruction with text anchors               │
│     - Sends screenshot + task + history to LLM                  │
│     - LLM analyzes screen and decides next action               │
│     - Returns JSON: {"action": "left_click",                    │
│                      "coordinate": [x, y],                      │
│                      "reasoning": "...",                        │
│                      "confidence": 0.95}                        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  8. BROADCAST: Update UI with action                            │
│     loop.py: _broadcast_status(action_dict)                     │
│     - Sends to both status_queue and ui_queue                   │
│     - Overlay moves cursor to target coordinates                │
│     - Status text updated                                       │
│     - Small delay (0.1s) for UI to update                       │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  9. EXECUTE: Perform action                                     │
│     actions.py: execute_action(action_dict)                     │
│     - Validates action and coordinates                          │
│     - Checks for stuck loops (3 identical actions)              │
│     - Routes to specific handler:                               │
│       • open_app: Windows Search (Win + type + Enter)           │
│       • left_click: pyautogui.click(x, y)                       │
│       • type: pyautogui.write(text)                             │
│       • key: pyautogui.press(key) or hotkey()                   │
│       • scroll: pyautogui.scroll(amount)                        │
│     - Logs action to session_log.json                           │
│     - Returns success/failure                                   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  10. WAIT: Allow screen to update                               │
│      loop.py: time.sleep(delay)                                 │
│      - Click actions: 1.5s (UI animations)                      │
│      - Enter key: 2.0s (app launch time)                        │
│      - Other actions: 0.8s                                      │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  11. CHECK: Task complete or continue?                          │
│      - If action == "done": Exit loop, show success             │
│      - If action == "error": Exit loop, show error              │
│      - If kill_event set: Exit loop, show stopped               │
│      - Otherwise: Add to history, go to step 5                  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  12. COMPLETE: Show result to user                              │
│      - Overlay shows "✅ Done!" or "❌ Error"                    │
│      - Auto-hides after 3-5 seconds                             │
│      - User can submit new task                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Component Details

### 1. Entry Point: `main.py`

**Purpose**: Application initialization and UI coordination

**Key Classes**:
- `AxonApplication`: Main application orchestrator

**Initialization Flow** (lines 30-64):
```python
def initialize(self):
    # 1. Create Qt application
    self.app = QApplication(sys.argv)
    
    # 2. Create UI components
    self.overlay = TransparentOverlay()        # Cursor overlay
    self.input_dialog = TaskInputDialog()      # Task input
    self.tray = TrayIcon(...)                  # System tray
    
    # 3. Connect signals
    self.input_dialog.task_submitted.connect(self.on_task_submitted)
    
    # 4. Start background monitoring thread
    self.monitor_thread = threading.Thread(target=start_monitoring, daemon=True)
    self.monitor_thread.start()
    
    # 5. Set up UI update timer (50ms interval)
    self.status_timer = QTimer()
    self.status_timer.timeout.connect(self.update_status)
    self.status_timer.start(50)
```

**Task Submission Handler** (lines 66-92):
```python
def on_task_submitted(self, task):
    # 1. Show overlay cursor
    self.overlay.show()
    self.overlay.show_reticle()
    
    # 2. Set initial position (center of screen)
    screen_width, screen_height = pyautogui.size()
    self.overlay.set_reticle_position(screen_width // 2, screen_height // 2)
    
    # 3. Activate agent with task
    activate_agent(task)  # Queues task for background thread
```

---

### 2. Configuration: `config.py`

**Purpose**: Shared state and configuration across all modules

**Shared State** (lines 11-14):
```python
status_queue = queue.Queue()    # For tray icon status updates
ui_queue = queue.Queue()        # For overlay UI updates (dedicated)
task_queue = queue.Queue()      # For submitting tasks to agent
kill_event = threading.Event()  # Emergency stop signal
```

**Why Two Queues?**
- `status_queue`: Consumed by tray icon for status text
- `ui_queue`: Consumed by overlay for cursor position/state
- Prevents race condition where one consumer steals messages meant for the other

---

### 3. Agent Loop: `core/loop.py`

**Purpose**: Main control loop that orchestrates the agent's behavior

**Main Agent Loop** (lines 134-305):
```python
def run_agent_loop(task_description):
    """Main loop: capture → analyze → execute → repeat"""
    
    conversation_history = []
    action_count = 0
    kill_event.clear()
    
    while not kill_event.is_set():
        # 1. Broadcast thinking status
        _broadcast_status({"type": "thinking", "message": "Analyzing screen..."})
        
        # 2. Capture screen
        screen_image = capture_screen()  # Returns JPEG bytes
        
        # 3. Call LLM with screen + task + history
        action_dict = call_llm(screen_image, task_description, conversation_history)
        
        # 4. Save debug screenshot (if DEBUG_MODE)
        if DEBUG_MODE:
            _save_debug_screenshot(screen_image, action_dict, action_count + 1)
        
        # 5. Broadcast action (moves cursor BEFORE execution)
        _broadcast_status({"type": "action", "action": action_dict, ...})
        time.sleep(0.1)  # Allow UI to update
        
        # 6. Check if done/error
        if action_dict['action'] == 'done':
            break
        
        # 7. Execute action
        success = execute_action(action_dict)
        action_count += 1
        
        # 8. Add to history
        action_dict['outcome'] = 'success' if success else 'warning'
        conversation_history.append(action_dict)
        
        # 9. Wait for screen to update
        delay = 1.5 if action_type in ['click', ...] else 0.8
        time.sleep(delay)
```

---

### 4. LLM Integration: `core/llm.py`

**Purpose**: Vision-language model integration with OCR grounding

**OCR Text Extraction** (lines 110-205):
```python
def get_screen_elements(image_path, native_width, native_height):
    """Extract text anchors using EasyOCR with coordinate scaling"""
    
    # 1. Check cache (2-second duration)
    if current_time - _last_ocr_time < OCR_CACHE_DURATION:
        return _ocr_cache
    
    # 2. Run OCR on downscaled image
    results = reader.readtext(image_path)
    
    # 3. Extract text anchors with scaled coordinates
    for bbox, text, confidence in results:
        # Calculate center and scale to native resolution
        center_x = sum(x for x, y in bbox) / 4
        center_y = sum(y for x, y in bbox) / 4
        native_x = int(center_x * scale_x)
        native_y = int(center_y * scale_y)
        
        text_anchors.append({
            "text": text,
            "center_coordinate": [native_x, native_y]
        })
    
    return text_anchors
```

---

### 5. Action Execution: `executor/actions.py`

**Purpose**: Execute actions with safety checks

**Main Dispatcher** (lines 267-431):
```python
def execute_action(action_dict):
    """Execute action with stuck-loop detection and logging"""
    
    # 1. Add to history
    action_history.append(action_dict)
    
    # 2. Check for stuck loop (3 identical actions)
    if _is_stuck_loop(action_history):
        kill_event.set()  # Stop agent
        return False
    
    # 3. Route to handler
    if action_type == "open_app":
        success = _open_app_via_search(app_name)
    elif action_type == "left_click":
        success = click(x, y, button='left')
    # ... other action types
    
    # 4. Log action to session_log.json
    log_action_to_file(action_dict, success, execution_time)
    
    return success
```

---

## Data Flow

### Message Flow Diagram

```
┌──────────────┐
│   main.py    │  (Main Thread - Qt Event Loop)
└──────┬───────┘
       │
       │ task_submitted signal
       ▼
┌──────────────────────────────────────────────────────────┐
│  activate_agent(task)                                    │
│  - Clears kill_event                                     │
│  - Puts task in task_queue ──────────────────────┐      │
│  - Broadcasts to status_queue & ui_queue         │      │
└──────────────────────────────────────────────────┼──────┘
                                                    │
                                                    ▼
                                    ┌───────────────────────────┐
                                    │  Background Thread        │
                                    │  start_monitoring()       │
                                    │  - Waits on task_queue    │
                                    │  - Calls run_agent_loop() │
                                    └───────────┬───────────────┘
                                                │
                                                ▼
                        ┌───────────────────────────────────────┐
                        │  run_agent_loop(task)                 │
                        │  Main agent loop (iterative)          │
                        └───────────┬───────────────────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    │               │               │
                    ▼               ▼               ▼
            ┌──────────────┐ ┌──────────┐ ┌──────────────┐
            │ capture.py   │ │  llm.py  │ │  actions.py  │
            │ Screenshot   │ │ Analyze  │ │  Execute     │
            └──────┬───────┘ └────┬─────┘ └──────┬───────┘
                   │              │               │
                   │              │               │
                   └──────────────┼───────────────┘
                                  │
                                  │ _broadcast_status()
                                  │
                    ┌─────────────┴─────────────┐
                    │                           │
                    ▼                           ▼
            ┌───────────────┐         ┌─────────────────┐
            │ status_queue  │         │   ui_queue      │
            │ (tray icon)   │         │   (overlay)     │
            └───────┬───────┘         └────────┬────────┘
                    │                          │
                    ▼                          ▼
            ┌───────────────┐         ┌─────────────────┐
            │  tray.py      │         │  overlay.py     │
            │  Status text  │         │  Cursor pos     │
            └───────────────┘         └─────────────────┘
```

---

## Sequence Diagrams

### Task Submission and Execution

```
User      Dialog    main.py    loop.py    capture.py   llm.py    actions.py   Overlay
 │          │          │          │            │          │           │          │
 │ Enter    │          │          │            │          │           │          │
 │ task     │          │          │            │          │           │          │
 ├─────────>│          │          │            │          │           │          │
 │          │ submit   │          │            │          │           │          │
 │          ├─────────>│          │            │          │           │          │
 │          │          │ show     │            │          │           │          │
 │          │          │ overlay  │            │          │           │          │
 │          │          ├─────────────────────────────────────────────────────────>│
 │          │          │          │            │          │           │          │
 │          │          │ activate_agent(task)  │          │           │          │
 │          │          ├─────────>│            │          │           │          │
 │          │          │          │ run_agent_loop()      │           │          │
 │          │          │          │            │          │           │          │
 │          │          │          │ capture_screen()      │           │          │
 │          │          │          ├───────────>│          │           │          │
 │          │          │          │<───────────┤          │           │          │
 │          │          │          │            │          │           │          │
 │          │          │          │ call_llm(image, task) │           │          │
 │          │          │          ├────────────────────────>          │          │
 │          │          │          │<────────────────────────          │          │
 │          │          │          │ action_dict                       │          │
 │          │          │          │            │          │           │          │
 │          │          │          │ _broadcast_status()               │          │
 │          │          │          ├───────────────────────────────────────────────>│
 │          │          │          │            │          │           │          │
 │          │          │          │ execute_action(action_dict)       │          │
 │          │          │          ├───────────────────────────────────>│          │
 │          │          │          │<───────────────────────────────────┤          │
 │          │          │          │            │          │           │          │
 │          │          │          │ [Loop continues...]               │          │
```

---

## Example: "Open Chrome and Search FitGirl"

### Complete Execution Trace

**Iteration 1: Open Chrome**
```
1. Capture: Screenshot of desktop (1600x900 JPEG)
2. OCR: Detects "Chrome" at [100, 1050] (taskbar)
3. LLM Decision:
   {
     "action": "open_app",
     "text": "chrome",
     "reasoning": "Opening Chrome browser",
     "confidence": 0.95
   }
4. Execute: Win key → type "chrome" → Enter
5. Wait: 2.0 seconds for Chrome to launch
```

**Iteration 2: Click Search Box**
```
1. Capture: Chrome is now open with Google homepage
2. OCR: Detects "Search" at [960, 500]
3. LLM Decision:
   {
     "action": "left_click",
     "coordinate": [960, 500],
     "reasoning": "Clicking search box",
     "confidence": 0.9
   }
4. Execute: pyautogui.click(960, 500)
5. Wait: 1.5 seconds for UI animation
```

**Iteration 3: Type Search Query**
```
1. Capture: Search box is focused
2. OCR: (cached from previous)
3. LLM Decision:
   {
     "action": "type",
     "text": "fitgirl",
     "reasoning": "Typing search query",
     "confidence": 0.95
   }
4. Execute: pyautogui.write("fitgirl")
5. Wait: 0.8 seconds
```

**Iteration 4: Submit Search**
```
1. Capture: Text entered in search box
2. OCR: (cached)
3. LLM Decision:
   {
     "action": "key",
     "text": "enter",
     "reasoning": "Submitting search",
     "confidence": 0.95
   }
4. Execute: pyautogui.press("enter")
5. Wait: 2.0 seconds for results to load
```

**Iteration 5: Task Complete**
```
1. Capture: Search results displayed
2. OCR: Detects search results
3. LLM Decision:
   {
     "action": "done",
     "reasoning": "Search completed successfully",
     "confidence": 1.0
   }
4. Exit loop
5. Show "✅ Done!" in overlay
```

---

## Key Design Decisions

### 1. Why Two Queues (status_queue and ui_queue)?
**Problem**: Race condition where tray icon and overlay compete for messages
**Solution**: Broadcast to both queues simultaneously
**Benefit**: Each consumer gets all messages reliably

### 2. Why OCR Caching?
**Problem**: OCR is slow (200-500ms per frame)
**Solution**: Cache results for 2 seconds
**Benefit**: 4-5x faster iteration speed for rapid actions

### 3. Why Coordinate Scaling?
**Problem**: LLM sees 1600x900 image but screen is 1920x1080
**Solution**: Scale OCR coordinates immediately to native resolution
**Benefit**: Accurate clicking without coordinate mismatch

### 4. Why Stuck-Loop Detection?
**Problem**: LLM can get stuck repeating failed actions
**Solution**: Detect 3 identical actions or 5 actions in same region
**Benefit**: Automatic recovery from infinite loops

### 5. Why Atomic open_app Action?
**Problem**: Opening apps with separate key/type/enter is slow and error-prone
**Solution**: Single atomic action that handles entire sequence
**Benefit**: Faster, more reliable app launching

---

## Performance Optimizations

1. **Frame Compression**: 1600x900 @ 85% JPEG quality
2. **OCR Caching**: 2-second cache duration
3. **Fast Mode**: Skip OCR for simple tasks
4. **GPU Acceleration**: EasyOCR uses CUDA if available
5. **Async UI Updates**: 50ms timer for smooth overlay
6. **Smart Delays**: Variable wait times based on action type

---

## Error Handling

1. **Stuck Loop Detection**: Stops after 3 identical actions
2. **Timeout Detection**: Stops after 15 seconds without progress
3. **Coordinate Validation**: Checks if coordinates are within screen bounds
4. **LLM Error Recovery**: Returns error action if API call fails
5. **Emergency Stop**: F12 key sets kill_event immediately

---

## Debugging Features

1. **Debug Screenshots**: Annotated images showing click targets
2. **Action Logging**: All actions logged to session_log.json
3. **Console Output**: Detailed logging of each step
4. **Status Updates**: Real-time status in overlay and tray

---

*This documentation was created to help developers understand the complete AXON system architecture and workflow.*