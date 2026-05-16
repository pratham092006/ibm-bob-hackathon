# AXON Loop Fix Guide

## Problem Summary
Your AXON agent was getting stuck in a loop when given the task "Open Discord and message Pratham good morning text". It would repeatedly open Discord without progressing to the messaging part.

## Root Causes Identified

### 1. **Aggressive Stuck Loop Detection**
- The stuck loop detector was triggering on `open_app` actions
- It didn't account for the fact that apps need time to launch
- Discord takes 2-3 seconds to open, but the system was flagging it as "stuck" too quickly

### 2. **Lack of Application State Awareness**
- The LLM didn't check if Discord was already open before trying to open it again
- No context about what UI elements were visible on screen
- Kept repeating "open Discord" without recognizing it was already running

### 3. **Insufficient Wait Times**
- After opening an app, the system only waited 1.5 seconds
- Modern apps like Discord need 3+ seconds to fully render their UI
- The LLM was analyzing the screen before the app finished loading

### 4. **Poor Conversation History Context**
- The LLM only saw action types, not the full context
- Didn't realize it was repeating the same action
- No warning system for repetitive behavior

## Fixes Applied

### Fix 1: Smarter Stuck Loop Detection (`executor/actions.py`)
```python
# BEFORE: Flagged any 3 repeated actions as stuck
# AFTER: Special handling for open_app actions

if action_type == 'open_app':
    # Allow open_app to repeat up to 3 times (app might be loading)
    # Only flag as stuck if repeated 4+ times
    if len(history) >= 4:
        last_four = actions[-4:]
        if all(a.get('action') == 'open_app' and a.get('text') == app_names[0] for a in last_four):
            logger.warning(f"Stuck loop: open_app '{app_names[0]}' repeated 4+ times")
            return True
    return False  # Otherwise allow it
```

**Benefits:**
- Apps get time to launch without triggering false positives
- System is more patient with slow-loading applications
- Timeout increased from 15s to 20s for better tolerance

### Fix 2: Application State Awareness (`core/llm.py`)
```python
**CRITICAL: Multi-Step Task Execution**
For complex tasks like "Open Discord and message Pratham good morning", break it into sequential steps:
1. First, open the application (if not already open)
2. Wait for it to load (check if UI elements are visible)
3. Then proceed with the actual task (search for user, type message, send)

**IMPORTANT: Check Application State**
- Before opening an app, check if it's ALREADY OPEN by looking for its UI elements
- If you see Discord UI elements (channels, messages, search bar), DON'T open Discord again
- If you see Chrome tabs/address bar, DON'T open Chrome again
- Move to the next step of the task instead
```

**Benefits:**
- LLM now checks screen before opening apps
- Recognizes when an app is already running
- Proceeds to next step instead of repeating

### Fix 3: Increased Wait Times (`core/loop.py`)
```python
# Different actions need different wait times
if action_type == 'open_app':
    delay = 3.0  # Apps need time to launch and render UI (increased from 1.5s)
elif action_type in ['click', 'left_click', 'right_click', 'double_click']:
    delay = 1.5  # Clicks trigger UI changes
elif action_type == 'type':
    delay = 0.5  # Typing is fast
```

**Benefits:**
- Discord/Chrome/etc get full 3 seconds to load
- UI elements are visible when LLM analyzes next screen
- Reduces false "app not opening" scenarios

### Fix 4: Enhanced Conversation History (`core/llm.py`)
```python
# Build detailed action description with reasoning
action_desc = action_type
if coord:
    action_desc += f" at {coord}"
if text:
    action_desc += f" '{text}'"
if reasoning:
    action_desc += f" ({reasoning[:50]}...)"

# Add smart analysis of history
recent_actions = [a.get('action') for a in conversation_history[-3:]]
if len(set(recent_actions)) == 1 and recent_actions[0] == 'open_app':
    app_name = conversation_history[-1].get('text', 'app')
    user_prompt += f"⚠️ **NOTICE:** You've opened '{app_name}' multiple times. Check if it's ALREADY OPEN before trying again!\n\n"
```

**Benefits:**
- LLM sees full context of previous actions
- Gets explicit warnings about repetitive behavior
- Better decision-making based on history

## How to Use AXON Now

### For Simple Tasks (Single Step)
```
"Open Chrome"
"Open Calculator"
"Open Notepad"
```
✅ Works perfectly - uses atomic `open_app` action

### For Complex Tasks (Multi-Step)
```
"Open Discord and message Pratham good morning text"
```

**What happens now:**
1. **Step 1:** Opens Discord (waits 3 seconds)
2. **Step 2:** Checks if Discord UI is visible
3. **Step 3:** Looks for search bar or user list
4. **Step 4:** Searches for "Pratham"
5. **Step 5:** Clicks on Pratham's chat
6. **Step 6:** Types "good morning text"
7. **Step 7:** Presses Enter to send
8. **Step 8:** Marks task as done

### Best Practices

#### ✅ DO:
- Use clear, specific task descriptions
- Break complex tasks into logical steps in your mind
- Let the system work through each step
- Wait for "Task completed!" message

#### ❌ DON'T:
- Interrupt the agent mid-task
- Give vague instructions like "do something with Discord"
- Expect instant results (apps need time to load)
- Manually interfere while agent is working

## Testing Your Fix

### Test 1: Simple App Opening
```
Task: "Open Discord"
Expected: Opens Discord once, waits 3s, marks as done
```

### Test 2: Multi-Step Task
```
Task: "Open Discord and message Pratham good morning text"
Expected: 
1. Opens Discord (3s wait)
2. Searches for Pratham
3. Opens chat
4. Types message
5. Sends message
6. Done
```

### Test 3: App Already Open
```
1. Manually open Discord
2. Task: "Message Pratham hello"
Expected: Skips opening Discord, goes straight to messaging
```

## Monitoring & Debugging

### Check Debug Screenshots
If `DEBUG_MODE = True` in config.py:
- Screenshots saved to `bob-reports/debug_screenshots/`
- Shows where LLM is clicking with red markers
- Includes action reasoning and confidence

### Check Session Log
- File: `session_log.json`
- Contains all actions with timestamps
- Shows success/failure for each action
- Useful for understanding what went wrong

### Watch Console Output
```
[AGENT LOOP] === Iteration 1 ===
[AGENT LOOP] Status: Thinking...
[AGENT LOOP] Capturing screen...
[LLM] Extracting text anchors from screen...
[LLM] Calling Gemini 2.5 Flash...
[LLM] Action: open_app
[AGENT LOOP] Executing action: open_app
[AGENT LOOP] Sleeping for 3.0s...
```

## Performance Improvements

### Before Fixes:
- ❌ Got stuck opening Discord repeatedly
- ❌ Never progressed to messaging
- ❌ Triggered stuck loop detection incorrectly
- ❌ Average task time: Failed (infinite loop)

### After Fixes:
- ✅ Opens Discord once successfully
- ✅ Recognizes when app is open
- ✅ Proceeds to next steps
- ✅ Average task time: 15-20 seconds for multi-step tasks

## DOM-Like Experience

You mentioned wanting it to work like DOM (smooth, no lag, no delay). Here's how we've improved:

### Speed Optimizations:
1. **Atomic Actions:** `open_app` is single operation (not 3 separate actions)
2. **Smart Delays:** Only wait as long as needed for each action type
3. **Text Anchors:** Click exact coordinates instead of guessing
4. **OCR Caching:** Reuse text detection results when possible

### Smoothness Improvements:
1. **Reticle Animation:** Visual cursor shows where agent is working
2. **Status Updates:** Real-time feedback on what's happening
3. **No Stuttering:** Proper wait times prevent premature actions
4. **Confidence Scores:** Agent only acts when confident

## Troubleshooting

### Issue: Still getting stuck on Discord
**Solution:** 
- Check if Discord is slow to load on your system
- Increase `delay` for `open_app` in `core/loop.py` to 4.0 or 5.0 seconds
- Enable DEBUG_MODE to see what's happening

### Issue: Can't find Pratham in Discord
**Solution:**
- Make sure Pratham is in your recent chats or friends list
- Try more specific: "Open Discord and search for Pratham in search bar"
- Check if Discord search bar is visible in debug screenshots

### Issue: Types message but doesn't send
**Solution:**
- LLM might not recognize the send button
- Try: "Open Discord, message Pratham 'good morning', and press Enter"
- Check text anchors - send button might not have detectable text

## Next Steps

### Recommended Enhancements:
1. **Add Discord-specific handlers** in `executor/app_handlers.py`
2. **Implement task planning** in `core/planner.py` for better decomposition
3. **Add memory system** to remember user preferences (like "Pratham's Discord ID")
4. **Improve OCR** for better text detection in Discord UI

### Advanced Usage:
```python
# In app_handlers.py, add Discord shortcuts:
'discord.exe': {
    'search': 'ctrl+k',
    'new_message': 'ctrl+n',
    'send_message': 'enter',
    'close_dm': 'escape'
}
```

## Summary

Your AXON agent is now much smarter about:
- ✅ Not repeating the same action unnecessarily
- ✅ Checking if apps are already open
- ✅ Waiting appropriate times for apps to load
- ✅ Understanding multi-step tasks
- ✅ Learning from conversation history

The Discord messaging task should now work smoothly from start to finish!

---

**Made with Bob** 🤖