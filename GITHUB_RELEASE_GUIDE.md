# 📦 GitHub Release Guide - Upload AXON.exe

## 🎯 Quick Steps to Create Release

### Step 1: Wait for Build to Complete
The EXE file will be located at:
```
c:/ibm/ibm-bob-hackathon/dist/AXON.exe
```

### Step 2: Go to GitHub Releases
1. Visit: https://github.com/pratham092006/ibm-bob-hackathon/releases
2. Click **"Create a new release"** button

### Step 3: Create Release Tag
- **Tag version:** `v1.0.0`
- **Release title:** `AXON v1.0.0 - Initial Release`
- **Target:** `main` branch

### Step 4: Write Release Notes
Copy and paste this template:

```markdown
# 🤖 AXON v1.0.0 - AI Desktop Agent

## 🎉 First Official Release!

AXON is a revolutionary AI desktop agent that sees your screen, understands your goals, and automates tasks autonomously. Built with IBM Bob AI Assistant for the IBM Bob Hackathon 2026.

### ✨ Features

- 🎯 **Vision-Based Automation** - Sees and understands your screen
- 🧠 **Multi-LLM Support** - Works with Gemini, Claude, Ollama, NVIDIA NIM
- 🛡️ **F12 Kill Switch** - Emergency stop anytime
- ⚡ **Real-time Feedback** - Transparent overlay shows AI actions
- 🌐 **Browser Automation** - Integrated Selenium support
- ⌨️ **Global Hotkey (Alt+G)** - Quick access from anywhere

### 📥 Download

**Windows 10/11 (64-bit)**
- Download `AXON.exe` below
- No installation required
- ~100-150 MB

### 🚀 Quick Start

1. Download `AXON.exe`
2. Double-click to run
3. Press `Alt+G` to open task dialog
4. Enter your task in natural language
5. Press `F12` for emergency stop

### ⚙️ Configuration

Create a `.env` file with your API keys:
```
LLM_PROVIDER=gemini
GEMINI_API_KEY=your-key-here
```

See [LLM_SETUP_GUIDE.md](https://github.com/pratham092006/ibm-bob-hackathon/blob/main/LLM_SETUP_GUIDE.md) for details.

### 📚 Documentation

- [README.md](https://github.com/pratham092006/ibm-bob-hackathon/blob/main/README.md) - Complete overview
- [HOW_TO_RUN.md](https://github.com/pratham092006/ibm-bob-hackathon/blob/main/HOW_TO_RUN.md) - Setup guide
- [ARCHITECTURE.md](https://github.com/pratham092006/ibm-bob-hackathon/blob/main/ARCHITECTURE.md) - Technical details

### 🐛 Known Issues

- First launch may take 10-15 seconds
- Requires Windows 10/11 64-bit
- Antivirus may flag (false positive)

### 🏆 Built For

IBM Bob Hackathon 2026 - AI Desktop Category

### 👥 Team

Team Merge Conflicts
- Joshua (Vision & Brain)
- Ashish (Executor & Safety)
- Pratham (UI & Integration)

### 📝 License

MIT License - See [LICENSE](https://github.com/pratham092006/ibm-bob-hackathon/blob/main/LICENSE)

---

**Made with Bob** 🤖 | **Team Merge Conflicts** 🏆
```

### Step 5: Upload AXON.exe
1. Scroll to **"Attach binaries"** section
2. Drag and drop `dist/AXON.exe` OR click to browse
3. Wait for upload to complete (~100-150 MB)

### Step 6: Publish Release
1. Check **"Set as the latest release"**
2. Click **"Publish release"**
3. Done! 🎉

## 📊 After Publishing

### Your Release URL
```
https://github.com/pratham092006/ibm-bob-hackathon/releases/tag/v1.0.0
```

### Direct Download Link
```
https://github.com/pratham092006/ibm-bob-hackathon/releases/download/v1.0.0/AXON.exe
```

### Update Landing Page
Update the download link in `landing-page/index.html`:
```html
<a href="https://github.com/pratham092006/ibm-bob-hackathon/releases/download/v1.0.0/AXON.exe" 
   class="btn-download">
    ⬇️ Download AXON.exe
</a>
```

## 🔒 Security Note

### Antivirus False Positives
Some antivirus software may flag the EXE as suspicious because:
- It's a PyInstaller-bundled application
- It uses keyboard/mouse automation
- It captures screenshots

**This is a false positive.** The source code is open and available for review.

### To Whitelist in Windows Defender
1. Open Windows Security
2. Go to Virus & threat protection
3. Click "Manage settings"
4. Add exclusion for AXON.exe

## 📈 Release Checklist

Before publishing, ensure:
- [ ] EXE file builds successfully
- [ ] File size is reasonable (~100-150 MB)
- [ ] Tested on clean Windows machine
- [ ] All documentation is up to date
- [ ] README has correct download link
- [ ] Landing page updated with download link

## 🎯 Next Steps

After release:
1. ✅ Share release link on social media
2. ✅ Update README with download badge
3. ✅ Add to hackathon submission
4. ✅ Monitor for issues/feedback

## 📝 Version Numbering

- **v1.0.0** - Initial release
- **v1.0.1** - Bug fixes
- **v1.1.0** - New features
- **v2.0.0** - Major changes

---

**Made with Bob** 🤖 | **Team Merge Conflicts** 🏆