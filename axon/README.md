# AXON — Live AI Desktop Agent 🤖

An agentic cursor that sees your screen live, understands your goal, and moves the cursor autonomously until the task is complete.

## ✨ Key Features

- 🎯 **Transparent Reticle Cursor** - See a glowing cursor indicator, NOT a black fullscreen overlay
- 🛑 **F12 Kill Switch** - Emergency stop anytime with one keypress
- ⚡ **Dual AI Models** - Switch between Gemini 2.5 Flash (fast) and Pro (accurate)
- 👁️ **Real-time Visual Feedback** - Color-coded states (blue=idle, orange=thinking, green=moving, red=clicking)
- 🔒 **Safe & Controllable** - Click-through overlay, always see your desktop

## 🚀 Quick Start

1. **Install dependencies:**
```bash
cd axon
pip install -r requirements.txt
```

2. **Run AXON:**
```bash
python main.py
```

3. **Emergency Stop:** Press **F12** anytime to stop AXON immediately

## ⌨️ Controls

- **F12** - Kill switch (emergency stop)
- **System Tray** - Right-click for menu
- **Task Dialog** - Enter your task when prompted

## 🎨 What You'll See

The reticle cursor appears **alongside your normal cursor** with color-coded states:
- 🔵 **Blue** - Idle/waiting
- 🟠 **Orange** - Thinking/analyzing
- 🟢 **Green** - Moving cursor
- 🔴 **Red** - Clicking

**No black screen, no fullscreen overlay** - just a transparent cursor indicator!

## 📚 Documentation

### Getting Started
- [HOW_TO_RUN.md](HOW_TO_RUN.md) - Detailed setup and usage guide
- [QUICK_REFERENCE.md](QUICK_REFERENCE.md) - Quick reference for developers

### Architecture & Design
- [ARCHITECTURE.md](ARCHITECTURE.md) - Complete system architecture and component details
- [FLOW_DIAGRAMS.md](FLOW_DIAGRAMS.md) - Visual flow diagrams and execution traces

### Configuration
- [LLM_SETUP_GUIDE.md](LLM_SETUP_GUIDE.md) - Configure different LLM providers
- [NVIDIA_MODELS_GUIDE.md](NVIDIA_MODELS_GUIDE.md) - NVIDIA NIM models setup
- [FREE_LLM_OPTIONS.md](FREE_LLM_OPTIONS.md) - Free LLM alternatives

### Project Info
- [PROJECT_STATUS.md](PROJECT_STATUS.md) - Current project status and features
- [AXON_PRD.md](AXON_PRD.md) - Product requirements document

## 🧪 Testing

```bash
python test_gemini.py      # Test Gemini API connection
python test_kill_switch.py # Test emergency stop
python test_actions.py     # Test action execution
```

## 🏆 Hackathon Winner Features

✅ Transparent overlay (no black screen!)
✅ F12 emergency kill switch
✅ Dual model support (Flash/Pro)
✅ Real-time visual feedback
✅ Safe and controllable

## 👥 Team

- **Dev 1 (Joshua)**: Vision & Brain - `core/` (LLM integration, Gemini API)
- **Dev 2 (Ashish)**: Executor & Safety - `executor/` (Actions, kill switch)
- **Dev 3 (Pratham)**: UI & Demo - `ui/` (Overlay, reticle, tray)

## 🤖 Built with IBM Bob

This project was built using IBM Bob AI assistant. Session reports are in `/bob-reports/`.

---

**Made with Bob** 🤖