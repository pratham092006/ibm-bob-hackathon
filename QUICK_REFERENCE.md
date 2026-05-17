# AXON Quick Reference Guide

This document provides a quick reference for understanding and working with AXON.

---

## What is AXON?

AXON is a **Live AI Desktop Agent** that uses vision-language models to control your Windows desktop. You give it a task in natural language (e.g., "open chrome and search fitgirl"), and it:

1. **Sees** your screen using screenshots
2. **Thinks** using an LLM (Gemini/Claude/etc.)
3. **Acts** by controlling mouse and keyboard
4. **Repeats** until the task is complete

---

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set up API key in .env
GEMINI_API_KEY=your_key_here
LLM_PROVIDER=gemini

# 3. Run AXON
python main.py

# 4. Enter task in dialog
# Example: "open chrome and search fitgirl"

# 5. Watch the AI cursor work!
```

---

## How It Works (Simple Version)

```
You type task → Agent Loop starts → Forever:
    1. Take screenshot
    2. Ask LLM "what should I do next?"
    3. LLM responds with action (click, type, etc.)
    4. Execute action
    5. Wait for screen to update
    6. Repeat until done
```

---

## Key Files (What Each Does)

| File | What It Does | Key Functions |
|------|--------------|---------------|
| **main.py** | Starts everything, manages UI | `initialize()`, `on_task_submitted()` |
| **config.py** | Settings and shared state | Queues, events, API keys |
| **core/loop.py** | Main agent loop | `run_agent_loop()`, `activate_agent()` |
| **core/llm.py** | Talks to AI models | `call_llm()`, `get_screen_elements()` |
| **core/capture.py** | Takes screenshots | `capture_screen()` |
| **executor/actions.py** | Controls mouse/keyboard | `execute_action()`, `click()`, `type_text()` |
| **ui/input_dialog.py** | Task input window | `TaskInputDialog` |
| **ui/overlay.py** | Animated cursor | `TransparentOverlay` |

---

## The Agent Loop (Detailed)

```python
# Simplified version of run_agent_loop()

while not stopped:
    # 1. CAPTURE
    screenshot = capture_screen()  # Take screenshot
    
    # 2. OCR (optional, cached)
    text_anchors = get_screen_elements(screenshot)
    # Returns: [{"text": "Chrome", "coordinate": [100, 1050]}, ...]
    
    # 3. LLM
    action = call_llm(screenshot, task, history)
    # Returns: {"action": "left_click", "coordinate": [100, 1050], ...}
    
    # 4. BROADCAST (move cursor on screen)
    ui_queue.put({"type": "action", "action": action})
    
    # 5. EXECUTE
    if action["action"] == "left_click":
        pyautogui.click(action["coordinate"][0], action["coordinate"][1])
    elif action["action"] == "type":
        pyautogui.write(action["text"])
    # ... etc
    
    # 6. WAIT
    time.sleep(1.5)  # Let screen update
    
    # 7. CHECK
    if action["action"] == "done":
        break  # Task complete!
```

---

## Available Actions

The LLM can choose from these actions:

### 1. open_app (Fastest way to open apps)
```json
{
  "action": "open_app",
  "text": "chrome",
  "reasoning": "Opening Chrome browser",
  "confidence": 0.95
}
```
**What it does**: Win key → type "chrome" → Enter (all in one atomic operation)

### 2. left_click
```json
{
  "action": "left_click",
  "coordinate": [960, 540],
  "reasoning": "Clicking search box",
  "confidence": 0.9
}
```

### 3. type
```json
{
  "action": "type",
  "text": "fitgirl",
  "reasoning": "Typing search query",
  "confidence": 0.95
}
```

### 4. key
```json
{
  "action": "key",
  "text": "enter",
  "reasoning": "Submitting search",
  "confidence": 0.95
}
```
**Supports**: Single keys ("enter", "tab") and combinations ("ctrl+c", "alt+tab")

### 5. scroll
```json
{
  "action": "scroll",
  "coordinate": [960, 540],
  "direction": "down",
  "amount": 3,
  "reasoning": "Scrolling to see more results",
  "confidence": 0.8
}
```

### 6. done
```json
{
  "action": "done",
  "reasoning": "Task completed successfully",
  "confidence": 1.0
}
```

---

## Text Anchors (OCR Grounding)

**Problem**: LLM can't reliably guess where UI elements are just from looking at a screenshot.

**Solution**: Use EasyOCR to detect text on screen and provide exact coordinates.

**Example**:
```python
# OCR detects:
text_anchors = [
    {"text": "Chrome", "center_coordinate": [100, 1050]},
    {"text": "Start", "center_coordinate": [30, 1050]},
    {"text": "Search", "center_coordinate": [960, 500]}
]

# LLM sees these in its prompt:
"""
Detected Text Elements:
- "Chrome" at [100, 1050]
- "Start" at [30, 1050]
- "Search" at [960, 500]
"""

# LLM can now click accurately:
{"action": "left_click", "coordinate": [100, 1050]}  # Clicks Chrome!
```

**Why it's cached**: OCR is slow (200-500ms), so we cache results for 2 seconds.

---

## Communication Between Threads

AXON uses **queues** for thread-safe communication:

```
Main Thread (Qt UI)          Background Thread (Agent Loop)
       │                              │
       │◄─────── task_queue ──────────┤  User submits task
       │                              │
       │                              │  Agent runs loop
       │                              │
       │◄─────── ui_queue ────────────┤  Status updates
       │         (cursor position)    │
       │                              │
       │◄─────── status_queue ────────┤  Status text
       │         (for tray icon)      │
       │                              │
       ├────────── kill_event ────────>│  Emergency stop
```

**Why two queues (ui_queue and status_queue)?**
- Prevents race condition where one consumer steals messages meant for the other
- Each consumer gets its own dedicated queue

---

## Safety Features

### 1. Stuck Loop Detection
Stops agent if it repeats the same action 3 times:
```python
# Example: Clicking same spot 3 times
[
    {"action": "left_click", "coordinate": [100, 100]},
    {"action": "left_click", "coordinate": [100, 100]},
    {"action": "left_click", "coordinate": [100, 100]}
]
# → Detected! Sets kill_event, stops agent
```

### 2. Emergency Stop (F12)
Press F12 anytime to immediately stop the agent.

### 3. Coordinate Validation
Ensures clicks are within screen bounds before executing.

### 4. Action Logging
All actions logged to `session_log.json` for debugging.

---

## Configuration (config.py)

### LLM Settings
```python
LLM_PROVIDER = "gemini"  # or "claude", "openrouter", "nvidia"
GEMINI_API_KEY = "your_key_here"

GEMINI_MODELS = {
    "flash": "gemini-2.5-flash",  # Faster, cheaper
    "pro": "gemini-2.5-pro"        # Smarter, slower
}
CURRENT_MODEL = "flash"  # Default model
```

### Performance Settings
```python
FRAME_WIDTH = 1600       # Screenshot width (downscaled from native)
FRAME_HEIGHT = 900       # Screenshot height
JPEG_QUALITY = 85        # Compression quality (1-100)

USE_GPU = True           # EasyOCR GPU acceleration
DEBUG_MODE = True        # Save annotated screenshots
FAST_MODE = True         # Skip OCR for simple tasks
OCR_CACHE_DURATION = 2.0 # Cache OCR results (seconds)
```

### Timing
```python
MAX_LOOP_DELAY = 0.5     # Delay between iterations
API_TIMEOUT = 30         # LLM API timeout (seconds)

# Action-specific delays (in loop.py):
# - Clicks: 1.5s (UI animations)
# - Enter key: 2.0s (app launch)
# - Other: 0.8s (default)
```

---

## Debug Features

### 1. Debug Screenshots
When `DEBUG_MODE = True`, saves annotated screenshots to `bob-reports/debug_screenshots/`:
- Shows red circle at click target
- Displays action info (type, confidence, reasoning)
- Filename: `action_001_left_click_1234567890.jpg`

### 2. Action Logging
All actions logged to `session_log.json`:
```json
{
  "timestamp": "2024-01-15T10:30:45.123",
  "action": "left_click",
  "details": {
    "action": "left_click",
    "coordinate": [100, 1050],
    "reasoning": "Clicking Chrome icon",
    "confidence": 0.95
  },
  "success": true,
  "execution_time_ms": 15.3
}
```

### 3. Console Output
Detailed logging of each step:
```
[AGENT LOOP] === Iteration 1 ===
[AGENT LOOP] Status: Thinking...
[AGENT LOOP] Capturing screen...
[AGENT LOOP] Calling Gemini API...
[AGENT LOOP] API response received in 2.34s
[AGENT LOOP] Action: left_click
[AGENT LOOP] Reasoning: Clicking Chrome icon
[AGENT LOOP] Confidence: 0.95
[AGENT LOOP] Executing action: left_click
[AGENT LOOP] Action executed successfully
[AGENT LOOP] Sleeping for 1.5s...
```

---

## Example Task Execution

**Task**: "open chrome and search fitgirl"

### Iteration 1: Open Chrome
```
Screenshot → OCR → LLM decides:
{
  "action": "open_app",
  "text": "chrome",
  "reasoning": "Opening Chrome browser to perform search",
  "confidence": 0.95
}
→ Execute: Win + type "chrome" + Enter
→ Wait 2.0s for Chrome to launch
```

### Iteration 2: Click Search Box
```
Screenshot (Chrome open) → OCR finds "Search" at [960, 500] → LLM decides:
{
  "action": "left_click",
  "coordinate": [960, 500],
  "reasoning": "Clicking search box to enter query",
  "confidence": 0.9
}
→ Execute: pyautogui.click(960, 500)
→ Wait 1.5s for UI animation
```

### Iteration 3: Type Query
```
Screenshot (search box focused) → LLM decides:
{
  "action": "type",
  "text": "fitgirl",
  "reasoning": "Typing search query",
  "confidence": 0.95
}
→ Execute: pyautogui.write("fitgirl")
→ Wait 0.8s
```

### Iteration 4: Submit Search
```
Screenshot (text entered) → LLM decides:
{
  "action": "key",
  "text": "enter",
  "reasoning": "Submitting search query",
  "confidence": 0.95
}
→ Execute: pyautogui.press("enter")
→ Wait 2.0s for results to load
```

### Iteration 5: Done
```
Screenshot (results displayed) → LLM decides:
{
  "action": "done",
  "reasoning": "Search completed successfully, results are visible",
  "confidence": 1.0
}
→ Exit loop
→ Show "✅ Done!" in overlay
```

**Total time**: ~8-10 seconds (depending on LLM response time)

---

## Common Issues & Solutions

### Issue: Agent clicks wrong location
**Cause**: Coordinate scaling mismatch
**Solution**: Check that OCR coordinates are scaled to native resolution in `get_screen_elements()`

### Issue: Agent gets stuck in loop
**Cause**: LLM repeating failed action
**Solution**: Stuck-loop detection automatically stops after 3 identical actions

### Issue: OCR is slow
**Cause**: Running on CPU without GPU acceleration
**Solution**: Set `USE_GPU = True` and install CUDA, or increase `OCR_CACHE_DURATION`

### Issue: LLM response is slow
**Cause**: Using slower model (Pro) or large images
**Solution**: Switch to Flash model or reduce `FRAME_WIDTH`/`FRAME_HEIGHT`

### Issue: Actions execute too fast
**Cause**: Screen hasn't updated yet
**Solution**: Increase delays in `run_agent_loop()` (lines 278-285)

---

## Performance Tips

1. **Use Flash model** for faster responses (2-3s vs 5-8s for Pro)
2. **Enable GPU** for EasyOCR (`USE_GPU = True`)
3. **Increase OCR cache** duration for rapid actions
4. **Reduce frame size** if LLM is slow (but keep above 1280x720)
5. **Use open_app** action instead of manual clicking for apps

---

## Architecture Summary

```
┌─────────────────────────────────────────────────────────┐
│                    AXON ARCHITECTURE                     │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐       │
│  │    UI      │  │   Core     │  │  Executor  │       │
│  │  (Pratham) │  │  (Joshua)  │  │  (Ashish)  │       │
│  ├────────────┤  ├────────────┤  ├────────────┤       │
│  │ • Dialog   │  │ • Loop     │  │ • Actions  │       │
│  │ • Overlay  │  │ • LLM      │  │ • Safety   │       │
│  │ • Tray     │  │ • Capture  │  │ • Logging  │       │
│  └────────────┘  └────────────┘  └────────────┘       │
│         │               │               │              │
│         └───────────────┼───────────────┘              │
│                         │                              │
│                    ┌────┴────┐                         │
│                    │ config  │                         │
│                    │ Queues  │                         │
│                    │ Events  │                         │
│                    └─────────┘                         │
└─────────────────────────────────────────────────────────┘
```

---

## Further Reading

- **ARCHITECTURE.md**: Detailed component documentation
- **FLOW_DIAGRAMS.md**: Visual flow diagrams
- **LLM_SETUP_GUIDE.md**: How to configure different LLM providers
- **HOW_TO_RUN.md**: Installation and setup instructions

---

*This quick reference provides the essential information for understanding and working with AXON.*