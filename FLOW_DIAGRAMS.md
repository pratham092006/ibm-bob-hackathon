# AXON Flow Diagrams

This document contains detailed ASCII flow diagrams for understanding AXON's execution flow.

---

## 1. Complete System Flow (User Prompt to Action)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              USER LAYER                                  │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │  TaskInputDialog (ui/input_dialog.py)                            │  │
│  │  - User types: "open chrome and search fitgirl"                  │  │
│  │  - Selects model: Gemini Flash / Pro                             │  │
│  │  - Optional: Voice input via faster-whisper                      │  │
│  │  - Clicks "Start" button                                         │  │
│  └────────────────────────────┬─────────────────────────────────────┘  │
└────────────────────────────────┼────────────────────────────────────────┘
                                 │ PyQt6 Signal: task_submitted
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         MAIN THREAD (main.py)                            │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │  AxonApplication.on_task_submitted(task)                         │  │
│  │  1. Show overlay cursor at screen center                         │  │
│  │  2. Set status: "Starting task..."                               │  │
│  │  3. Call activate_agent(task)                                    │  │
│  └────────────────────────────┬─────────────────────────────────────┘  │
└────────────────────────────────┼────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    TASK ACTIVATION (core/loop.py)                        │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │  activate_agent(task)                                            │  │
│  │  1. kill_event.clear()  # Reset stop signal                      │  │
│  │  2. task_queue.put(task)  # Queue for background thread          │  │
│  │  3. _broadcast_status({"type": "task_start", ...})               │  │
│  └────────────────────────────┬─────────────────────────────────────┘  │
└────────────────────────────────┼────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                  BACKGROUND THREAD (core/loop.py)                        │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │  start_monitoring() - Daemon Thread                              │  │
│  │  while True:                                                     │  │
│  │      task = task_queue.get(timeout=0.5)  # Blocking wait         │  │
│  │      if task:                                                    │  │
│  │          run_agent_loop(task)  # Start main loop                 │  │
│  └────────────────────────────┬─────────────────────────────────────┘  │
└────────────────────────────────┼────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    MAIN AGENT LOOP (core/loop.py)                        │
│                                                                           │
│  ╔═══════════════════════════════════════════════════════════════════╗  │
│  ║  run_agent_loop(task_description)                                 ║  │
│  ║  conversation_history = []                                        ║  │
│  ║  action_count = 0                                                 ║  │
│  ║                                                                   ║  │
│  ║  while not kill_event.is_set():                                  ║  │
│  ║      ┌─────────────────────────────────────────────────────────┐ ║  │
│  ║      │ STEP 1: CAPTURE SCREEN                                  │ ║  │
│  ║      │ screen_image = capture_screen()                         │ ║  │
│  ║      │ → mss library captures primary monitor                  │ ║  │
│  ║      │ → Resize to 1600x900                                    │ ║  │
│  ║      │ → Compress to JPEG (quality 85)                         │ ║  │
│  ║      │ → Returns bytes                                         │ ║  │
│  ║      └─────────────────────────────────────────────────────────┘ ║  │
│  ║                              ▼                                    ║  │
│  ║      ┌─────────────────────────────────────────────────────────┐ ║  │
│  ║      │ STEP 2: EXTRACT TEXT ANCHORS (OCR)                     │ ║  │
│  ║      │ text_anchors = get_screen_elements(screen_image)        │ ║  │
│  ║      │ → Check cache (2-second duration)                       │ ║  │
│  ║      │ → If expired: Run EasyOCR                               │ ║  │
│  ║      │ → Extract text + bounding boxes                         │ ║  │
│  ║      │ → Scale coordinates to native resolution                │ ║  │
│  ║      │ → Cache results                                         │ ║  │
│  ║      │ → Returns: [{"text": "Chrome", "coordinate": [x,y]}]   │ ║  │
│  ║      └─────────────────────────────────────────────────────────┘ ║  │
│  ║                              ▼                                    ║  │
│  ║      ┌─────────────────────────────────────────────────────────┐ ║  │
│  ║      │ STEP 3: CALL LLM                                        │ ║  │
│  ║      │ action_dict = call_llm(screen_image, task, history)     │ ║  │
│  ║      │ → Build system instruction with text anchors            │ ║  │
│  ║      │ → Format conversation history (last 5 actions)          │ ║  │
│  ║      │ → Upload image to LLM API                               │ ║  │
│  ║      │ → Send prompt with task + context                       │ ║  │
│  ║      │ → Parse JSON response                                   │ ║  │
│  ║      │ → Returns: {"action": "left_click",                     │ ║  │
│  ║      │             "coordinate": [x, y],                       │ ║  │
│  ║      │             "reasoning": "...",                         │ ║  │
│  ║      │             "confidence": 0.95}                         │ ║  │
│  ║      └─────────────────────────────────────────────────────────┘ ║  │
│  ║                              ▼                                    ║  │
│  ║      ┌─────────────────────────────────────────────────────────┐ ║  │
│  ║      │ STEP 4: SAVE DEBUG SCREENSHOT (if DEBUG_MODE)           │ ║  │
│  ║      │ _save_debug_screenshot(screen_image, action_dict, n)    │ ║  │
│  ║      │ → Decode JPEG to OpenCV image                           │ ║  │
│  ║      │ → Draw red circle at target coordinate                  │ ║  │
│  ║      │ → Add overlay with action info                          │ ║  │
│  ║      │ → Save to bob-reports/debug_screenshots/                │ ║  │
│  ║      └─────────────────────────────────────────────────────────┘ ║  │
│  ║                              ▼                                    ║  │
│  ║      ┌─────────────────────────────────────────────────────────┐ ║  │
│  ║      │ STEP 5: BROADCAST ACTION TO UI                          │ ║  │
│  ║      │ _broadcast_status({"type": "action", ...})              │ ║  │
│  ║      │ → Put in status_queue (for tray icon)                   │ ║  │
│  ║      │ → Put in ui_queue (for overlay)                         │ ║  │
│  ║      │ → Overlay moves cursor to target coordinate             │ ║  │
│  ║      │ → Status text updated                                   │ ║  │
│  ║      │ time.sleep(0.1)  # Allow UI to update                   │ ║  │
│  ║      └─────────────────────────────────────────────────────────┘ ║  │
│  ║                              ▼                                    ║  │
│  ║      ┌─────────────────────────────────────────────────────────┐ ║  │
│  ║      │ STEP 6: CHECK IF DONE/ERROR                             │ ║  │
│  ║      │ if action_dict['action'] == 'done':                     │ ║  │
│  ║      │     _broadcast_status({"type": "task_complete"})        │ ║  │
│  ║      │     break  # Exit loop                                  │ ║  │
│  ║      │ if action_dict['action'] == 'error':                    │ ║  │
│  ║      │     _broadcast_status({"type": "error"})                │ ║  │
│  ║      │     break  # Exit loop                                  │ ║  │
│  ║      └─────────────────────────────────────────────────────────┘ ║  │
│  ║                              ▼                                    ║  │
│  ║      ┌─────────────────────────────────────────────────────────┐ ║  │
│  ║      │ STEP 7: EXECUTE ACTION                                  │ ║  │
│  ║      │ success = execute_action(action_dict)                   │ ║  │
│  ║      │ → Check for stuck loops                                 │ ║  │
│  ║      │ → Route to appropriate handler:                         │ ║  │
│  ║      │   • open_app → _open_app_via_search()                   │ ║  │
│  ║      │   • left_click → click(x, y)                            │ ║  │
│  ║      │   • type → type_text(text)                              │ ║  │
│  ║      │   • key → press_key(key)                                │ ║  │
│  ║      │   • scroll → scroll(x, y, direction, amount)            │ ║  │
│  ║      │ → Log action to session_log.json                        │ ║  │
│  ║      │ → Returns success/failure                               │ ║  │
│  ║      └─────────────────────────────────────────────────────────┘ ║  │
│  ║                              ▼                                    ║  │
│  ║      ┌─────────────────────────────────────────────────────────┐ ║  │
│  ║      │ STEP 8: UPDATE HISTORY                                  │ ║  │
│  ║      │ action_dict['outcome'] = 'success' or 'warning'         │ ║  │
│  ║      │ conversation_history.append(action_dict)                │ ║  │
│  ║      │ action_count += 1                                       │ ║  │
│  ║      └─────────────────────────────────────────────────────────┘ ║  │
│  ║                              ▼                                    ║  │
│  ║      ┌─────────────────────────────────────────────────────────┐ ║  │
│  ║      │ STEP 9: WAIT FOR SCREEN UPDATE                          │ ║  │
│  ║      │ if action_type in ['click', 'left_click', ...]:         │ ║  │
│  ║      │     time.sleep(1.5)  # UI animations                    │ ║  │
│  ║      │ elif action_type == 'key' and text == 'enter':          │ ║  │
│  ║      │     time.sleep(2.0)  # App launch time                  │ ║  │
│  ║      │ else:                                                   │ ║  │
│  ║      │     time.sleep(0.8)  # Default delay                    │ ║  │
│  ║      └─────────────────────────────────────────────────────────┘ ║  │
│  ║                              │                                    ║  │
│  ║                              └──────────┐                         ║  │
│  ║                                         │                         ║  │
│  ║  ◄──────────────────────────────────────┘                         ║  │
│  ║  Loop back to STEP 1 (next iteration)                            ║  │
│  ╚═══════════════════════════════════════════════════════════════════╝  │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 2. LLM Decision Making Process

```
┌─────────────────────────────────────────────────────────────────┐
│                    LLM DECISION PIPELINE                         │
└─────────────────────────────────────────────────────────────────┘

Input: screen_image (JPEG bytes), task, conversation_history

    │
    ▼
┌─────────────────────────────────────────────────────────────────┐
│ 1. SAVE SCREENSHOT TO TEMP FILE                                 │
│    with tempfile.NamedTemporaryFile() as f:                     │
│        f.write(screen_image)                                    │
│        frame_path = f.name                                      │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│ 2. EXTRACT TEXT ANCHORS (OCR)                                   │
│    text_anchors = get_screen_elements(frame_path)               │
│                                                                 │
│    ┌─────────────────────────────────────────────────────────┐ │
│    │ Check Cache (2-second duration)                         │ │
│    │ if current_time - last_ocr_time < 2.0:                  │ │
│    │     return cached_anchors  # Fast path                  │ │
│    └─────────────────────────────────────────────────────────┘ │
│                             │                                   │
│                             ▼                                   │
│    ┌─────────────────────────────────────────────────────────┐ │
│    │ Run EasyOCR                                             │ │
│    │ reader = easyocr.Reader(['en'], gpu=True)               │ │
│    │ results = reader.readtext(frame_path)                   │ │
│    │                                                         │ │
│    │ For each detection:                                     │ │
│    │   bbox, text, confidence = detection                    │ │
│    │   if confidence < 0.4: skip                             │ │
│    │                                                         │ │
│    │   # Calculate center of bounding box                    │ │
│    │   center_x = avg(bbox x-coordinates)                    │ │
│    │   center_y = avg(bbox y-coordinates)                    │ │
│    │                                                         │ │
│    │   # Scale from 1600x900 to native resolution           │ │
│    │   scale_x = native_width / 1600                         │ │
│    │   scale_y = native_height / 900                         │ │
│    │   native_x = int(center_x * scale_x)                    │ │
│    │   native_y = int(center_y * scale_y)                    │ │
│    │                                                         │ │
│    │   text_anchors.append({                                 │ │
│    │       "text": text,                                     │ │
│    │       "center_coordinate": [native_x, native_y]         │ │
│    │   })                                                    │ │
│    └─────────────────────────────────────────────────────────┘ │
│                                                                 │
│    Returns: [                                                   │
│        {"text": "Chrome", "center_coordinate": [100, 1050]},    │
│        {"text": "Start", "center_coordinate": [30, 1050]},      │
│        ...                                                      │
│    ]                                                            │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│ 3. BUILD SYSTEM INSTRUCTION                                     │
│    system_instruction = _get_system_instruction(text_anchors)   │
│                                                                 │
│    Includes:                                                    │
│    • Role: "You are an AI agent controlling Windows desktop"   │
│    • Text anchor usage examples                                │
│    • Available actions (open_app, click, type, key, scroll)    │
│    • Screen dimensions                                          │
│    • Formatted text anchors:                                    │
│      - "Chrome" at [100, 1050]                                  │
│      - "Start" at [30, 1050]                                    │
│      ...                                                        │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│ 4. BUILD USER PROMPT                                            │
│    user_prompt = f"Task: {task_description}\n\n"                │
│                                                                 │
│    # Add last 5 actions from history                            │
│    for i, action in enumerate(history[-5:]):                    │
│        action_type = action['action']                           │
│        outcome = action.get('outcome', 'unknown')               │
│        coord = action.get('coordinate', [])                     │
│        user_prompt += f"Previous action {i+1}: "                │
│        user_prompt += f"{action_type} at {coord} → {outcome}\n" │
│                                                                 │
│    user_prompt += "\nWhat is the next action?"                  │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│ 5. CALL LLM API (Provider-Specific)                             │
│                                                                 │
│    ┌─────────────────────────────────────────────────────────┐ │
│    │ GEMINI (Google)                                         │ │
│    │ image_part = genai.upload_file(frame_path)              │ │
│    │ response = model.generate_content([                     │ │
│    │     system_instruction,                                 │ │
│    │     image_part,                                         │ │
│    │     user_prompt                                         │ │
│    │ ])                                                      │ │
│    └─────────────────────────────────────────────────────────┘ │
│                                                                 │
│    ┌─────────────────────────────────────────────────────────┐ │
│    │ CLAUDE (Anthropic)                                      │ │
│    │ image_base64 = base64.b64encode(image_bytes)            │ │
│    │ response = client.messages.create(                      │ │
│    │     model="claude-3-5-sonnet-20241022",                 │ │
│    │     system=system_instruction,                          │ │
│    │     messages=[{                                         │ │
│    │         "role": "user",                                 │ │
│    │         "content": [                                    │ │
│    │             {"type": "image", "source": {...}},         │ │
│    │             {"type": "text", "text": user_prompt}       │ │
│    │         ]                                               │ │
│    │     }]                                                  │ │
│    │ )                                                       │ │
│    └─────────────────────────────────────────────────────────┘ │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│ 6. PARSE JSON RESPONSE                                          │
│    response_text = response.text                                │
│                                                                 │
│    # Extract JSON from markdown code blocks if present          │
│    if "```json" in response_text:                               │
│        json_match = re.search(r'```json\s*(\{.*?\})\s*```')     │
│        response_text = json_match.group(1)                      │
│                                                                 │
│    action_dict = json.loads(response_text)                      │
│                                                                 │
│    Example:                                                     │
│    {                                                            │
│        "action": "left_click",                                  │
│        "coordinate": [100, 1050],                               │
│        "reasoning": "Clicking Chrome icon on taskbar",          │
│        "confidence": 0.95                                       │
│    }                                                            │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│ 7. NORMALIZE AND SCALE COORDINATES                              │
│    action_dict = normalize_and_scale_action(action_dict)        │
│                                                                 │
│    • Ensure 'coordinate' field exists (not 'x'/'y')             │
│    • Validate coordinate format: [x, y]                         │
│    • Ensure coordinates are integers                            │
│    • Clamp to screen bounds                                     │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
                        Return action_dict
```

---

## 3. Action Execution Flow

```
┌─────────────────────────────────────────────────────────────────┐
│              ACTION EXECUTION (executor/actions.py)              │
└─────────────────────────────────────────────────────────────────┘

Input: action_dict from LLM

    │
    ▼
┌─────────────────────────────────────────────────────────────────┐
│ 1. ADD TO HISTORY                                               │
│    action_history.append(action_dict)  # Deque, maxlen=10       │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│ 2. STUCK LOOP DETECTION                                         │
│    if _is_stuck_loop(action_history):                           │
│                                                                 │
│    ┌─────────────────────────────────────────────────────────┐ │
│    │ Type 1: Timeout (15 seconds without progress)           │ │
│    │ if current_time - last_progress_time > 15:              │ │
│    │     return True                                         │ │
│    └─────────────────────────────────────────────────────────┘ │
│                                                                 │
│    ┌─────────────────────────────────────────────────────────┐ │
│    │ Type 2: Exact Repetition (3 identical actions)          │ │
│    │ last_three = history[-3:]                               │ │
│    │ if all same action type AND same coordinates:           │ │
│    │     return True                                         │ │
│    └─────────────────────────────────────────────────────────┘ │
│                                                                 │
│    ┌─────────────────────────────────────────────────────────┐ │
│    │ Type 3: Semantic Loop (5 actions in same 100px region)  │ │
│    │ last_five = history[-5:]                                │ │
│    │ coords = extract_coordinates(last_five)                 │ │
│    │ if all_in_same_region(coords, radius=100):              │ │
│    │     return True                                         │ │
│    └─────────────────────────────────────────────────────────┘ │
│                                                                 │
│    If stuck loop detected:                                      │
│        kill_event.set()  # Stop agent                           │
│        status_queue.put({"type": "stuck", ...})                 │
│        return False                                             │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│ 3. ROUTE TO ACTION HANDLER                                      │
│    action_type = action_dict.get('action')                      │
│                                                                 │
│    ┌─────────────────────────────────────────────────────────┐ │
│    │ open_app                                                │ │
│    │ → _open_app_via_search(app_name)                        │ │
│    │   1. pyautogui.press('win')                             │ │
│    │   2. time.sleep(0.3)                                    │ │
│    │   3. pyautogui.write(app_name, interval=0.05)           │ │
│    │   4. time.sleep(0.5)                                    │ │
│    │   5. pyautogui.press('enter')                           │ │
│    │   6. time.sleep(1.0)  # Wait for app launch             │ │
│    └─────────────────────────────────────────────────────────┘ │
│                                                                 │
│    ┌─────────────────────────────────────────────────────────┐ │
│    │ left_click / right_click / double_click                 │ │
│    │ → click(x, y, button, clicks)                           │ │
│    │   1. validate_coordinates(x, y)                         │ │
│    │   2. pyautogui.click(x=x, y=y, clicks=clicks,           │ │
│    │                      button=button)                     │ │
│    └─────────────────────────────────────────────────────────┘ │
│                                                                 │
│    ┌─────────────────────────────────────────────────────────┐ │
│    │ mouse_move                                              │ │
│    │ → mouse_move(x, y, duration=0.1)                        │ │
│    │   1. validate_coordinates(x, y)                         │ │
│    │   2. pyautogui.moveTo(x, y, duration=0.1)               │ │
│    └─────────────────────────────────────────────────────────┘ │
│                                                                 │
│    ┌─────────────────────────────────────────────────────────┐ │
│    │ type                                                    │ │
│    │ → type_text(text, interval=0.03)                        │ │
│    │   1. pyautogui.write(text, interval=0.03)               │ │
│    └─────────────────────────────────────────────────────────┘ │
│                                                                 │
│    ┌─────────────────────────────────────────────────────────┐ │
│    │ key                                                     │ │
│    │ → press_key(key_combination)                            │ │
│    │   if '+' in key_combination:                            │ │
│    │       keys = key_combination.split('+')                 │ │
│    │       pyautogui.hotkey(*keys)  # e.g., ctrl+c           │ │
│    │   else:                                                 │ │
│    │       pyautogui.press(key)  # e.g., enter               │ │
│    └─────────────────────────────────────────────────────────┘ │
│                                                                 │
│    ┌─────────────────────────────────────────────────────────┐ │
│    │ scroll                                                  │ │
│    │ → scroll(x, y, direction, amount)                       │ │
│    │   1. validate_coordinates(x, y)                         │ │
│    │   2. pyautogui.moveTo(x, y, duration=0.1)               │ │
│    │   3. scroll_amount = amount if direction=='up'          │ │
│    │                      else -amount                       │ │
│    │   4. pyautogui.scroll(scroll_amount)                    │ │
│    └─────────────────────────────────────────────────────────┘ │
│                                                                 │
│    ┌─────────────────────────────────────────────────────────┐ │
│    │ done                                                    │ │
│    │ → kill_event.set()  # Signal completion                 │ │
│    │   return True                                           │ │
│    └─────────────────────────────────────────────────────────┘ │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│ 4. LOG ACTION                                                   │
│    log_action_to_file(action_dict, success, execution_time)     │
│                                                                 │
│    Appends to session_log.json:                                 │
│    {                                                            │
│        "timestamp": "2024-01-15T10:30:45.123",                  │
│        "action": "left_click",                                  │
│        "details": {...},                                        │
│        "success": true,                                         │
│        "execution_time_ms": 15.3                                │
│    }                                                            │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
                        Return success
```

---

## 4. UI Update Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    UI UPDATE MECHANISM                           │
└─────────────────────────────────────────────────────────────────┘

Background Thread                Main Thread (Qt Event Loop)
(core/loop.py)                   (main.py)

     │                                    │
     │ _broadcast_status(status_dict)     │
     ├────────────────────────────────────┤
     │                                    │
     │ status_queue.put(status_dict) ────>│
     │ ui_queue.put(status_dict) ─────────>│
     │                                    │
     │                                    │ QTimer (50ms interval)
     │                                    │ update_status()
     │                                    │
     │                                    ▼
     │                          ┌─────────────────────────┐
     │                          │ while not ui_queue.empty(): │
     │                          │   status = ui_queue.get()   │
     │                          │                         │
     │                          │   if status['type'] == 'action': │
     │                          │     # Move cursor       │
     │                          │     coord = status['action']['coordinate'] │
     │                          │     overlay.set_reticle_position(coord[0], coord[1]) │
     │                          │                         │
     │                          │     # Set state         │
     │                          │     if action == 'left_click': │
     │                          │       overlay.set_reticle_state('clicking') │
     │                          │     elif action == 'mouse_move': │
     │                          │       overlay.set_reticle_state('moving') │
     │                          │                         │
     │                          │   elif status['type'] == 'thinking': │
     │                          │     overlay.set_reticle_state('thinking') │
     │                          │     overlay.set_status_text("🤔 Thinking...") │
     │                          │                         │
     │                          │   elif status['type'] == 'task_complete': │
     │                          │     overlay.set_status_text("✅ Done!") │
     │                          │     QTimer.singleShot(3000, hide_overlay) │
     │                          │                         │
     │                          │   elif status['type'] == 'error': │
     │                          │     overlay.set_status_text("❌ Error") │
     │                          │     QTimer.singleShot(5000, hide_overlay) │
     │                          └─────────────────────────┘
     │                                    │
     │                                    ▼
     │                          Overlay widget updates:
     │                          • Position (x, y)
     │                          • Reticle color/animation
     │                          • Status text
     │                          • Visibility
```

---

*These flow diagrams provide a visual understanding of AXON's execution pipeline from user input to action completion.*