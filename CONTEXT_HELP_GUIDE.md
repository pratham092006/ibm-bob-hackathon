# AXON Context Help Feature Guide

## Overview
AXON has two modes when you press **Alt+G**:
1. **Task Dialog Mode** - Opens when NO text is selected
2. **Context Help Mode** - Activates when text IS selected

## Fixed Issues

### Issue 1: Loading Screen Appearing with Alt+G ✅ FIXED
**Problem:** The overlay (loading screen) was appearing when pressing Alt+G to open the task dialog.

**Root Cause:** The overlay has a continuous timer that runs at 60 FPS, and it was automatically showing itself even when the dialog was open.

**Solution Implemented:**
1. Added `_dialog_is_open` flag to the overlay to track dialog state
2. Added `set_dialog_open(is_open)` method to lock/unlock the overlay
3. Modified `show_overlay()` and `show_reticle()` to respect the dialog lock
4. Updated `main.py` to call `set_dialog_open(True)` when dialog opens
5. Updated `main.py` to call `set_dialog_open(False)` when task starts or answer overlay closes

**Files Modified:**
- `ui/overlay.py` - Added dialog lock mechanism
- `main.py` - Added calls to lock/unlock overlay at appropriate times

### Issue 2: How to Use Context Help Feature ✅ DOCUMENTED

## How to Test Both Modes

### Mode 1: Task Dialog (No Text Selected)

**Steps:**
1. Run AXON: `python main.py`
2. Press **Alt+G** (without selecting any text)
3. Task input dialog should appear
4. **NO loading screen/overlay should appear**

**Expected Console Output:**
```
============================================================
[HOTKEY] Alt+G pressed - NO TEXT SELECTED
[MODE] Task Dialog Mode
============================================================

[MAIN] Locking overlay (dialog mode)
[OVERLAY] Dialog opened - overlay hidden and locked
[MAIN] Opening task input dialog...
[MAIN] Task dialog opened successfully
```

**What Should Happen:**
- ✅ Task input dialog appears
- ✅ NO overlay/loading screen appears
- ✅ You can type your task
- ✅ When you submit, overlay unlocks and shows for task execution

### Mode 2: Context Help (Text Selected)

**Steps:**
1. Run AXON: `python main.py`
2. Run the test helper: `python test_highlight_feature.py`
   - This creates a test file on your Desktop
   - Opens it in Notepad automatically
3. In the opened file, **select some text** (e.g., the Python code example)
4. Press **Alt+G**
5. Wait for the AI response overlay to appear

**Expected Console Output:**
```
============================================================
[HOTKEY] Alt+G pressed - TEXT SELECTED
[MODE] Context Help Mode
[TEXT] Selected: 'def fibonacci(n):...'
============================================================

[MAIN] Hiding task dialog (context help mode)
[MAIN] Keeping overlay hidden (context help mode)
[OVERLAY] Dialog opened - overlay hidden and locked
[MAIN] Showing answer overlay with loading state...
[CONTEXT] Requesting AI help for selected text...
[MAIN] Context help request started

[CONTEXT] Received answer (XXX chars)
```

**What Should Happen:**
- ✅ A transparent answer overlay appears
- ✅ Shows "Loading..." initially
- ✅ Then displays the AI's response
- ✅ The main overlay (cursor tracker) stays hidden
- ✅ You can close the answer overlay with the X button

## Quick Test Script

Run this to test the context help feature:
```bash
cd ibm-bob-hackathon/axon
python test_highlight_feature.py
```

This will:
1. Create a test file on your Desktop with sample text
2. Open it in Notepad
3. Show you instructions on how to test

## Testing Checklist

### Task Dialog Mode (Alt+G without selection)
- [ ] Press Alt+G without selecting text
- [ ] Task dialog appears
- [ ] NO loading screen/overlay appears
- [ ] Console shows "Task Dialog Mode"
- [ ] Can type and submit task
- [ ] Overlay appears ONLY after submitting task

### Context Help Mode (Alt+G with selection)
- [ ] Select text in any application
- [ ] Press Alt+G
- [ ] Answer overlay appears (not the cursor overlay)
- [ ] Console shows "Context Help Mode"
- [ ] Console shows the selected text
- [ ] AI response appears in the overlay
- [ ] Can close the answer overlay
- [ ] Main cursor overlay stays hidden

## Console Messages Reference

### Task Dialog Mode Messages
```
[HOTKEY] Alt+G pressed - NO TEXT SELECTED
[MODE] Task Dialog Mode
[MAIN] Locking overlay (dialog mode)
[OVERLAY] Dialog opened - overlay hidden and locked
[MAIN] Opening task input dialog...
```

### Context Help Mode Messages
```
[HOTKEY] Alt+G pressed - TEXT SELECTED
[MODE] Context Help Mode
[TEXT] Selected: '...'
[MAIN] Keeping overlay hidden (context help mode)
[CONTEXT] Requesting AI help for selected text...
[CONTEXT] Received answer (XXX chars)
```

### Task Execution Messages (after submitting task)
```
[MAIN] Unlocking overlay (task starting)
[MAIN] Showing AI cursor overlay...
[MAIN] Overlay shown at center (X, Y)
```

## Troubleshooting

### Problem: Overlay still appears when opening dialog
**Solution:** Make sure you're running the latest version with the fixes applied.

### Problem: Context help not working
**Check:**
1. Is text actually selected? (highlight it with your mouse)
2. Is AXON running? (check console for startup messages)
3. Check console for error messages

### Problem: Answer overlay doesn't appear
**Check:**
1. Console should show "Context Help Mode"
2. Check for error messages in console
3. Make sure your LLM is configured correctly (check .env file)

## Technical Details

### Overlay Lock Mechanism
The overlay now has two flags:
- `_should_be_visible`: Tracks if overlay should be shown (set by show/hide methods)
- `_dialog_is_open`: Locks the overlay when dialog is open (prevents auto-show)

When dialog opens:
```python
overlay.set_dialog_open(True)  # Locks overlay
```

When dialog closes or task starts:
```python
overlay.set_dialog_open(False)  # Unlocks overlay
```

### Mode Detection
The global hotkey handler detects which mode to use:
- If text is selected → Context Help Mode
- If no text selected → Task Dialog Mode

## Files Involved

### Modified Files
- `ui/overlay.py` - Added dialog lock mechanism
- `main.py` - Added mode detection and logging

### New Files
- `test_highlight_feature.py` - Test helper script
- `CONTEXT_HELP_GUIDE.md` - This guide

## Summary

✅ **Issue 1 Fixed:** Loading screen no longer appears when pressing Alt+G to open task dialog
✅ **Issue 2 Documented:** Clear instructions on how to use and test the context help feature
✅ **Enhanced Logging:** Console messages clearly show which mode is active
✅ **Test Script:** Easy way to test the context help feature

Both modes now work correctly with clear visual and console feedback!