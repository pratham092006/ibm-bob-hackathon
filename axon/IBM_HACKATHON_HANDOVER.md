# AXON - IBM Hackathon Handover Document

## 🏆 Executive Summary

**Project Name:** AXON - Live AI Desktop Agent  
**Tagline:** An agentic cursor that sees your screen live, understands your goal, and moves autonomously until the task is complete  
**Hackathon:** IBM Bob Hackathon (24-hour sprint)  
**Team Size:** 3 developers  
**Status:** ✅ Production Ready

### Key Achievements

- ✅ **Fully Functional AI Desktop Agent** - Autonomous task execution across any Windows application
- ✅ **Multi-LLM Support** - 5 providers (Gemini, Claude, OpenRouter, NVIDIA, Ollama) with seamless switching
- ✅ **Advanced Features** - Global hotkey (Alt+G), context-aware help, print automation, emergency kill switch
- ✅ **Production Ready** - Comprehensive error handling, safety features, and extensive documentation
- ✅ **Built with IBM Bob** - Entire codebase developed using IBM Bob AI assistant

### Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **AI Brain** | Gemini 2.5 / Claude 3.5 / Ollama | Vision-language models for screen understanding |
| **Screen Capture** | mss | Ultra-fast screenshot capture (<5ms) |
| **OCR** | EasyOCR | Text extraction and coordinate grounding |
| **Automation** | PyAutoGUI, PyWin32 | Mouse/keyboard control and Windows API |
| **UI Framework** | PyQt6 | Transparent overlay and system tray |
| **Hotkeys** | pynput | Global keyboard listener (Alt+G, F12) |

### Target Audience

- **Power Users** - Automate repetitive desktop tasks
- **Developers** - Quick access to AI help while coding
- **Professionals** - Streamline document workflows
- **Accessibility** - Voice-controlled computer interaction
- **Enterprise** - Scalable automation platform

---

## 📋 Project Overview

### What is AXON?

AXON is a revolutionary AI-powered desktop automation agent that combines computer vision, natural language understanding, and autonomous action execution. Unlike traditional automation tools that require scripting or recording, AXON understands natural language commands and executes them by visually analyzing your screen in real-time.

**Example Workflow:**
```
User: "Open Chrome and search for Python tutorials"
↓
AXON captures screen → Analyzes with AI → Clicks Start menu
→ Types "Chrome" → Opens Chrome → Clicks search bar
→ Types "Python tutorials" → Presses Enter
→ Task complete! ✅
```

### Problem It Solves

1. **Repetitive Tasks** - Manual clicking and typing wastes time
2. **Complex Workflows** - Multi-step processes are tedious
3. **Learning Curve** - Traditional automation requires programming
4. **Context Switching** - Constantly switching between apps disrupts flow
5. **Accessibility** - Not everyone can easily use mouse/keyboard

### Key Features & Capabilities

#### 🎯 Core Features

1. **Vision-Based Control**
   - Real-time screen analysis using vision-language models
   - OCR text extraction for precise coordinate grounding
   - Understands UI elements without pre-training

2. **Natural Language Interface**
   - Speak or type your task in plain English
   - No scripting or programming required
   - Contextual understanding of complex requests

3. **Autonomous Execution**
   - Continuous loop: capture → analyze → execute → repeat
   - Self-correcting behavior based on screen feedback
   - Handles multi-step workflows automatically

4. **Multi-LLM Support** (5 Providers)
   - **Gemini** (Google) - Fast and cost-effective
   - **Claude** (Anthropic) - Most accurate and reliable
   - **OpenRouter** - Access to multiple models with one API
   - **NVIDIA** - Free tier with powerful models
   - **Ollama** - 100% local, private, offline capable

5. **Global Hotkey System (Alt+G)**
   - **Task Dialog Mode** - Quick task submission from anywhere
   - **Context Help Mode** - Select text, press Alt+G, get AI explanation
   - Works system-wide across all applications

6. **Safety & Control**
   - **F12 Kill Switch** - Emergency stop anytime
   - **Transparent Overlay** - Always see your desktop
   - **Stuck-Loop Detection** - Automatic recovery from infinite loops
   - **Action Logging** - Complete audit trail in session_log.json

7. **Advanced Automation**
   - **Print Document Integration** - Natural language printing
   - **App-Specific Handlers** - Optimized for common applications
   - **Windows API Integration** - Deep OS-level control
   - **Voice Input** - Speak your commands (faster-whisper)

### Unique Selling Points

1. **Live Vision Loop** - Continuous screen analysis, not one-shot automation
2. **Zero Configuration** - Works out of the box with any application
3. **Multi-Provider Flexibility** - Switch LLMs based on speed/cost/privacy needs
4. **Context-Aware Help** - Built-in AI assistant for learning and troubleshooting
5. **Production Ready** - Comprehensive error handling and safety features
6. **Extensible Architecture** - Easy to add new actions and integrations

---

## 🏗️ Technical Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                     AXON Architecture                        │
└─────────────────────────────────────────────────────────────┘

┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   UI Layer   │────▶│  Core Brain  │────▶│   Executor   │
│  (PyQt6)     │     │  (LLM+OCR)   │     │ (PyAutoGUI)  │
└──────────────┘     └──────────────┘     └──────────────┘
      │                     │                     │
      ▼                     ▼                     ▼
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  - Overlay   │     │ - LLM API    │     │ - Actions    │
│  - Reticle   │     │ - OCR        │     │ - Win API    │
│  - Dialog    │     │ - Capture    │     │ - Hotkeys    │
│  - Tray      │     │ - Loop       │     │ - Safety     │
└──────────────┘     └──────────────┘     └──────────────┘
```

### Component Details

#### 1. Core (Vision & Brain) - `core/`

- **`loop.py`** (373 lines) - Main agent control loop
- **`llm.py`** (1096 lines) - Multi-provider LLM integration
- **`capture.py`** (63 lines) - Ultra-fast screen capture
- **`context_help.py`** - AI-powered help system
- **`planner.py`** - Task planning (future)

#### 2. Executor (Action & Safety) - `executor/`

- **`actions.py`** (606 lines) - Action execution engine
- **`win_api.py`** - Windows API integration
- **`kill_switch.py`** - F12 emergency stop
- **`global_hotkey.py`** - Alt+G hotkey system
- **`app_handlers.py`** - App-specific logic

#### 3. UI (User Interface) - `ui/`

- **`overlay.py`** (335 lines) - Transparent cursor overlay
- **`reticle.py`** - Animated cursor indicator
- **`input_dialog.py`** (505 lines) - Task input interface
- **`answer_overlay.py`** - Context help display
- **`tray.py`** - System tray icon

### Data Flow

```
User Input (Alt+G or Dialog)
         ↓
Task Queue (thread-safe)
         ↓
Agent Loop (background thread)
         ↓
┌────────────────────────────────────┐
│  1. Capture Screen (mss)           │
│  2. Extract Text (EasyOCR)         │
│  3. Analyze with LLM               │
│  4. Broadcast to UI Queue          │
│  5. Execute Action (PyAutoGUI)     │
│  6. Wait for Screen Update         │
│  7. Check if Done/Error/Kill       │
│  8. Repeat or Complete             │
└────────────────────────────────────┘
         ↓
Status Updates → UI Components
         ↓
Visual Feedback (Overlay, Tray)
```

### Technology Choices & Rationale

| Technology | Why Chosen | Alternatives |
|-----------|-----------|--------------|
| **PyQt6** | Cross-platform, transparent overlays | Tkinter, wxPython |
| **mss** | Fastest screen capture (<5ms) | PIL, pyautogui |
| **EasyOCR** | GPU-accelerated, accurate | Tesseract, PaddleOCR |
| **PyAutoGUI** | Simple API, cross-platform | pywinauto, keyboard |
| **pynput** | Global hotkeys, reliable | keyboard, win32api |
| **Gemini/Claude** | Vision capabilities | GPT-4V, local models |

For detailed architecture diagrams and execution traces, see [ARCHITECTURE.md](ARCHITECTURE.md).

---

## 🚀 Features & Capabilities

### Complete Feature List

#### Core Automation (6 Action Types)

1. **Mouse Control** - Click, right-click, double-click, drag, scroll
2. **Keyboard Control** - Type text, hotkeys, special keys
3. **Application Control** - Open apps, switch windows, close apps
4. **Document Automation** - Print, open, save, copy/paste
5. **Screen Analysis** - OCR text extraction, UI element detection
6. **Multi-Step Workflows** - Complex task execution

#### Advanced Features

**Global Hotkey System (Alt+G)**
- **Task Dialog Mode** - Quick task submission from anywhere
- **Context Help Mode** - AI explanations for selected text
- Works system-wide across all applications

**Multi-LLM Provider Support**
- 5 providers: Gemini, Claude, OpenRouter, NVIDIA, Ollama
- Easy switching with `python switch_llm.py <provider>`
- Model selection in UI dropdown

**Print Document Integration**
- Natural language: "Print KheloParty_Full_Plan"
- Automatic document opening and printing
- Extensible to other document types

**Safety Features**
- F12 Kill Switch - Emergency stop
- Stuck-Loop Detection - Auto-recovery
- Transparent Overlay - Always see desktop
- Action Logging - Complete audit trail

**OCR Text Grounding**
- Extracts text from screenshots
- Provides precise click coordinates
- GPU-accelerated processing
- 2-second caching for performance

### Recent Additions

- ✅ Alt+G Global Hotkey (May 2026)
- ✅ Context-Aware Help (May 2026)
- ✅ Print Document Integration (May 2026)
- ✅ Ollama Local Support (May 2026)
- ✅ NVIDIA Models Integration (May 2026)
- ✅ Dialog Lock Mechanism (May 2026)

---

## 🛠️ Setup & Installation

### Prerequisites

- Windows 10/11 (64-bit)
- Python 3.8+
- 8GB RAM (16GB for Ollama)
- GPU optional (recommended for OCR)
- Internet for cloud LLMs

### Quick Start

```bash
# 1. Navigate to project
cd ibm-bob-hackathon/axon

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure API key (create .env file)
echo "LLM_PROVIDER=gemini" > .env
echo "GEMINI_API_KEY=your_key_here" >> .env

# 4. Run AXON
python main.py
```

### Get API Keys

- **Gemini:** https://aistudio.google.com/app/apikey (Free tier)
- **Claude:** https://console.anthropic.com/ (Paid)
- **OpenRouter:** https://openrouter.ai/keys (Free tier)
- **NVIDIA:** https://build.nvidia.com/ (Free tier)
- **Ollama:** No API key needed (local)

### Configuration

Edit `.env` file:

```env
# Choose provider
LLM_PROVIDER=gemini

# Add your API keys
GEMINI_API_KEY=your_key_here
CLAUDE_API_KEY=your_key_here
OPENROUTER_API_KEY=your_key_here
NVIDIA_API_KEY=your_key_here

# Ollama (local)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2-vision:11b
```

### First-Time Setup

```bash
# Test API connection
python test_gemini.py

# Test components
python test_actions.py
python test_kill_switch.py
python test_global_hotkey.py

# Check configuration
python switch_llm.py status
```

---

## 📖 Usage Guide

### Starting AXON

```bash
python main.py
```

**What happens:**
1. System tray icon appears
2. Global hotkey (Alt+G) activates
3. Kill switch (F12) ready
4. Background monitoring starts
5. Ready for tasks!

### Keyboard Shortcuts

| Shortcut | Action | Context |
|----------|--------|---------|
| **Alt+G** | Open task dialog | No text selected |
| **Alt+G** | Get context help | Text selected |
| **F12** | Emergency stop | During execution |
| **Esc** | Close overlay | Answer visible |

### Using Features

**Submit Task:**
1. Press Alt+G
2. Type task (e.g., "Open Chrome")
3. Press Enter

**Get Context Help:**
1. Select text anywhere
2. Press Alt+G
3. Read AI explanation
4. Press Esc to close

**Emergency Stop:**
- Press F12 anytime

**Switch LLM:**
```bash
python switch_llm.py gemini
python switch_llm.py ollama
```

### Example Tasks

```
"Open Notepad"
"Click the Start button"
"Type 'Hello World'"
"Open Chrome and search for Python"
"Print KheloParty_Full_Plan"
```

---

## 🤖 LLM Integration

### Supported Providers (5)

| Provider | Models | Speed | Cost | Best For |
|----------|--------|-------|------|----------|
| **Gemini** | Flash, Pro | ⚡⚡⚡⚡ | $ | Development |
| **Claude** | Sonnet, Haiku, Opus | ⚡⚡⚡ | $$$ | Production |
| **OpenRouter** | Multiple | ⚡⚡⚡ | $-$$ | Flexibility |
| **NVIDIA** | Llama, Gemma | ⚡⚡⚡⚡ | Free | Testing |
| **Ollama** | Local models | ⚡⚡⚡ | Free | Privacy |

### How to Switch

```bash
# Using switch script
python switch_llm.py gemini
python switch_llm.py claude
python switch_llm.py ollama

# Check current
python switch_llm.py status
```

### Configuration

Each provider has specific settings in `.env`:

```env
# Gemini
GEMINI_API_KEY=your_key

# Claude
CLAUDE_API_KEY=your_key
CLAUDE_MODEL=claude-3-5-sonnet-20241022

# OpenRouter
OPENROUTER_API_KEY=your_key
OPENROUTER_MODEL=anthropic/claude-3.5-haiku

# NVIDIA
NVIDIA_API_KEY=your_key
NVIDIA_MODEL=meta/llama-3.2-90b-vision-instruct

# Ollama (local)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2-vision:11b
```

### Cost Considerations

- **Gemini Flash:** $0.075 per 1M tokens (free tier available)
- **Claude:** $0.80-$15 per 1M tokens (no free tier)
- **OpenRouter:** Varies by model (free tier available)
- **NVIDIA:** Free tier available
- **Ollama:** $0 (100% free, local)

**Recommendation:** Start with Ollama or NVIDIA (free), upgrade to Claude for production.

---

## 💻 Development & Customization

### Project Structure

```
axon/
├── core/           # Vision & Brain
├── executor/       # Action & Safety
├── ui/             # User Interface
├── main.py         # Entry point
├── config.py       # Configuration
├── .env            # API keys
└── bob-reports/    # IBM Bob sessions
```

### Adding New Actions

1. **Define handler** in `executor/actions.py`
2. **Add to router** in `execute_action()`
3. **Update LLM prompt** in `core/llm.py`
4. **Test** with test script

Example:
```python
def _my_action(param):
    # Your logic here
    return True  # Success
```

### Extending Functionality

- Add new LLM providers in `core/llm.py`
- Create UI widgets in `ui/`
- Add app handlers in `executor/app_handlers.py`
- Customize prompts in `core/llm.py`

### Code Organization

- **Modular design** - Separate concerns
- **Thread-safe** - Queues for communication
- **Extensible** - Easy to add features
- **Well-documented** - Comprehensive comments

---

## 🧪 Testing & Validation

### Test Scripts

```bash
# Core tests
python test_gemini.py
python test_ollama.py
python test_nvidia_api.py

# Component tests
python test_actions.py
python test_kill_switch.py
python test_global_hotkey.py

# Integration tests
python test_full_flow.py
python test_print_integration.py
```

### Manual Testing

1. **Simple task:** "Open Notepad"
2. **Multi-step:** "Open Chrome and search"
3. **Context help:** Select text, press Alt+G
4. **Emergency stop:** Press F12 during task

### Performance Targets

- Screen capture: <5ms
- OCR extraction: <500ms
- LLM response: 1-5 seconds
- Action execution: <100ms

---

## ⚠️ Known Limitations & Future Enhancements

### Current Limitations

1. **Windows Only** - macOS/Linux support planned
2. **Single Monitor** - Multi-monitor support planned
3. **English Language** - Multi-language possible
4. **Some Apps Block Automation** - Security features
5. **Print Document** - Currently one specific document

### Planned Improvements

**Short-Term:**
- Enhanced print support (PDF, Excel, PowerPoint)
- Better error handling
- Performance optimization
- UI enhancements

**Medium-Term:**
- Multi-monitor support
- Macro recording
- Task templates
- Advanced scheduling

**Long-Term:**
- Cross-platform support
- Plugin system
- Cloud sync
- Mobile companion app
- Enterprise features

---

## 🔧 Troubleshooting

### Common Issues

**"API_KEY not found"**
- Check `.env` file exists
- Verify API key is correct
- Restart application

**Black Screen**
- Press F12 to stop
- Restart AXON
- Update to latest version

**Alt+G Not Working**
- Check AXON is running
- Verify no conflicts
- Restart application

**Slow Performance**
- Switch to faster model
- Enable GPU for OCR
- Use local Ollama

**Actions Not Executing**
- Check action logs
- Verify coordinates
- Test with simple task

### Debug Procedures

1. Check console output
2. Review session_log.json
3. Run test scripts
4. Enable DEBUG_MODE
5. Check debug screenshots

---

## 🎯 IBM Hackathon Context

### How This Fits the Theme

**Innovation in AI-Powered Automation:**
- Combines vision AI with desktop automation
- Natural language interface for accessibility
- Multi-provider flexibility for different needs
- Real-world practical applications

### Innovation Highlights

1. **Live Vision Loop** - Continuous screen analysis, not one-shot
2. **Multi-LLM Architecture** - Flexible provider switching
3. **Context-Aware Help** - Built-in AI assistant
4. **Safety-First Design** - Kill switch, loop detection
5. **Production Ready** - Comprehensive error handling

### Business Value

**For Individuals:**
- Save hours on repetitive tasks
- Learn faster with context help
- Accessible computer control

**For Enterprises:**
- Automate workflows without coding
- Reduce training time
- Improve productivity
- Scalable automation platform

### Scalability Potential

**Technical Scalability:**
- Cloud deployment ready
- Multi-user support possible
- API for integration
- Plugin architecture

**Business Scalability:**
- SaaS model potential
- Enterprise licensing
- Marketplace for macros
- Training and support services

### Metrics & Achievements

- **Lines of Code:** ~3,500+ (excluding tests)
- **Test Coverage:** 15+ test scripts
- **Documentation:** 12+ comprehensive guides
- **Features:** 20+ major features
- **LLM Providers:** 5 supported
- **Development Time:** 24-hour sprint
- **Team Size:** 3 developers
- **Built with:** IBM Bob AI Assistant

### Demo Scenarios

**Scenario 1: Quick Automation**
```
User: "Open Notepad and type 'Meeting Notes'"
Result: Task completed in 5 seconds
```

**Scenario 2: Learning Assistant**
```
User: Selects error message, presses Alt+G
Result: Instant AI explanation with solution
```

**Scenario 3: Document Workflow**
```
User: "Print KheloParty_Full_Plan"
Result: Document opens and prints automatically
```

---

## 📚 Documentation Reference

### Complete Documentation Set

1. **README.md** - Project overview and quick start
2. **ARCHITECTURE.md** - Detailed technical architecture
3. **HOW_TO_RUN.md** - Setup and usage instructions
4. **LLM_SETUP_GUIDE.md** - Multi-provider configuration
5. **GLOBAL_HOTKEY_GUIDE.md** - Alt+G feature guide
6. **CONTEXT_HELP_GUIDE.md** - Context help usage
7. **PRINT_DOCUMENT_INTEGRATION.md** - Print feature guide
8. **OLLAMA_QUICK_START.md** - Local AI setup
9. **FREE_LLM_OPTIONS.md** - Free provider options
10. **PROJECT_STATUS.md** - Current status and roadmap
11. **FLOW_DIAGRAMS.md** - Visual workflow diagrams
12. **QUICK_REFERENCE.md** - Developer quick reference

### Key Files

- **main.py** - Application entry point
- **config.py** - Configuration and shared state
- **.env** - API keys and settings
- **requirements.txt** - Python dependencies
- **session_log.json** - Action audit trail

---

## 👥 Team & Development

### Team Structure

- **Dev 1 (Joshua)** - Vision & Brain (`core/`)
- **Dev 2 (Ashish)** - Executor & Safety (`executor/`)
- **Dev 3 (Pratham)** - UI & Demo (`ui/`)

### Built with IBM Bob

**Every line of code was written with IBM Bob AI assistant:**
- Used Bob for architecture design
- Bob helped implement all features
- Bob assisted with debugging
- Bob generated documentation
- Session reports in `/bob-reports/`

### Development Approach

1. **Modular Design** - Clear separation of concerns
2. **Test-Driven** - Comprehensive test coverage
3. **Documentation-First** - Extensive guides
4. **Safety-Focused** - Multiple safety layers
5. **User-Centric** - Intuitive interface

---

## 🎉 Conclusion

AXON represents a significant advancement in desktop automation, combining cutting-edge AI vision models with practical automation capabilities. The project demonstrates:

✅ **Technical Excellence** - Robust architecture, comprehensive features  
✅ **Innovation** - Unique live vision loop, multi-LLM support  
✅ **Practical Value** - Real-world applications, immediate usability  
✅ **Production Ready** - Safety features, error handling, documentation  
✅ **Scalability** - Extensible design, enterprise potential  

### Next Steps

1. **Try AXON:** `python main.py`
2. **Read Documentation:** Start with README.md
3. **Run Tests:** Validate your setup
4. **Explore Features:** Try Alt+G and context help
5. **Customize:** Add your own actions and integrations

### Contact & Support

- **Repository:** [GitHub Link]
- **Documentation:** See `/axon/` directory
- **Issues:** Report via GitHub Issues
- **Questions:** Check documentation first

---

**Made with IBM Bob** 🤖  
**IBM Hackathon 2026**  
**AXON - Live AI Desktop Agent**

*Empowering users to automate anything, anywhere, with just their voice or keyboard.*