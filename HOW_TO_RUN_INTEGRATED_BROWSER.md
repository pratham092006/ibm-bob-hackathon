# How to Run AXON with Integrated Browser Automation

## 🎯 Overview

This guide shows you how to run AXON's **full AI system** with browser automation integrated. The AI will be able to control web browsers through natural language commands.

---

## 🚀 Quick Start - Integrated Version

### Prerequisites
✅ Playwright installed  
✅ Chromium browser installed  
✅ AXON dependencies installed  

If not done yet:
```bash
pip install -r axon/requirements.txt
playwright install chromium
```

---

## 📋 Method 1: Run with Full AXON AI Loop

### Step 1: Start AXON
```bash
cd e:/ibm-bob-hackathon
python axon/main.py
```

### Step 2: Give Browser Commands

Once AXON is running, you can give natural language commands:

**Example Commands:**
```
"Search GitHub for React"
"Go to Python.org and take a screenshot"
"Search Google for Python tutorials"
"Check the weather on weather.com"
```

### What Happens:
1. AXON's AI receives your command
2. AI generates browser action dictionaries
3. `execute_action()` routes to browser handlers
4. Browser automation executes
5. Results are captured

---

## 📋 Method 2: Test Integration Directly

### Option A: Test Browser Actions via execute_action()

Create a test file `test_my_browser.py`:

```python
import sys
sys.path.insert(0, 'axon')

from executor.actions import execute_action
import time

# Test sequence
actions = [
    {"action": "browser_navigate", "url": "https://github.com"},
    {"action": "browser_press_key", "key": "/"},
    {"action": "browser_press_key", "key": "P"},
    {"action": "browser_press_key", "key": "y"},
    {"action": "browser_press_key", "key": "t"},
    {"action": "browser_press_key", "key": "h"},
    {"action": "browser_press_key", "key": "o"},
    {"action": "browser_press_key", "key": "n"},
    {"action": "browser_press_key", "key": "Enter"},
    {"action": "browser_screenshot", "path": "axon/bob-reports/my_test.png"},
    {"action": "browser_close"}
]

print("Testing integrated browser automation...")
for i, action in enumerate(actions, 1):
    print(f"[{i}/{len(actions)}] {action['action']}")
    result = execute_action(action)
    print(f"  Result: {'✅ Success' if result else '❌ Failed'}")
    time.sleep(0.5)

print("\nDone! Check axon/bob-reports/my_test.png")
```

Run it:
```bash
python test_my_browser.py
```

---

### Option B: Use Existing Integration Test

```bash
python axon/test_browser_integration.py
```

This runs a pre-built test that:
- Opens GitHub
- Searches for "React"
- Takes screenshot
- Closes browser

---

## 📋 Method 3: Interactive Python Session

### Step 1: Start Python
```bash
cd e:/ibm-bob-hackathon
python
```

### Step 2: Import and Use
```python
import sys
sys.path.insert(0, 'axon')

from executor.actions import execute_action

# Navigate to a website
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

## 🎯 Method 4: Create Custom Automation Script

Create `my_automation.py`:

```python
"""My custom browser automation using AXON's integrated system."""

import sys
sys.path.insert(0, 'axon')

from executor.actions import execute_action
import time

def search_github(query):
    """Search GitHub for a query."""
    print(f"Searching GitHub for: {query}")
    
    actions = [
        {"action": "browser_navigate", "url": "https://github.com"},
        {"action": "browser_press_key", "key": "/"},
    ]
    
    # Type each character
    for char in query:
        actions.append({"action": "browser_press_key", "key": char})
    
    actions.extend([
        {"action": "browser_press_key", "key": "Enter"},
        {"action": "browser_screenshot", "path": f"axon/bob-reports/{query}_search.png"},
        {"action": "browser_close"}
    ])
    
    # Execute all actions
    for action in actions:
        execute_action(action)
        time.sleep(0.3)
    
    print(f"✅ Done! Screenshot saved to axon/bob-reports/{query}_search.png")

# Run it
if __name__ == "__main__":
    search_github("Python")
```

Run it:
```bash
python my_automation.py
```

---

## 🔧 Integration Architecture

### How It Works:

```
User Command
    ↓
AXON AI (main.py)
    ↓
Generates Action Dictionary
    ↓
execute_action() in actions.py
    ↓
Routes to browser_* functions
    ↓
browser_actions.py executes
    ↓
Playwright controls browser
    ↓
Result returned to AI
```

### Example Flow:

**User says:** "Search GitHub for React"

**AI generates:**
```json
{"action": "browser_navigate", "url": "https://github.com"}
{"action": "browser_press_key", "key": "/"}
{"action": "browser_press_key", "key": "R"}
...
{"action": "browser_close"}
```

**System executes:**
1. `execute_action()` receives each dictionary
2. Routes to `browser_navigate()`, `browser_press_key()`, etc.
3. Browser automation happens
4. Results logged and returned

---

## 📊 Verification Steps

### 1. Check Integration is Loaded

```python
import sys
sys.path.insert(0, 'axon')

from executor import actions

# Check if browser actions are available
print(f"Browser actions available: {actions.BROWSER_ACTIONS_AVAILABLE}")
```

**Expected Output:** `Browser actions available: True`

---

### 2. Test Single Action

```python
from executor.actions import execute_action

result = execute_action({
    "action": "browser_navigate",
    "url": "https://github.com"
})

print(f"Navigation result: {result}")
```

**Expected Output:** `Navigation result: True`

---

### 3. Check Screenshot Creation

```python
from executor.actions import execute_action

execute_action({"action": "browser_navigate", "url": "https://github.com"})
execute_action({"action": "browser_screenshot", "path": "axon/bob-reports/verify.png"})
execute_action({"action": "browser_close"})

# Check if file exists
import os
exists = os.path.exists("axon/bob-reports/verify.png")
print(f"Screenshot created: {exists}")
```

**Expected Output:** `Screenshot created: True`

---

## 🎓 Complete Example: Full Integration

Here's a complete example showing AXON's integrated browser automation:

```python
"""
Complete example: AXON integrated browser automation
File: complete_integration_example.py
"""

import sys
import time
sys.path.insert(0, 'axon')

from executor.actions import execute_action

def demo_integrated_browser():
    """Demonstrate AXON's integrated browser automation."""
    
    print("=" * 60)
    print("AXON Integrated Browser Automation Demo")
    print("=" * 60)
    print()
    
    # Define a workflow
    workflow = [
        {
            "step": "Navigate to GitHub",
            "action": {"action": "browser_navigate", "url": "https://github.com"}
        },
        {
            "step": "Open search",
            "action": {"action": "browser_press_key", "key": "/"}
        },
        {
            "step": "Type 'React'",
            "actions": [
                {"action": "browser_press_key", "key": "R"},
                {"action": "browser_press_key", "key": "e"},
                {"action": "browser_press_key", "key": "a"},
                {"action": "browser_press_key", "key": "c"},
                {"action": "browser_press_key", "key": "t"},
            ]
        },
        {
            "step": "Submit search",
            "action": {"action": "browser_press_key", "key": "Enter"}
        },
        {
            "step": "Wait for results",
            "action": {"action": "browser_wait", "selector": ".repo-list", "timeout": 10000}
        },
        {
            "step": "Take screenshot",
            "action": {"action": "browser_screenshot", "path": "axon/bob-reports/integrated_demo.png"}
        },
        {
            "step": "Close browser",
            "action": {"action": "browser_close"}
        }
    ]
    
    # Execute workflow
    for i, step_info in enumerate(workflow, 1):
        step_name = step_info["step"]
        print(f"[{i}/{len(workflow)}] {step_name}...")
        
        # Handle single action or multiple actions
        if "action" in step_info:
            result = execute_action(step_info["action"])
            status = "✅" if result else "❌"
            print(f"  {status} {'Success' if result else 'Failed'}")
        elif "actions" in step_info:
            for action in step_info["actions"]:
                result = execute_action(action)
            print(f"  ✅ Completed")
        
        time.sleep(0.5)
    
    print()
    print("=" * 60)
    print("✅ Demo Complete!")
    print("Screenshot saved: axon/bob-reports/integrated_demo.png")
    print("=" * 60)

if __name__ == "__main__":
    demo_integrated_browser()
```

Save as `complete_integration_example.py` and run:
```bash
python complete_integration_example.py
```

---

## 🔍 Debugging Integration

### Check if Browser Module Loaded

```python
import sys
sys.path.insert(0, 'axon')

try:
    from executor.browser_actions import browser_navigate
    print("✅ Browser module loaded successfully")
except ImportError as e:
    print(f"❌ Browser module not loaded: {e}")
```

---

### Check Action Routing

```python
from executor.actions import execute_action

# This should route to browser_navigate
result = execute_action({
    "action": "browser_navigate",
    "url": "https://example.com"
})

print(f"Action executed: {result}")
```

---

### View Action Logs

Check `axon/session_log.json` for action execution history:

```python
import json

with open('axon/session_log.json', 'r') as f:
    logs = json.load(f)
    
# Show last 5 actions
for log in logs[-5:]:
    print(f"{log['action']}: {log['success']}")
```

---

## 🎯 Common Integration Patterns

### Pattern 1: Search Workflow
```python
def search_workflow(site, query):
    execute_action({"action": "browser_navigate", "url": site})
    execute_action({"action": "browser_type", "selector": "input[name='q']", "text": query})
    execute_action({"action": "browser_press_key", "key": "Enter"})
    execute_action({"action": "browser_screenshot", "path": f"axon/bob-reports/{query}.png"})
    execute_action({"action": "browser_close"})
```

### Pattern 2: Form Filling
```python
def fill_form(url, data):
    execute_action({"action": "browser_navigate", "url": url})
    for selector, value in data.items():
        execute_action({"action": "browser_type", "selector": selector, "text": value})
    execute_action({"action": "browser_click", "selector": "button[type='submit']"})
    execute_action({"action": "browser_close"})
```

### Pattern 3: Multi-Page Navigation
```python
def visit_pages(urls):
    for url in urls:
        execute_action({"action": "browser_navigate", "url": url})
        execute_action({"action": "browser_screenshot", "path": f"axon/bob-reports/{url.split('/')[-1]}.png"})
    execute_action({"action": "browser_close"})
```

---

## 📊 Performance Monitoring

### Track Execution Time

```python
import time

start = time.time()
execute_action({"action": "browser_navigate", "url": "https://github.com"})
end = time.time()

print(f"Navigation took: {end - start:.2f} seconds")
```

### Monitor Success Rate

```python
actions = [...]  # Your actions
successes = sum(1 for action in actions if execute_action(action))
total = len(actions)
print(f"Success rate: {successes}/{total} ({successes/total*100:.1f}%)")
```

---

## 🎉 Summary

### To Run Integrated Version:

**Option 1: With Full AXON AI**
```bash
python axon/main.py
# Then give voice/text commands
```

**Option 2: Direct Integration Test**
```bash
python axon/test_browser_integration.py
```

**Option 3: Custom Script**
```python
from executor.actions import execute_action
execute_action({"action": "browser_navigate", "url": "..."})
```

**Option 4: Interactive Session**
```bash
python
>>> from executor.actions import execute_action
>>> execute_action({...})
```

---

## ✅ Success Indicators

You'll know the integrated version is working when:

1. ✅ `BROWSER_ACTIONS_AVAILABLE = True` in actions.py
2. ✅ Browser actions execute through `execute_action()`
3. ✅ Actions are logged in `session_log.json`
4. ✅ Screenshots appear in `bob-reports/`
5. ✅ No import errors in console
6. ✅ AI can generate and execute browser actions

---

## 🚀 Next Steps

1. **Test the integration** with provided examples
2. **Create custom workflows** for your needs
3. **Integrate with AXON's AI** for voice control
4. **Build automation scripts** for repetitive tasks

---

**Last Updated:** 2026-05-17  
**Status:** ✅ Fully Integrated  
**Difficulty:** Intermediate