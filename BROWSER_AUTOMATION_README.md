# AXON Browser Automation Integration

## Overview

This document describes the integrated browser automation system for AXON using Playwright. The system allows AXON's AI to control web browsers through the existing action framework.

## Architecture

### Components

1. **`executor/browser_actions.py`** - Core browser automation module
   - Singleton `BrowserAutomation` class manages browser lifecycle
   - Async/await Playwright operations
   - Synchronous wrappers for AXON's action system

2. **`github_search_automation.py`** - Standalone example script
   - Demonstrates Playwright capabilities
   - Can run independently for testing

3. **`test_browser_integration.py`** - Integration test
   - Shows how AXON's action system uses browser automation
   - Demonstrates action dictionary format

## Features

### Browser Actions Available

| Action | Function | Description |
|--------|----------|-------------|
| `browser_navigate` | Navigate to URL | Opens a webpage |
| `browser_click` | Click element | Clicks using CSS selector |
| `browser_type` | Type text | Fills input fields |
| `browser_press_key` | Press keyboard key | Simulates key press |
| `browser_wait` | Wait for element | Waits for selector to appear |
| `browser_get_text` | Extract text | Gets text from element |
| `browser_screenshot` | Capture screen | Saves screenshot to file |
| `browser_close` | Close browser | Cleanup and close |

### Key Features

- **Singleton Pattern**: One browser instance shared across actions
- **Visible Browser**: Runs with `headless=False` for debugging
- **Slow Motion**: 300ms delay between actions for visibility
- **Robust Selectors**: Uses CSS selectors (Playwright native)
- **Error Handling**: Try-catch blocks with detailed logging
- **Sync/Async Bridge**: Async Playwright wrapped in sync functions

## Usage

### Standalone Script

```bash
# Run the standalone example
python axon/github_search_automation.py
```

### Integration Test

```bash
# Test browser integration with AXON
python axon/test_browser_integration.py
```

### In AXON's AI Loop

The AI can generate action dictionaries like:

```python
{
    "action": "browser_navigate",
    "url": "https://github.com"
}

{
    "action": "browser_click",
    "selector": "button.search-button"
}

{
    "action": "browser_type",
    "selector": "input[name='q']",
    "text": "React"
}

{
    "action": "browser_press_key",
    "key": "Enter"
}

{
    "action": "browser_screenshot",
    "path": "axon/bob-reports/result.png"
}
```

## Integration with actions.py

To fully integrate browser actions into AXON's action system, add these handlers to `executor/actions.py`:

```python
from executor.browser_actions import (
    browser_navigate,
    browser_click,
    browser_type,
    browser_press_key,
    browser_wait,
    browser_screenshot,
    browser_close
)

# In execute_action() function, add these cases:

elif action_type == "browser_navigate":
    url = action_dict.get('url', '')
    if not url:
        logger.error("No URL specified for browser_navigate")
        success = False
    else:
        success = browser_navigate(url)

elif action_type == "browser_click":
    selector = action_dict.get('selector', '')
    timeout = action_dict.get('timeout', 10000)
    if not selector:
        logger.error("No selector specified for browser_click")
        success = False
    else:
        success = browser_click(selector, timeout)

elif action_type == "browser_type":
    selector = action_dict.get('selector', '')
    text = action_dict.get('text', '')
    timeout = action_dict.get('timeout', 10000)
    if not selector or not text:
        logger.error("Missing selector or text for browser_type")
        success = False
    else:
        success = browser_type(selector, text, timeout)

elif action_type == "browser_press_key":
    key = action_dict.get('key', '')
    if not key:
        logger.error("No key specified for browser_press_key")
        success = False
    else:
        success = browser_press_key(key)

elif action_type == "browser_screenshot":
    path = action_dict.get('path', 'axon/bob-reports/screenshot.png')
    success = browser_screenshot(path)

elif action_type == "browser_close":
    success = browser_close()
```

## AI Prompt Updates

Add to AXON's system prompt:

```
Browser Automation Actions:
- browser_navigate: Navigate to a URL
  Example: {"action": "browser_navigate", "url": "https://example.com"}

- browser_click: Click an element using CSS selector
  Example: {"action": "browser_click", "selector": "button.submit"}

- browser_type: Type text into an input field
  Example: {"action": "browser_type", "selector": "input[name='search']", "text": "query"}

- browser_press_key: Press a keyboard key
  Example: {"action": "browser_press_key", "key": "Enter"}

- browser_screenshot: Capture current page
  Example: {"action": "browser_screenshot", "path": "axon/bob-reports/page.png"}

- browser_close: Close the browser
  Example: {"action": "browser_close"}
```

## Testing Results

### Test Execution Log

```
============================================================
AXON Browser Automation Test - GitHub Search
============================================================

[1/5] Navigating to GitHub...
2026-05-17 13:33:06,767 - INFO - Browser launched successfully
2026-05-17 13:33:09,573 - INFO - Successfully navigated to https://github.com
[OK] GitHub loaded

[2/5] Opening search (pressing '/')...
2026-05-17 13:33:10,944 - INFO - Successfully pressed: /
[OK] Search opened

[3/5] Typing 'React'...
[OK] Typed 'React'

[4/5] Submitting search (pressing Enter)...
2026-05-17 13:33:14,853 - INFO - Successfully pressed: Enter
[OK] Search submitted

[5/5] Taking screenshot...
2026-05-17 13:33:18,055 - INFO - Screenshot saved to: axon/bob-reports/github_search_results.png
[OK] Screenshot saved

[SUCCESS] Browser automation test completed!
```

### Screenshot Evidence

- ✅ Screenshot saved: `axon/bob-reports/github_search_results.png`
- ✅ Shows GitHub search results for "React"
- ✅ Proves end-to-end automation working

## Benefits

1. **Web Automation**: AXON can now interact with web applications
2. **Data Extraction**: Can scrape information from websites
3. **Form Filling**: Automate web form submissions
4. **Testing**: Automated web application testing
5. **Research**: Browse and gather information from the web

## Use Cases

- **Research Tasks**: Search for information online
- **Form Automation**: Fill out web forms automatically
- **Data Collection**: Extract data from websites
- **Web Testing**: Automated testing of web applications
- **Social Media**: Interact with social platforms
- **E-commerce**: Automate shopping tasks

## Technical Details

### Browser Management

- **Browser**: Chromium (via Playwright)
- **Lifecycle**: Singleton pattern ensures one instance
- **Visibility**: Runs in visible mode for debugging
- **Speed**: 300ms slow_mo for human-readable actions

### Error Handling

- All functions return `bool` for success/failure
- Detailed logging at INFO and ERROR levels
- Graceful degradation on failures
- Timeout handling for element waits

### Performance

- **Startup**: ~2-3 seconds for browser launch
- **Navigation**: Depends on page load time
- **Actions**: 300ms delay between actions
- **Cleanup**: Automatic browser close on exit

## Dependencies

```
playwright>=1.40.0
```

Install browsers:
```bash
playwright install chromium
```

## Limitations

1. **Single Browser**: Only one browser instance at a time
2. **Synchronous**: Actions block until complete
3. **No Parallel**: Cannot run multiple browser tasks simultaneously
4. **Memory**: Browser consumes significant RAM

## Future Enhancements

1. **Multi-tab Support**: Open multiple tabs
2. **Cookie Management**: Save/load cookies
3. **Authentication**: Handle login flows
4. **File Downloads**: Download files from web
5. **iFrame Support**: Interact with embedded frames
6. **Mobile Emulation**: Test mobile websites

## Troubleshooting

### Browser Won't Launch

```bash
# Reinstall browsers
playwright install chromium
```

### Selector Not Found

- Use browser DevTools to verify selector
- Try alternative selectors (ID, class, text)
- Increase timeout value

### Slow Performance

- Reduce `slow_mo` value in `browser_actions.py`
- Use `headless=True` for faster execution

## Examples

### Example 1: Search GitHub

```python
actions = [
    {"action": "browser_navigate", "url": "https://github.com"},
    {"action": "browser_press_key", "key": "/"},
    {"action": "browser_press_key", "key": "R"},
    {"action": "browser_press_key", "key": "e"},
    {"action": "browser_press_key", "key": "a"},
    {"action": "browser_press_key", "key": "c"},
    {"action": "browser_press_key", "key": "t"},
    {"action": "browser_press_key", "key": "Enter"},
    {"action": "browser_screenshot", "path": "results.png"},
    {"action": "browser_close"}
]
```

### Example 2: Fill Form

```python
actions = [
    {"action": "browser_navigate", "url": "https://example.com/form"},
    {"action": "browser_type", "selector": "#name", "text": "John Doe"},
    {"action": "browser_type", "selector": "#email", "text": "john@example.com"},
    {"action": "browser_click", "selector": "button[type='submit']"},
    {"action": "browser_close"}
]
```

## Conclusion

The browser automation integration extends AXON's capabilities to the web, enabling sophisticated web interactions through the familiar action system. The modular design allows easy integration and future enhancements.

---

**Created**: 2026-05-17  
**Author**: Dev 2 (Ashish) - Executor & Safety  
**Status**: ✅ Tested and Working