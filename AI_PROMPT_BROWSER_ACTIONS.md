# AI System Prompt - Browser Automation Actions

## Overview

This document contains the browser automation action specifications to be added to AXON's AI system prompt. These actions enable the AI to control web browsers through Playwright.

## Browser Actions for AI Prompt

Add the following to AXON's system prompt in the "Available Actions" section:

---

### Browser Automation Actions

You can now control web browsers to search for information, interact with websites, and extract data. Use these actions for web-based tasks:

#### browser_navigate
Navigate to a URL in the browser.

**Format:**
```json
{
    "action": "browser_navigate",
    "url": "https://example.com"
}
```

**Parameters:**
- `url` (required): The full URL to navigate to (must include http:// or https://)

**Example:**
```json
{"action": "browser_navigate", "url": "https://github.com"}
```

---

#### browser_click
Click an element on the webpage using a CSS selector.

**Format:**
```json
{
    "action": "browser_click",
    "selector": "button.submit",
    "timeout": 10000
}
```

**Parameters:**
- `selector` (required): CSS selector for the element to click
- `timeout` (optional): Maximum wait time in milliseconds (default: 10000)

**Examples:**
```json
{"action": "browser_click", "selector": "button[type='submit']"}
{"action": "browser_click", "selector": "#search-button"}
{"action": "browser_click", "selector": ".nav-link"}
```

**Common Selectors:**
- By ID: `#element-id`
- By class: `.class-name`
- By tag: `button`, `a`, `input`
- By attribute: `[name='search']`, `[type='submit']`
- By text: `button:has-text("Submit")`

---

#### browser_type
Type text into an input field.

**Format:**
```json
{
    "action": "browser_type",
    "selector": "input[name='search']",
    "text": "search query",
    "timeout": 10000
}
```

**Parameters:**
- `selector` (required): CSS selector for the input element
- `text` (required): Text to type into the field
- `timeout` (optional): Maximum wait time in milliseconds (default: 10000)

**Examples:**
```json
{"action": "browser_type", "selector": "#username", "text": "john_doe"}
{"action": "browser_type", "selector": "input[type='email']", "text": "user@example.com"}
{"action": "browser_type", "selector": "textarea", "text": "Multi-line\ntext content"}
```

---

#### browser_press_key
Press a keyboard key in the browser.

**Format:**
```json
{
    "action": "browser_press_key",
    "key": "Enter"
}
```

**Parameters:**
- `key` (required): Key to press

**Common Keys:**
- `Enter` - Submit forms, confirm actions
- `Escape` - Close dialogs, cancel actions
- `Tab` - Navigate between fields
- `ArrowDown`, `ArrowUp`, `ArrowLeft`, `ArrowRight` - Navigation
- `/` - Open GitHub search (site-specific shortcut)
- `Control+A` - Select all
- `Control+C` - Copy
- `Control+V` - Paste

**Examples:**
```json
{"action": "browser_press_key", "key": "Enter"}
{"action": "browser_press_key", "key": "/"}
{"action": "browser_press_key", "key": "Escape"}
```

---

#### browser_wait
Wait for an element to appear on the page.

**Format:**
```json
{
    "action": "browser_wait",
    "selector": ".results-list",
    "timeout": 10000
}
```

**Parameters:**
- `selector` (required): CSS selector for the element to wait for
- `timeout` (optional): Maximum wait time in milliseconds (default: 10000)

**Examples:**
```json
{"action": "browser_wait", "selector": ".search-results"}
{"action": "browser_wait", "selector": "#loading-complete", "timeout": 30000}
```

---

#### browser_screenshot
Capture a screenshot of the current page.

**Format:**
```json
{
    "action": "browser_screenshot",
    "path": "axon/bob-reports/screenshot.png"
}
```

**Parameters:**
- `path` (optional): File path to save screenshot (default: "axon/bob-reports/browser_screenshot.png")

**Examples:**
```json
{"action": "browser_screenshot", "path": "axon/bob-reports/search_results.png"}
{"action": "browser_screenshot"}
```

---

#### browser_close
Close the browser and cleanup resources.

**Format:**
```json
{
    "action": "browser_close"
}
```

**Parameters:** None

**Example:**
```json
{"action": "browser_close"}
```

---

## Usage Guidelines for AI

### When to Use Browser Actions

Use browser actions when you need to:
- Search for information on websites
- Extract data from web pages
- Fill out web forms
- Navigate through web applications
- Verify website content
- Capture visual evidence of web pages

### Best Practices

1. **Always start with browser_navigate**
   ```json
   {"action": "browser_navigate", "url": "https://example.com"}
   ```

2. **Use keyboard shortcuts when available**
   - GitHub search: Press `/` instead of clicking search button
   - Submit forms: Press `Enter` instead of clicking submit

3. **Wait for dynamic content**
   ```json
   {"action": "browser_wait", "selector": ".results-loaded"}
   ```

4. **Take screenshots for verification**
   ```json
   {"action": "browser_screenshot", "path": "axon/bob-reports/verification.png"}
   ```

5. **Always close browser when done**
   ```json
   {"action": "browser_close"}
   ```

### Common Workflows

#### Search GitHub for a Repository
```json
{"action": "browser_navigate", "url": "https://github.com"}
{"action": "browser_press_key", "key": "/"}
{"action": "browser_press_key", "key": "R"}
{"action": "browser_press_key", "key": "e"}
{"action": "browser_press_key", "key": "a"}
{"action": "browser_press_key", "key": "c"}
{"action": "browser_press_key", "key": "t"}
{"action": "browser_press_key", "key": "Enter"}
{"action": "browser_screenshot", "path": "axon/bob-reports/github_search.png"}
{"action": "browser_close"}
```

#### Fill Out a Web Form
```json
{"action": "browser_navigate", "url": "https://example.com/form"}
{"action": "browser_type", "selector": "#name", "text": "John Doe"}
{"action": "browser_type", "selector": "#email", "text": "john@example.com"}
{"action": "browser_type", "selector": "#message", "text": "Hello, this is a test message."}
{"action": "browser_click", "selector": "button[type='submit']"}
{"action": "browser_wait", "selector": ".success-message"}
{"action": "browser_screenshot", "path": "axon/bob-reports/form_submitted.png"}
{"action": "browser_close"}
```

#### Research a Topic
```json
{"action": "browser_navigate", "url": "https://www.google.com"}
{"action": "browser_type", "selector": "input[name='q']", "text": "Python web scraping"}
{"action": "browser_press_key", "key": "Enter"}
{"action": "browser_wait", "selector": "#search"}
{"action": "browser_screenshot", "path": "axon/bob-reports/search_results.png"}
{"action": "browser_close"}
```

---

## Error Handling

If a browser action fails:
1. The action will return `false` and log an error
2. You can retry with a different selector or approach
3. Consider using `browser_press_key` as a fallback for clicks
4. Increase timeout for slow-loading pages

---

## Limitations

1. **Single Browser Instance**: Only one browser can be active at a time
2. **Synchronous Execution**: Actions execute one at a time
3. **No Multi-tab Support**: Currently limited to single tab
4. **Selector Dependency**: Requires valid CSS selectors

---

## Integration Status

✅ **Fully Integrated**: Browser actions are now part of AXON's action system
✅ **Tested**: Successfully tested with GitHub search workflow
✅ **Documented**: Complete documentation available in BROWSER_AUTOMATION_README.md
✅ **Ready for Production**: AI can use these actions immediately

---

## Example: Complete AI Task

**User Request:** "Search GitHub for React and take a screenshot"

**AI Response (Action Sequence):**
```json
{"action": "browser_navigate", "url": "https://github.com"}
{"action": "browser_press_key", "key": "/"}
{"action": "browser_type", "selector": "#query-builder-test", "text": "React"}
{"action": "browser_press_key", "key": "Enter"}
{"action": "browser_wait", "selector": ".repo-list"}
{"action": "browser_screenshot", "path": "axon/bob-reports/react_search.png"}
{"action": "browser_close"}
{"action": "done"}
```

---

**Last Updated:** 2026-05-17  
**Status:** ✅ Production Ready