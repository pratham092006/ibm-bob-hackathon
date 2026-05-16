# AXON - How to Run

## 🚀 Quick Start

### 1. Install Dependencies
```bash
cd axon
pip install -r requirements.txt
```

### 2. Configure API Key
The Gemini API key is already configured in `config.py`. If you need to change it:
```python
# In config.py
GEMINI_API_KEY = "your-api-key-here"
```

### 3. Run AXON
```bash
python main.py
```

## ⌨️ Keyboard Controls

### 🛑 KILL SWITCH (EMERGENCY STOP)
**Press F12** - Immediately stops AXON and all actions

This is your emergency stop button. Use it if:
- AXON is doing something unexpected
- You need to regain control immediately
- The application gets stuck in a loop

### Other Controls
- **System Tray Icon** - Right-click for menu options
- **Task Input Dialog** - Enter your task when prompted

## 🎯 What You'll See

### Reticle Cursor
AXON displays a **glowing animated cursor** that shows where it plans to click next:
- **Blue** 🔵 - Idle/waiting
- **Orange** 🟠 - Thinking/analyzing
- **Green** 🟢 - Moving cursor
- **Red** 🔴 - Clicking

The reticle appears **alongside your normal cursor** - it's NOT a fullscreen overlay or black box.

### Status HUD (Top-Left Corner)
Shows current task information:
- Current task
- Current step
- Response time
- Action count

## 🔧 Model Selection

AXON supports two Gemini models:

### Gemini 2.5 Flash (Default)
- ⚡ **Faster** responses
- 💰 **Lower cost**
- ✅ Good for most tasks

### Gemini 2.5 Pro
- 🧠 **More capable**
- 🎯 **Higher accuracy**
- ⏱️ Slower responses

Switch models in the task input dialog dropdown.

## 🧪 Testing

### Test Gemini API Connection
```bash
python test_gemini.py
```
This verifies:
- API key is valid
- Model switching works
- Response parsing works

### Test Individual Components
```bash
python test_actions.py      # Test action execution
python test_kill_switch.py  # Test emergency stop
python test_win_api.py      # Test Windows API
```

## 🐛 Troubleshooting

### Black Screen Issue
**FIXED!** The overlay is now truly transparent. You should only see:
- The glowing reticle cursor
- Optional status HUD in top-left

If you still see a black screen:
1. Press **F12** to stop AXON
2. Close the application
3. Restart with `python main.py`

### Can't Exit the Application
**Press F12** - This is the kill switch that stops everything immediately.

### Stuck in a Loop
1. **Press F12** to activate kill switch
2. The application will stop gracefully
3. Check console output for error messages

### API Errors
- Verify your Gemini API key in `config.py`
- Check your internet connection
- Run `python test_gemini.py` to diagnose

## 📊 Performance Tips

### For Speed
```python
# In config.py
CURRENT_MODEL = "flash"
JPEG_QUALITY = 75
```

### For Accuracy
```python
# In config.py
CURRENT_MODEL = "pro"
JPEG_QUALITY = 90
```

## 🎮 Example Tasks

Try these tasks to test AXON:
- "Open Notepad"
- "Click the Start button"
- "Type 'Hello World'"
- "Open Chrome and search for Python"

## 🔐 Safety Features

1. **Kill Switch (F12)** - Emergency stop
2. **Transparent Overlay** - See your desktop at all times
3. **Click-through Window** - Doesn't block your mouse
4. **Visual Feedback** - Always know what AXON is doing

## 📝 Notes

- AXON runs in the background with a system tray icon
- The reticle cursor is always visible when AXON is active
- All actions are logged to the console
- Press F12 anytime to stop

## 🏆 Hackathon Winner Features

✅ **Transparent Reticle** - No black screen, just a cursor indicator
✅ **F12 Kill Switch** - Instant emergency stop
✅ **Dual Model Support** - Switch between Flash and Pro
✅ **Real-time Visual Feedback** - See what AXON is thinking
✅ **Safe & Controllable** - You're always in control

---

**Made with Bob** 🤖

For technical details, see [PROJECT_STATUS.md](PROJECT_STATUS.md)