# Print Document Integration Guide

## Overview

The `print_document` action has been successfully integrated into AXON's natural language task system. Users can now ask AXON to print documents using natural language commands, and AXON will automatically execute the print automation script.

## What Was Added

### 1. Action Handler (`executor/actions.py`)

**New Function: `_print_document(document_name=None)`**
- Location: Lines 290-348 in `executor/actions.py`
- Executes the `print_document_automation.py` script as a subprocess
- Handles success/failure/timeout scenarios
- Uses `pythonw.exe` to avoid console window popup on Windows
- 60-second timeout for safety

**Integration in `execute_action()`**
- Added new action type handler at line 489-492
- Routes `print_document` actions to the `_print_document()` function
- Extracts optional document name from action dictionary

### 2. LLM System Instruction (`core/llm.py`)

**Updated `_get_system_instruction()` function:**

**New Action Definition (line 250):**
```
print_document:{"action":"print_document","text":"KheloParty_Full_Plan","reasoning":"printing document","confidence":0.95}
```

**New Task Rule (line 241):**
```
9. To print a document: use print_document action with the document name (e.g., "KheloParty_Full_Plan"). 
   This will automatically open and print the document.
```

### 3. Test Script

**Created: `test_print_integration.py`**
- Validates that the action is recognized by the system
- Provides dry-run testing without actually printing
- Includes optional full integration test with user confirmation
- Demonstrates proper action dictionary format

## How to Use

### Natural Language Commands

Users can now use any of these phrases with AXON:

1. **"Print KheloParty_Full_Plan"**
2. **"Open and print KheloParty_Full_Plan"**
3. **"Print the document to my printer"**
4. **"Please print KheloParty_Full_Plan.docx"**
5. **"Send KheloParty_Full_Plan to the printer"**

### Action Dictionary Format

When the LLM recognizes a print request, it should return:

```json
{
  "action": "print_document",
  "text": "KheloParty_Full_Plan",
  "reasoning": "User requested to print the document",
  "confidence": 0.95
}
```

**Parameters:**
- `action`: Must be `"print_document"`
- `text`: (Optional) Document name without extension
- `reasoning`: Explanation of why this action was chosen
- `confidence`: Confidence score (0.0 to 1.0)

### What Happens When Executed

1. AXON receives the natural language command
2. LLM analyzes the request and returns a `print_document` action
3. `execute_action()` routes to `_print_document()` function
4. The function runs `print_document_automation.py` as a subprocess
5. The automation script:
   - Opens Run dialog (Win+R)
   - Types the full document path
   - Opens the document in Microsoft Word
   - Sends print command (Ctrl+P, Ctrl+P, Enter)
   - Closes Word
6. Document is sent to the default printer

## Testing

### Run the Integration Test

```bash
cd ibm-bob-hackathon/axon
python test_print_integration.py
```

The test will:
1. Verify the action is recognized (dry run)
2. Ask if you want to run the actual print test
3. Execute the print automation if confirmed

### Manual Testing with AXON

1. Start AXON: `python main.py`
2. Use the global hotkey to activate AXON
3. Say: "Print KheloParty_Full_Plan"
4. AXON should recognize the request and execute the print action

## Technical Details

### File Modifications

1. **`executor/actions.py`**
   - Added `import subprocess` (line 17)
   - Added `_print_document()` function (lines 290-348)
   - Added print_document handler in `execute_action()` (lines 489-492)

2. **`core/llm.py`**
   - Updated action list in system instruction (line 250)
   - Added task rule for printing (line 241)

3. **New Files**
   - `test_print_integration.py` - Integration test script

### Error Handling

The integration includes comprehensive error handling:

- **Script Not Found**: Logs error if `print_document_automation.py` is missing
- **Timeout**: 60-second timeout prevents hanging
- **User Abort**: Detects FAILSAFE abort (exit code 2)
- **Execution Errors**: Captures and logs stderr output
- **Subprocess Errors**: Handles subprocess exceptions gracefully

### Logging

All print actions are logged to:
- Console output (INFO level)
- `session_log.json` (with timestamp and execution details)

## Limitations

1. **Document Location**: Currently hardcoded to `C:\Users\admin\Documents\KheloParty_Full_Plan.docx`
2. **Single Document**: The automation script is configured for one specific document
3. **Windows Only**: Uses Windows-specific commands (Win+R, Ctrl+P)
4. **Microsoft Word Required**: Document must be a Word file (.docx)
5. **Default Printer**: Prints to the system's default printer

## Future Enhancements

Potential improvements for future versions:

1. **Dynamic Document Path**: Accept full file paths from user
2. **Document Search**: Search for documents by name in common locations
3. **Multiple Formats**: Support PDF, Excel, PowerPoint, etc.
4. **Printer Selection**: Allow user to specify which printer to use
5. **Print Options**: Support page range, copies, color/BW, etc.
6. **Cross-Platform**: Add support for macOS and Linux

## Example Usage Scenarios

### Scenario 1: Simple Print Request
```
User: "Print KheloParty_Full_Plan"
AXON: [Executes print_document action]
Result: Document opens in Word and prints
```

### Scenario 2: Print with Context
```
User: "Open KheloParty_Full_Plan and print it to my printer"
AXON: [Recognizes print intent, executes print_document action]
Result: Document opens in Word and prints
```

### Scenario 3: Implicit Print Request
```
User: "I need a hard copy of KheloParty_Full_Plan"
AXON: [LLM interprets as print request, executes print_document action]
Result: Document opens in Word and prints
```

## Troubleshooting

### Issue: Action Not Recognized
**Solution**: Check that `core/llm.py` includes the print_document action in the system instruction

### Issue: Script Not Found
**Solution**: Verify `print_document_automation.py` exists in the axon directory

### Issue: Document Not Found
**Solution**: Ensure the document exists at `C:\Users\admin\Documents\KheloParty_Full_Plan.docx`

### Issue: Word Doesn't Open
**Solution**: 
- Check that Microsoft Word is installed
- Verify the document path is correct
- Try running `print_document_automation.py` directly to debug

### Issue: Print Command Fails
**Solution**:
- Ensure a printer is configured as default
- Check printer is online and has paper
- Verify Word print dialog settings

## Code Examples

### Adding a New Document

To support printing different documents, modify `_print_document()`:

```python
def _print_document(document_name=None):
    """Execute the print document automation script."""
    try:
        import subprocess
        
        script_dir = Path(__file__).parent.parent
        script_path = script_dir / "print_document_automation.py"
        
        # Build command with document name
        cmd = [sys.executable, str(script_path)]
        if document_name:
            cmd.extend(["--document", document_name])
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        return result.returncode == 0
        
    except Exception as e:
        logger.error(f"Error executing print automation: {e}")
        return False
```

### Custom Print Settings

To add print options, extend the action dictionary:

```json
{
  "action": "print_document",
  "text": "KheloParty_Full_Plan",
  "options": {
    "copies": 2,
    "color": false,
    "pages": "1-5"
  },
  "reasoning": "Print first 5 pages in black and white, 2 copies",
  "confidence": 0.95
}
```

## Summary

The print document integration is now fully functional and allows users to print documents using natural language commands. The system is extensible and can be enhanced to support more document types, printers, and print options in the future.

---

**Integration Date**: 2026-05-17  
**Version**: 1.0  
**Status**: ✅ Complete and Tested