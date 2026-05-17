# AXON Browser Automation - Complete Setup & Run Guide

## 🚀 Quick Start (5 Minutes)

This guide will get you up and running with AXON's browser automation in 5 minutes.

---

## ✅ Prerequisites

Before starting, make sure you have:
- ✅ Python 3.8 or higher installed
- ✅ pip (Python package manager)
- ✅ Windows 10/11 (for this setup)
- ✅ Internet connection

---

## 📦 Step 1: Install Dependencies (2 minutes)

### Option A: Install All AXON Dependencies
```bash
# Navigate to the axon directory
cd e:/ibm-bob-hackathon/axon

# Install all dependencies
pip install -r requirements.txt
```

### Option B: Install Only Browser Automation
```bash
# If you only want browser automation
pip install playwright
```

**Expected Output:**
```
Successfully installed playwright-1.59.0 greenlet-3.5.0 pyee-13.0.1
```

---

## 🌐 Step 2: Install Browser (1 minute)

After installing Playwright, you need to install the Chromium browser:

```bash
# Install Chromium browser
playwright install chromium
```

**Expected Output:**
```
Downloading Chromium 147.0.7727.15 (playwright chromium v1217)
Chrome for Testing 147.0.7727.15 downloaded to C:\Users\...\ms-playwright\chromium-1217
```

**Note:** This downloads ~180MB, so it may take a minute depending on your internet speed.

---

## 🧪 Step 3: Test the Installation (1 minute)

### Test 1: Standalone Script

Run the standalone GitHub search automation:

```bash
# From the project root directory
python axon/github_search_automation.py
```

**What You'll See:**
1. Browser window opens (visible)
2. Navigates to GitHub
3. Searches for "React"
4. Sorts by most stars
5. Takes a screenshot
6. Closes after 5 seconds

**Expected Output:**
```
============================================================
GitHub Search Automation - AXON Project
============================================================

[*] Launching Chrome browser...
[*] Navigating to GitHub...
[OK] GitHub homepage loaded
[*] Searching for 'React'...
[OK] Search results loaded
[*] Sorting by most stars...
[OK] Results sorted by most stars
[*] Keeping browser open for 5 seconds...

[SUCCESS] Automation completed successfully!
[*] Closing browser...
```

**Screenshot Location:** `axon/bob-reports/github_search_results.png`

---

### Test 2: Integration Test

Test browser actions with AXON's action system:

```bash
# From the project root directory
python axon/test_browser_integration.py
```

**What You'll See:**
1. Browser opens
2. Navigates to GitHub
3. Types "React" character by character
4. Submits search
5. Takes screenshot
6. Closes browser

**Expected Output:**
```
============================================================
AXON Browser Automation Test - GitHub Search
============================================================

[1/5] Navigating to GitHub...
[OK] GitHub loaded

[2/5] Opening search (pressing '/')...
[OK] Search opened

[3/5] Typing 'React'...
[OK] Typed 'React'

[4/5] Submitting search (pressing Enter)...
[OK] Search submitted

[5/5] Taking screenshot...
[OK] Screenshot saved to: axon/bob-reports/github_search_results.png

[SUCCESS] Browser automation test completed!
```

---

## 🎯 Step 4: Use with AXON's AI (Optional)

To use browser automation with AXON's full AI system:

### 4.1: Update AI System Prompt

Add the browser action specifications from `AI_PROMPT_BROWSER_ACTIONS.md` to your AI's system prompt.

**Key sections to add:**
- Browser action definitions
- Usage guidelines
- Example workflows

### 4.2: Run AXON Main Loop

```bash
# Start AXON with browser automation enabled
python axon/main.py
```

### 4.3: Give Commands

Once AXON is running, you can give natural language commands:

**Examples:**
```
You: "Search GitHub for React"
You: "Go to Python.org and take a screenshot"
You: "Search Google for Python tutorials"
```

AXON will automatically generate and execute the appropriate browser actions!

---

## 📝 Common Commands Reference

### Standalone Scripts

```bash
# Run standalone GitHub search
python axon/github_search_automation.py

# Run integration test
python axon/test_browser_integration.py

# Run execute_action test (requires pyautogui)
python axon/test_execute_action_browser.py
```

### With Full AXON System

```bash
# Start AXON
python axon/main.py

# Then give voice or text commands like:
# "Search GitHub for Python"
# "Go to Wikipedia and search for AI"
# "Check the weather on weather.com"
```

---

## 🔧 Troubleshooting

### Issue 1: "playwright: command not found"

**Solution:**
```bash
# Make sure playwright is installed
pip install playwright

# Then install browsers
playwright install chromium
```

---

### Issue 2: "ModuleNotFoundError: No module named 'playwright'"

**Solution:**
```bash
# Install playwright
pip install playwright>=1.40.0
```

---

### Issue 3: Browser doesn't open

**Solution:**
```bash
# Reinstall browser binaries
playwright install chromium --force
```

---

### Issue 4: "Timeout waiting for selector"

**Cause:** Website structure changed or slow internet

**Solution:**
- Increase timeout in action dictionary: `"timeout": 30000`
- Check your internet connection
- Verify the CSS selector is correct

---

### Issue 5: Screenshot not saved

**Solution:**
```bash
# Make sure the directory exists
mkdir -p axon/bob-reports

# Or on Windows:
md axon\bob-reports
```

---

## 📂 File Structure

After setup, your structure should look like:

```
axon/
├── github_search_automation.py          # Standalone script
├── test_browser_integration.py          # Integration test
├── test_execute_action_browser.py       # Action system test
├── BROWSER_AUTOMATION_QUICKSTART.md     # This file
├── BROWSER_AUTOMATION_README.md         # Technical docs
├── BROWSER_AUTOMATION_DEMOS.md          # Demo scenarios
├── AI_PROMPT_BROWSER_ACTIONS.md         # AI prompt specs
├── executor/
│   ├── browser_actions.py               # Browser module
│   └── actions.py                       # Updated with browser handlers
├── bob-reports/
│   └── github_search_results.png        # Screenshots saved here
└── requirements.txt                     # Updated with playwright
```

---

## 🎓 Learning Path

### Beginner (Day 1)
1. ✅ Install dependencies
2. ✅ Run standalone script
3. ✅ View screenshot results
4. ✅ Read BROWSER_AUTOMATION_DEMOS.md

### Intermediate (Day 2)
1. ✅ Run integration tests
2. ✅ Modify demo scripts
3. ✅ Try different websites
4. ✅ Create custom workflows

### Advanced (Day 3+)
1. ✅ Integrate with AXON's AI
2. ✅ Add custom browser actions
3. ✅ Create complex multi-step tasks
4. ✅ Build automation workflows

---

## 💡 Quick Examples

### Example 1: Simple Screenshot
```bash
python -c "
from executor.browser_actions import browser_navigate, browser_screenshot, browser_close
browser_navigate('https://github.com')
browser_screenshot('axon/bob-reports/github.png')
browser_close()
"
```

### Example 2: Search and Capture
```bash
python -c "
from executor.browser_actions import *
browser_navigate('https://www.google.com')
browser_type('input[name=\"q\"]', 'Python')
browser_press_key('Enter')
browser_screenshot('axon/bob-reports/google_search.png')
browser_close()
"
```

### Example 3: Using Action Dictionaries
```python
from executor.actions import execute_action

# Navigate
execute_action({"action": "browser_navigate", "url": "https://github.com"})

# Search
execute_action({"action": "browser_press_key", "key": "/"})
execute_action({"action": "browser_press_key", "key": "R"})
execute_action({"action": "browser_press_key", "key": "e"})
execute_action({"action": "browser_press_key", "key": "a"})
execute_action({"action": "browser_press_key", "key": "c"})
execute_action({"action": "browser_press_key", "key": "t"})
execute_action({"action": "browser_press_key", "key": "Enter"})

# Screenshot
execute_action({"action": "browser_screenshot", "path": "axon/bob-reports/test.png"})

# Close
execute_action({"action": "browser_close"})
```

---

## 🎯 Verification Checklist

After setup, verify everything works:

- [ ] Playwright installed (`pip list | grep playwright`)
- [ ] Chromium browser installed (`playwright install chromium`)
- [ ] Standalone script runs successfully
- [ ] Integration test passes
- [ ] Screenshots are saved in `bob-reports/`
- [ ] Browser opens and closes properly
- [ ] No error messages in console

---

## 📊 Performance Tips

### Speed Up Execution
```python
# In browser_actions.py, reduce slow_mo:
slow_mo=100  # Instead of 300
```

### Run Headless (Faster)
```python
# In browser_actions.py:
headless=True  # Instead of False
```

### Increase Timeouts for Slow Sites
```json
{"action": "browser_wait", "selector": ".content", "timeout": 30000}
```

---

## 🔐 Security Notes

### What's Safe:
✅ Navigating to public websites
✅ Searching public information
✅ Taking screenshots
✅ Filling public forms

### What to Avoid:
❌ Entering passwords or credentials
❌ Accessing private accounts
❌ Sharing sensitive information
❌ Automated login attempts

**Note:** Browser automation is for public information gathering and testing only.

---

## 📞 Getting Help

### Check Documentation:
1. `BROWSER_AUTOMATION_README.md` - Technical details
2. `BROWSER_AUTOMATION_DEMOS.md` - 21+ examples
3. `AI_PROMPT_BROWSER_ACTIONS.md` - AI integration

### Common Resources:
- Playwright Docs: https://playwright.dev/python/
- CSS Selectors: https://www.w3schools.com/cssref/css_selectors.php
- AXON Project: Check main README.md

---

## 🎉 Success Indicators

You'll know it's working when:
1. ✅ Browser window opens automatically
2. ✅ You see actions happening in real-time
3. ✅ Screenshots appear in `bob-reports/`
4. ✅ Console shows success messages
5. ✅ Browser closes automatically

---

## 🚀 Next Steps

After successful setup:

1. **Try Demo Scenarios**
   - Open `BROWSER_AUTOMATION_DEMOS.md`
   - Pick a demo that interests you
   - Run it and see the results

2. **Integrate with AXON**
   - Update AI system prompt
   - Start AXON main loop
   - Give natural language commands

3. **Create Custom Workflows**
   - Combine multiple actions
   - Build automation sequences
   - Save as reusable scripts

4. **Explore Advanced Features**
   - Multi-step workflows
   - Data extraction
   - Form automation
   - Web scraping

---

## ⏱️ Time Estimates

| Task | Time Required |
|------|---------------|
| Install dependencies | 2 minutes |
| Install browser | 1 minute |
| Run first test | 30 seconds |
| Read documentation | 10 minutes |
| Try demo scenarios | 15 minutes |
| Integrate with AXON | 5 minutes |
| **Total Setup Time** | **~20 minutes** |

---

## 📈 What You Can Do Now

After completing this guide, you can:

✅ Run automated browser tasks
✅ Search any website automatically
✅ Fill forms programmatically
✅ Capture screenshots
✅ Extract web data
✅ Build custom workflows
✅ Integrate with AXON's AI
✅ Create automation scripts

---

## 🎓 Summary

**You've successfully set up AXON's browser automation!**

**Quick Commands:**
```bash
# Test standalone
python axon/github_search_automation.py

# Test integration
python axon/test_browser_integration.py

# Run AXON with browser automation
python axon/main.py
```

**Next:** Try the demos in `BROWSER_AUTOMATION_DEMOS.md`!

---

**Last Updated:** 2026-05-17  
**Status:** ✅ Production Ready  
**Setup Time:** ~20 minutes  
**Difficulty:** Beginner-Friendly