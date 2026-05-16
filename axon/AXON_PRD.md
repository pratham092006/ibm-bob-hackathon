# AXON — Live AI Desktop Agent
### IBM BOB Hackathon · 24-hour Sprint · 3-person team

> **What it is:** An agentic cursor that sees your screen live, understands your goal, and moves the cursor on its own — continuously, across any app — until the task is done.

---

## Table of Contents
1. [IBM Bob Requirement](#ibm-bob-requirement)
2. [How It Works — The Live Agent Loop](#how-it-works)
3. [Tech Stack](#tech-stack)
4. [Project File Structure](#project-file-structure)
5. [Integration Contract](#integration-contract)
6. [Team Split — Who Builds What](#team-split)
7. [24-Hour Timeline](#24-hour-timeline)
8. [Demo Scenarios](#demo-scenarios)
9. [What Wins Top 3](#what-wins-top-3)
10. [Risk Flags](#risk-flags)

---

## IBM Bob Requirement

> **Bob is your coding tool, not a runtime API.**

- Use IBM Bob inside VS Code to write all code throughout the hackathon
- Every teammate should actively use Bob (ask it to write functions, debug, refactor)
- At submission: export all Bob session reports → commit them to `/bob-reports/` in the repo
- In your demo video: briefly show a Bob session writing a key module
- The judges are specifically checking for **genuine, heavy Bob usage** — not a bolt-on mention

---

## How It Works

### The Live Agent Loop

```
User types / speaks task
        │
        ▼
┌─────────────────┐     frame      ┌─────────────────┐     action JSON   ┌─────────────────┐
│  Capture live   │ ─────────────► │   Vision LLM    │ ────────────────► │ Execute action  │
│  frame (mss)    │                │ Computer Use API │                   │ pyautogui/pynput│
│   < 5ms grab    │                │  ~300–600ms      │                   │   instant       │
└─────────────────┘                └─────────────────┘                   └─────────────────┘
        ▲                                                                          │
        └──────────────────── next frame → loop repeats until task done ──────────┘

                                                    [Ctrl+Shift+K] = instant kill at any point
```

### Loop in Code

```python
while not kill_event.is_set():
    frame = capture_frame()                    # mss grabs live screen < 5ms
    frame_b64 = compress_frame(frame)          # resize to 1280×720, JPEG 85
    action = call_computer_use_api(frame_b64, goal)   # {action, coordinate, text}
    execute(action)                            # pyautogui acts immediately
    status_queue.put(action)                   # overlay updates HUD
```

### What the API returns

The Anthropic Computer Use API returns structured actions — no parsing guesswork:

```json
{"action": "left_click",  "coordinate": [420, 310]}
{"action": "type",        "text": "Hello World"}
{"action": "scroll",      "coordinate": [340, 400], "direction": "down", "amount": 3}
{"action": "key",         "text": "ctrl+s"}
{"action": "mouse_move",  "coordinate": [200, 150]}
```

---

## Tech Stack

| Layer | Tool | Why |
|---|---|---|
| Screen capture | `mss` | Grabs frames in < 5ms. Fastest cross-platform option. |
| AI brain | Anthropic Computer Use API (`claude-3-5-sonnet`) | Built exactly for this — returns structured actions from a screenshot + goal. |
| Mouse control | `pyautogui` | move, click, scroll, drag. Works on Windows without admin. |
| Keyboard / hotkeys | `pynput` | Global listener for kill switch + voice hotkey. |
| Overlay UI | `PyQt6` | Transparent borderless window on top of everything. Use `WA_TranslucentBackground` + `WindowStaysOnTopHint` + `FramelessWindowHint`. |
| Voice input | `faster-whisper` (tiny model) | Local, CPU-only. Hold Alt+Space → speak → transcribed in ~1s. No API key. |
| System tray | `pystray` + `Pillow` | Status icon, pause/resume/quit from tray. |
| Packaging | `PyInstaller` | Single `.exe` judges can double-click. No Python install needed. |
| Dev tool | IBM Bob (VS Code) | Used to write all code. Export session reports for submission. |

### Install

```bash
pip install mss pyautogui pynput PyQt6 pystray Pillow faster-whisper anthropic pyinstaller
```

---

## Project File Structure

```
axon/
├── core/
│   ├── capture.py        # Dev 1 — mss frame grab + compress
│   ├── llm.py            # Dev 1 — Computer Use API call + response parse
│   ├── loop.py           # Dev 1 — main while-loop, kill_event check
│   └── planner.py        # Dev 1 — goal → subtask decomposition
├── executor/
│   ├── actions.py        # Dev 2 — mouse_move, click, type, scroll, key
│   ├── kill_switch.py    # Dev 2 — pynput global listener, threading.Event
│   ├── win_api.py        # Dev 2 — Win32 active window + app detection
│   └── app_handlers.py   # Dev 2 — app-specific keybind shortcuts
├── ui/
│   ├── overlay.py        # Dev 3 — PyQt6 transparent fullscreen overlay
│   ├── reticle.py        # Dev 3 — glowing circle predicting next cursor move
│   ├── input_dialog.py   # Dev 3 — floating task input + voice toggle button
│   └── tray.py           # Dev 3 — system tray icon + status menu
├── bob-reports/          # IBM Bob session exports go here
├── main.py               # All — entry point, wires everything together
├── config.py             # All — API keys, constants, tuning params
└── requirements.txt      # All
```

---

## Integration Contract

> **Agree on this at Hour 0 before anyone writes a line of code.**

This is the only shared interface between the three devs. Everything else is internal.

### Dev 2 exposes:

```python
# executor/kill_switch.py
kill_event = threading.Event()   # set() to halt, clear() to resume

# executor/actions.py
def execute(action: dict) -> None:
    """
    Accepts an action dict from the Computer Use API response:
    {"action": "left_click", "coordinate": [x, y]}
    {"action": "type", "text": "..."}
    {"action": "scroll", "coordinate": [x, y], "direction": "down", "amount": 3}
    {"action": "key", "text": "ctrl+s"}
    {"action": "mouse_move", "coordinate": [x, y]}
    """
```

### Dev 1's loop uses:

```python
from executor.actions import execute
from executor.kill_switch import kill_event

while not kill_event.is_set():
    frame = capture_frame()
    action = call_llm(frame, goal)
    execute(action)
    status_queue.put({"step": current_step, "action": action})
```

### Dev 3's overlay subscribes to:

```python
# shared in config.py
import queue
status_queue = queue.Queue()   # Dev 1 puts, Dev 3 gets
```

**That's it.** Three touch points. Do not add more shared state.

---

## Team Split

### Dev 1 — Vision & Brain

**Owns:** `core/`

| Task | Detail |
|---|---|
| mss capture loop | `sct.grab(monitor)` in a tight loop. Return PIL Image. |
| Frame preprocessing | Resize to 1280×720, save as JPEG quality 85, base64 encode. Reduces payload ~70%. |
| Computer Use API call | POST to Anthropic API with screenshot + system prompt + user goal. |
| Response parser | Extract action dict from API response content blocks. |
| Main agent loop | `while not kill_event.is_set()` — calls capture → llm → execute → status. |
| Task planner | Break complex goals into ordered subtasks. Store as a list, tick off each one. |
| Loop throttle | If LLM call is still pending, skip the next frame capture. Don't pile up requests. |

**Key prompt to send the model:**

```
System: You are controlling a Windows desktop. At each step you receive a screenshot 
and return exactly one action. Be precise with coordinates. When the task is complete, 
return {"action": "done"}.

User: Goal: {user_goal}
Current step: {step_description}
[screenshot attached]
```

---

### Dev 2 — Executor & Safety

**Owns:** `executor/`

| Task | Detail |
|---|---|
| `execute(action)` | Route action dict to the right pyautogui call. |
| Kill switch | `pynput` global listener. On Ctrl+Shift+K: `kill_event.set()`, stop all pyautogui motion. |
| Win32 app detection | `win32gui.GetForegroundWindow()` → know which app is active. |
| App-specific handlers | Video editor: use I/O keybinds. Browser: Ctrl+L to focus address bar. |
| Stuck-loop detection | If the same action fires 3× in a row, pause and push a "stuck" signal to status_queue. |
| Action log | Write every executed action to `session_log.json` with timestamp. |

**Action router:**

```python
def execute(action: dict):
    match action.get("action"):
        case "mouse_move":
            pyautogui.moveTo(*action["coordinate"], duration=0.1)
        case "left_click":
            pyautogui.click(*action["coordinate"])
        case "right_click":
            pyautogui.rightClick(*action["coordinate"])
        case "type":
            pyautogui.typewrite(action["text"], interval=0.03)
        case "key":
            pyautogui.hotkey(*action["text"].split("+"))
        case "scroll":
            pyautogui.scroll(action.get("amount", 3) * (1 if action["direction"]=="up" else -1),
                             x=action["coordinate"][0], y=action["coordinate"][1])
        case "done":
            kill_event.set()
```

---

### Dev 3 — UI, Demo & Submission

**Owns:** `ui/`, repo, demo

| Task | Detail |
|---|---|
| Transparent overlay | PyQt6 frameless window, always on top, transparent background. |
| **Target reticle** ⭐ | A glowing ring that appears at the next action's coordinate *before* the cursor moves there. This is your biggest visual wow moment. |
| Status HUD | Shows: current task name, current step, model response time, action count. |
| Task input dialog | Floating mini-window for typing a task. Alt+Space toggles voice mode. |
| System tray | AXON icon, right-click menu: Pause / Resume / New Task / Quit. |
| GitHub + README | Public repo, clear setup instructions, architecture section, screenshot of overlay. |
| IBM Bob export | Export all session reports → `/bob-reports/`. Add a `BOB_USAGE.md` summarising which features Bob helped build. |
| Demo video | 3–4 min max. OBS or Loom. Script below. |

**Reticle implementation sketch:**

```python
class Reticle(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(40, 40)
        self._opacity = 0.0

    def move_to(self, x, y):
        self.move(x - 20, y - 20)   # center the ring on the coordinate
        self.show()
        self._fade_in()

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        pen = QPen(QColor(80, 200, 120, int(200 * self._opacity)), 2)
        p.setPen(pen)
        p.drawEllipse(4, 4, 32, 32)
```

---

## 24-Hour Timeline

```
Hour  0–1   KICKOFF (all 3)
             ├─ Clone repo, install deps
             ├─ Agree on integration contract
             ├─ Everyone opens IBM Bob in VS Code
             ├─ Dev 1: confirm mss grabs a frame
             ├─ Dev 2: confirm pyautogui can click a point
             └─ Dev 3: confirm PyQt6 window opens on top

Hour  1–6   CORE BUILD (parallel)
             ├─ Dev 1: mss loop → API → parse action (target: printing actions by H4)
             ├─ Dev 2: execute() working for all action types + kill switch active
             └─ Dev 3: overlay + HUD visible + task input dialog functional

Hour  6–8   FIRST INTEGRATION (all 3)
             └─ Wire all tracks together
                Test: "Open Notepad and type Hello World"
                If this works end-to-end → you are in top-3 territory

Hour  8–14  DEMO SCENARIOS + VOICE (parallel)
             ├─ Dev 1: add faster-whisper voice transcription
             ├─ Dev 2: Win32 app detection + app-specific handlers
             └─ Dev 3: target reticle (PRIORITY #1) + tray icon

Hour 14–18  BUG HUNT + STABILITY (all 3)
             ├─ Run all 3 demo scenarios 5× each
             ├─ Test kill switch in every state
             ├─ Add stuck-loop detection
             └─ FREEZE CODE after H18 — no new features

Hour 18–21  PACKAGING + SUBMISSION PREP
             ├─ Dev 2: PyInstaller → AXON.exe, test on clean VM
             ├─ Dev 3: README, BOB_USAGE.md, export Bob session reports
             └─ Dev 1: fresh run of all demos on the packaged exe

Hour 21–23  RECORD DEMO VIDEO (Dev 3 leads)
             └─ Script: 30s intro → Scenario 1 (60s) → Scenario 2 (40s) → Scenario 3 (50s)
                Show IBM Bob session briefly at end

Hour 23–24  SUBMIT
             ├─ Confirm repo is PUBLIC
             ├─ Submit on lablab.ai: GitHub URL + video link + Bob export
             └─ Done
```

---

## Demo Scenarios

### Scenario 1 — Warm-up (browser + writing)
> **"Search Google for the top 3 AI coding tools and paste a summary into Notepad."**

AXON opens Chrome, types the search query, reads the results, opens Notepad, types a 3-line summary. Judges see a real multi-app task from one sentence.

### Scenario 2 — Practical utility (file management)
> **"Rename all the screenshots in this folder to include today's date."**

AXON opens File Explorer, selects files, renames them. Pure cursor control, no code. Shows it understands file system UI naturally.

### Scenario 3 — The hero moment (video editor)
> **"Trim the first 30 seconds off this video and export it."**

AXON opens DaVinci Resolve or Premiere, finds the timeline, uses I/O keyboard shortcuts to mark the cut, triggers export. **Practice this 10+ times before the demo.** This is the clip judges will remember.

If Scenario 3 isn't stable by H12 → simplify to VLC or Windows Media Player. A working simple demo beats a broken complex one.

---

## What Wins Top 3

**1. The reticle is the money shot**
A glowing circle that appears at the next action coordinate *before* the cursor moves there makes AXON feel eerily intelligent. Judges will screenshot this. Dev 3 should prioritize it above everything else in the UI.

**2. Live = instantly understood**
No other 24h team is likely doing live continuous computer use. Most will take a screenshot, wait, respond. Yours moves the cursor in real time. That difference requires no explanation — it's immediately visible.

**3. Kill switch = safety story**
Judges will ask "but what if it goes wrong?" You have an answer: Ctrl+Shift+K halts everything instantly. Responsible AI — which IBM specifically values.

**4. Heavy IBM Bob usage**
Show 3–4 Bob sessions in the export. In the demo video, briefly show Bob writing a key module. Judges are looking for real Bob usage across the whole build, not a mention.

**5. Extensibility pitch**
In the Q&A, pitch the roadmap: macro recorder (learn a task once, replay it), scheduled tasks ("do this every Monday"), multi-monitor support, plugin API for new apps. This signals a real product, not a weekend hack.

---

## Risk Flags

⚠️ **Computer Use API latency** — if responses are slow (> 1s), the cursor feels laggy.
Mitigate: resize frames to 1280×720 JPEG before sending, set `max_tokens=512`, run on good wifi.

⚠️ **Integration hell at H6** — this is where most hackathon projects die.
Mitigate: keep the integration contract simple. One Event, one Queue, one execute(). Do not add more shared state.

⚠️ **Scenario 3 complexity** — video editor UIs are complex and may resist automation.
Mitigate: have Scenario 2 as your fallback. Know which one to show based on how stable things are by H14.

⚠️ **Mac skip** — PyAutoGUI on Mac needs Accessibility permissions that require system settings changes and reboots. Windows only for the 24h build. Mention Mac as roadmap in your pitch.

---

## Submission Checklist

- [ ] Repo is **public** on GitHub
- [ ] `README.md` with setup instructions, features, architecture
- [ ] `BOB_USAGE.md` summarising how IBM Bob was used
- [ ] `/bob-reports/` contains exported IBM Bob session reports
- [ ] `requirements.txt` up to date
- [ ] `AXON.exe` tested on a clean machine
- [ ] Demo video uploaded (3–4 min, unlisted YouTube or Loom)
- [ ] Submitted on lablab.ai before deadline

---

*Built for the IBM BOB Hackathon on lablab.ai · AXON · MIT License*
