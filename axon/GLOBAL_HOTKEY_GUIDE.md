# Global Hotkey Feature Guide (Alt+G)

## Overview

AXON now includes a powerful global hotkey feature that allows you to interact with the AI assistant from anywhere on your system using **Alt+G**. This feature works in two intelligent modes:

1. **Task Dialog Mode** - Opens the task input dialog when no text is selected
2. **Context Help Mode** - Provides AI-powered explanations when text is selected

## Features

### Feature 1: Quick Task Dialog (Alt+G)

Press **Alt+G** anywhere on your system to instantly open the AXON task input dialog.

**Use Cases:**
- Quickly start a new task without switching to the AXON window
- Access AXON from any application
- Streamlined workflow for frequent task submissions

**How to Use:**
1. Press **Alt+G** (no text selection needed)
2. The task input dialog appears
3. Type your task and press Enter or click Start

### Feature 2: Context-Aware Help (Select + Alt+G)

Select any text on your screen, press **Alt+G**, and get instant AI-powered explanations and help.

**Use Cases:**
- Understand unfamiliar code snippets
- Get explanations for technical terms
- Learn about error messages
- Understand documentation or articles
- Get help with any selected text

**How to Use:**
1. Select/highlight any text on your screen (in any application)
2. Press **Alt+G**
3. A transparent overlay appears with AI-generated help
4. Click anywhere or press **Esc** to close the overlay

## Technical Details

### Architecture

The global hotkey system consists of four main components:

1. **Global Hotkey Listener** (`executor/global_hotkey.py`)
   - Uses `pynput` for system-wide keyboard monitoring
   - Detects Alt+G key combination
   - Captures selected text via clipboard

2. **Context Help Engine** (`core/context_help.py`)
   - Queries the configured LLM (Gemini, Claude, OpenRouter, NVIDIA, or Ollama)
   - Generates helpful explanations for selected text
   - Supports all LLM providers configured in AXON

3. **Answer Overlay** (`ui/answer_overlay.py`)
   - Semi-transparent PyQt6 window
   - Displays AI responses with formatted text
   - Dismissible by click or Esc key
   - Automatically hides main dialog during display

4. **Main Application Integration** (`main.py`)
   - Initializes global hotkey on startup
   - Coordinates between task dialog and context help modes
   - Manages UI state transitions

### Text Selection Detection

The system uses a smart clipboard-based approach:

1. Saves current clipboard content
2. Simulates Ctrl+C to copy selected text
3. Retrieves the copied text
4. Restores original clipboard content
5. Determines mode based on whether text was captured

### LLM Integration

Context help uses the same LLM provider configured for AXON:

- **Gemini**: Uses `gemini-2.0-flash-exp` for fast responses
- **Claude**: Uses configured Claude model (Sonnet, Haiku, or Opus)
- **OpenRouter**: Uses configured OpenRouter model
- **NVIDIA**: Uses NVIDIA API with configured model
- **Ollama**: Uses local Ollama model

The prompt is optimized to provide:
- Clear, concise explanations
- Context and purpose of the text
- Technical details for code/technical content
- Practical usage examples
- Common issues and tips

## Configuration

No additional configuration is required! The global hotkey feature:

- Automatically starts with AXON
- Uses your existing LLM configuration
- Works system-wide (even when AXON is in background)
- Requires no special permissions

## Keyboard Shortcuts Summary

| Shortcut | Action | Context |
|----------|--------|---------|
| **Alt+G** | Open task dialog | No text selected |
| **Alt+G** | Get context help | Text is selected |
| **F12** | Emergency stop | During task execution |
| **Esc** | Close answer overlay | Answer overlay visible |

## Examples

### Example 1: Understanding Code

1. Select this Python code:
   ```python
   async def fetch_data(url):
       async with aiohttp.ClientSession() as session:
           async with session.get(url) as response:
               return await response.json()
   ```

2. Press **Alt+G**

3. Get explanation:
   - What async/await means
   - How aiohttp works
   - Context manager usage
   - Best practices

### Example 2: Error Message Help

1. Select an error message:
   ```
   ModuleNotFoundError: No module named 'requests'
   ```

2. Press **Alt+G**

3. Get help:
   - What the error means
   - How to fix it (pip install requests)
   - Common causes
   - Prevention tips

### Example 3: Quick Task

1. Press **Alt+G** (no selection)
2. Type: "Open Chrome and search for Python tutorials"
3. Press Enter
4. AXON executes the task

## Troubleshooting

### Alt+G Not Working

**Problem**: Hotkey doesn't respond

**Solutions**:
- Check if AXON is running (system tray icon should be visible)
- Verify no other application is using Alt+G
- Restart AXON
- Check console for error messages

### Text Selection Not Detected

**Problem**: Context help doesn't trigger with selected text

**Solutions**:
- Ensure text is actually selected (highlighted)
- Try selecting again and pressing Alt+G
- Some applications may block clipboard access
- Try in a different application (e.g., Notepad, browser)

### Answer Overlay Not Appearing

**Problem**: No overlay shows after Alt+G with selected text

**Solutions**:
- Check console for LLM errors
- Verify LLM API keys are configured correctly
- Check internet connection (for cloud LLMs)
- Try with a shorter text selection

### Slow Response

**Problem**: Context help takes too long

**Solutions**:
- Switch to a faster model (e.g., Gemini Flash, Claude Haiku)
- Use local Ollama for instant responses
- Reduce selected text length
- Check internet connection speed

## Best Practices

### For Task Dialog Mode

1. **Use descriptive tasks**: "Open Chrome and navigate to GitHub" is better than "Open Chrome"
2. **Be specific**: Include details about what you want to accomplish
3. **One task at a time**: Break complex workflows into steps

### For Context Help Mode

1. **Select relevant text**: Include enough context but not too much
2. **Use for learning**: Great for understanding new concepts
3. **Code snippets**: Select complete functions or logical blocks
4. **Error messages**: Include the full error for better help

### General Tips

1. **Keyboard-first workflow**: Alt+G is faster than mouse navigation
2. **Combine with F12**: Use F12 to stop tasks if needed
3. **Experiment**: Try context help on various types of text
4. **Privacy**: Be mindful of sensitive text (it's sent to LLM)

## Privacy & Security

### Data Handling

- Selected text is sent to your configured LLM provider
- No data is stored locally by AXON
- Clipboard is temporarily used but restored
- Follow your LLM provider's privacy policy

### Recommendations

- Don't select sensitive information (passwords, API keys, personal data)
- Use local Ollama for private/sensitive content
- Be aware of your LLM provider's data retention policies
- Consider using context help only for public/non-sensitive text

## Performance

### Response Times

| Provider | Typical Response Time |
|----------|----------------------|
| Gemini Flash | 1-3 seconds |
| Claude Haiku | 1-2 seconds |
| Claude Sonnet | 2-4 seconds |
| OpenRouter | 2-5 seconds |
| NVIDIA | 2-4 seconds |
| Ollama (local) | 0.5-2 seconds |

### Resource Usage

- **CPU**: Minimal (keyboard listener is lightweight)
- **Memory**: ~50MB for overlay UI
- **Network**: Only when querying cloud LLMs
- **GPU**: Used by Ollama if available

## Advanced Usage

### Custom Prompts

The context help prompt is optimized for general use. For custom behavior, you can modify `core/context_help.py`:

```python
def _build_help_prompt(selected_text: str) -> str:
    # Customize this function for different prompt styles
    return f"Your custom prompt with {selected_text}"
```

### Integration with Other Tools

The global hotkey system can be extended:

1. Add more hotkey combinations in `executor/global_hotkey.py`
2. Create additional overlay types in `ui/`
3. Add new LLM query types in `core/context_help.py`

## Limitations

1. **Windows Only**: Global hotkeys use Windows-specific APIs
2. **Clipboard Dependency**: Text selection requires clipboard access
3. **Application Compatibility**: Some apps may block clipboard operations
4. **LLM Availability**: Requires working LLM configuration
5. **Internet Required**: For cloud-based LLMs (not Ollama)

## Future Enhancements

Potential improvements for future versions:

- [ ] Multiple hotkey combinations (Alt+H, Alt+E, etc.)
- [ ] Customizable overlay themes
- [ ] History of context help queries
- [ ] Offline mode with cached responses
- [ ] Voice input integration
- [ ] Screenshot-based context help
- [ ] Multi-language support
- [ ] Custom prompt templates

## Support

If you encounter issues:

1. Check the console output for error messages
2. Verify your LLM configuration in `.env`
3. Test with different text selections
4. Try switching LLM providers
5. Restart AXON

For bugs or feature requests, please report them in the project repository.

---

**Made with Bob** 🤖

Last Updated: 2026-05-17