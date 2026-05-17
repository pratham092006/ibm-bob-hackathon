# AXON Improved Navigation & Reasoning Guide

## What's New - Enhanced Features

### 🎯 Problem Solved
The 7B model (qwen2.5vl:7b) was successfully opening Discord and finding Pratham, but then clicking in wrong places instead of the text input field.

### ✨ New Features Implemented

#### 1. **Verbose Reasoning Display** 
Now you can see EXACTLY what the model is thinking at each step!

**Before:**
```
[AGENT LOOP] Action: left_click
[AGENT LOOP] Reasoning: Clicking on chat
```

**After:**
```
================================================================================
[ITERATION 3] MODEL DECISION:
================================================================================
🎯 Action: left_click
💭 Reasoning: Clicking on the text input field at bottom of chat to type message
📊 Confidence: 85.00%
📍 Target: (850, 1020)
================================================================================
```

**Benefits:**
- See the model's reasoning in real-time
- Understand why it's making each decision
- Identify when it's confused or uncertain
- Debug issues faster

#### 2. **Step-by-Step Task Guidance**
The model now receives explicit step tracking and knows where it is in the task.

**Example for "Open Discord and message Pratham good morning":**

```
✅ STEP 1 COMPLETE: Discord has been opened.
📋 NEXT STEP: Look for the target element (user, chat, input field) and interact with it.

✅ STEP 2 COMPLETE: Target user/chat has been clicked.
📋 NEXT STEP: Find and click the TEXT INPUT FIELD (look for 'Type a message', 'Message', or input box).
```

**Benefits:**
- Model knows which step it's on
- Clear guidance on what to do next
- Prevents confusion and wrong clicks
- Better task completion rate

#### 3. **Enhanced Text Input Field Detection**
Added specific instructions for finding and clicking text input fields.

**New Instructions:**
- Text input fields are usually at the BOTTOM of the chat window
- Look for text anchors: "Type a message", "Message @username", "Send a message"
- Input fields often have a light background or border
- DON'T click on chat messages or user names - click on the INPUT BOX
- If you can't find text anchor, look for the bottom-most clickable area

**Benefits:**
- More accurate clicking on input fields
- Fewer wrong clicks on chat history
- Better understanding of UI layout

#### 4. **Smart Action Analysis**
The system now analyzes recent actions and provides contextual warnings.

**Examples:**

**Repeated App Opening:**
```
⚠️ NOTICE: You've opened 'discord' multiple times. Check if it's ALREADY OPEN before trying again!
```

**Repeated Clicking:**
```
⚠️ NOTICE: You've clicked twice in a row. Make sure you're clicking the RIGHT element (text input field, not chat history).
```

**Benefits:**
- Prevents getting stuck in loops
- Helps model self-correct
- Reduces wasted actions

## How It Works Now

### Complete Task Flow Example

**Task:** "Open Discord and message Pratham good morning text"

#### Iteration 1: Open Discord
```
================================================================================
[ITERATION 1] MODEL DECISION:
================================================================================
🎯 Action: open_app
💭 Reasoning: Opening Discord application to access messaging
📊 Confidence: 95.00%
⌨️  Text: 'discord'
================================================================================
```
**Result:** Discord opens (waits 3 seconds)

#### Iteration 2: Find Pratham
```
================================================================================
[ITERATION 2] MODEL DECISION:
================================================================================
🎯 Action: left_click
💭 Reasoning: Clicking on Pratham's chat in the user list to open conversation
📊 Confidence: 88.00%
📍 Target: (250, 450)
================================================================================

✅ STEP 1 COMPLETE: Discord has been opened.
📋 NEXT STEP: Look for the target element (user, chat, input field) and interact with it.
```
**Result:** Pratham's chat opens

#### Iteration 3: Click Text Input
```
================================================================================
[ITERATION 3] MODEL DECISION:
================================================================================
🎯 Action: left_click
💭 Reasoning: Clicking on text input field at bottom of chat window to type message
📊 Confidence: 82.00%
📍 Target: (850, 1020)
================================================================================

✅ STEP 2 COMPLETE: Target user/chat has been clicked.
📋 NEXT STEP: Find and click the TEXT INPUT FIELD (look for 'Type a message', 'Message', or input box).
```
**Result:** Text input field is focused

#### Iteration 4: Type Message
```
================================================================================
[ITERATION 4] MODEL DECISION:
================================================================================
🎯 Action: type
💭 Reasoning: Typing the message content into the focused input field
📊 Confidence: 95.00%
⌨️  Text: 'good morning text'
================================================================================
```
**Result:** Message is typed

#### Iteration 5: Send Message
```
================================================================================
[ITERATION 5] MODEL DECISION:
================================================================================
🎯 Action: key
💭 Reasoning: Pressing Enter to send the message
📊 Confidence: 98.00%
⌨️  Text: 'enter'
================================================================================
```
**Result:** Message is sent

#### Iteration 6: Complete
```
================================================================================
[ITERATION 6] MODEL DECISION:
================================================================================
🎯 Action: done
💭 Reasoning: Task completed successfully - message sent to Pratham
📊 Confidence: 100.00%
================================================================================
```
**Result:** Task complete! ✅

## Debugging with New Features

### 1. Check Console Output
The verbose logging shows you exactly what's happening:

```bash
cd ibm-bob-hackathon/axon
python main.py
```

Watch for:
- 🎯 **Action** - What the model is doing
- 💭 **Reasoning** - Why it's doing it
- 📊 **Confidence** - How sure it is (low confidence = might be wrong)
- 📍 **Target** - Where it's clicking

### 2. Check Debug Screenshots
With `DEBUG_MODE = True` in config.py:
- Screenshots saved to `bob-reports/debug_screenshots/`
- Red markers show where model clicked
- Includes reasoning and confidence overlays

### 3. Analyze Step Progression
Look for the step completion messages:
```
✅ STEP 1 COMPLETE: Discord has been opened.
✅ STEP 2 COMPLETE: Target user/chat has been clicked.
```

If steps aren't completing, the model is stuck or confused.

## Common Issues & Solutions

### Issue 1: Model Clicks Wrong Area
**Symptoms:**
- Clicks on chat history instead of input field
- Clicks on user avatar instead of chat

**Solution:**
Check the reasoning:
```
💭 Reasoning: Clicking on message area
```
If reasoning is vague, the model is guessing. The new instructions should help it find the correct input field.

### Issue 2: Low Confidence Actions
**Symptoms:**
```
📊 Confidence: 45.00%
```

**Solution:**
- Low confidence (<60%) means model is uncertain
- Check if text anchors are available
- Model might need better screen context
- Consider using a larger model for complex UIs

### Issue 3: Repeated Actions
**Symptoms:**
```
⚠️ NOTICE: You've clicked twice in a row.
```

**Solution:**
- Model is stuck or confused
- Check debug screenshots to see what it's seeing
- May need to manually guide with more specific task description

## Performance Tips

### 1. Use Specific Task Descriptions
**Bad:** "Message Pratham"
**Good:** "Open Discord, find Pratham in the user list, click on his chat, click the text input field at the bottom, type 'good morning text', and press Enter"

### 2. Enable Debug Mode
```python
# In config.py
DEBUG_MODE = True
```
This saves screenshots so you can see what the model sees.

### 3. Monitor Confidence Scores
- **>80%** - Model is confident, likely correct
- **60-80%** - Model is somewhat sure, might work
- **<60%** - Model is guessing, likely to fail

### 4. Check Step Progression
Make sure each step completes before moving to next:
```
✅ STEP 1 COMPLETE
✅ STEP 2 COMPLETE
✅ STEP 3 COMPLETE
```

## Comparison: Before vs After

### Before Improvements:
```
[AGENT LOOP] Action: left_click
[AGENT LOOP] Reasoning: Clicking
[AGENT LOOP] Confidence: 0.7
```
❌ Vague reasoning
❌ No step tracking
❌ No guidance on what to do next
❌ Clicks in wrong places

### After Improvements:
```
================================================================================
[ITERATION 3] MODEL DECISION:
================================================================================
🎯 Action: left_click
💭 Reasoning: Clicking on text input field at bottom of chat window to type message
📊 Confidence: 82.00%
📍 Target: (850, 1020)
================================================================================

✅ STEP 2 COMPLETE: Target user/chat has been clicked.
📋 NEXT STEP: Find and click the TEXT INPUT FIELD (look for 'Type a message', 'Message', or input box).
```
✅ Clear, detailed reasoning
✅ Step tracking shows progress
✅ Explicit guidance on next action
✅ More accurate clicking

## Advanced Features

### Custom Step Definitions
You can modify the step detection in `core/llm.py` to add custom steps for your specific workflows.

### Confidence Thresholds
Adjust confidence requirements in `core/loop.py` to make the model more or less cautious.

### Extended History
Increase history length in `core/llm.py` (currently shows last 5 actions) to give model more context.

## Next Steps

### Recommended Enhancements:
1. **Add Discord-specific handlers** - Keyboard shortcuts for common actions
2. **Implement visual element detection** - Use computer vision to find input fields
3. **Add retry logic** - Automatically retry failed actions with different approach
4. **Create task templates** - Pre-defined workflows for common tasks

### Testing Checklist:
- [ ] Test with simple tasks (open app)
- [ ] Test with medium tasks (open app + click)
- [ ] Test with complex tasks (open + find + type + send)
- [ ] Check debug screenshots for accuracy
- [ ] Monitor confidence scores
- [ ] Verify step progression

## Summary

Your AXON agent now has:
- ✅ **Verbose reasoning display** - See what it's thinking
- ✅ **Step-by-step guidance** - Knows where it is in the task
- ✅ **Better input field detection** - Finds text boxes accurately
- ✅ **Smart action analysis** - Self-corrects when stuck
- ✅ **7B model** - Faster responses with good accuracy

**The Discord messaging task should now work much better!** 🎉

---

**Made with Bob** 🤖