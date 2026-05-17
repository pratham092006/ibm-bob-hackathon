r"""
Document Printing Automation Script
====================================
This script automates the process of printing a Word document using PyAutoGUI.

Target Document: KheloParty_Full_Plan.docx
Search Location: C:\Users\admin\Documents

Workflow:
1. Uses Win+R (Run dialog) to directly open the document with full path
2. Waits 8 seconds for Word to fully open
3. Prints using Ctrl+P, Ctrl+P, Enter sequence

This approach is more reliable than File Explorer search because:
- Directly opens the file using the full path
- No dependency on search results loading
- No focus management issues with search boxes
- Faster execution

Fallback methods available if primary method fails:
- Method 2: File Explorer with double-click
- Method 3: File Explorer with Enter key (twice)

Requirements:
- pyautogui
- Microsoft Word installed

Usage:
    python print_document_automation.py
"""

import pyautogui
import time
import os
import sys

# Enable fail-safe feature (move mouse to corner to abort)
pyautogui.FAILSAFE = True

# Configuration
DOCUMENT_NAME = "KheloParty_Full_Plan.docx"
SEARCH_DIRECTORY = r"C:\Users\admin\Documents"
FULL_DOCUMENT_PATH = os.path.join(SEARCH_DIRECTORY, DOCUMENT_NAME)

# Timing constants (in seconds)
WAIT_SHORT = 1
WAIT_MEDIUM = 2
WAIT_LONG = 3
WAIT_RUN_DIALOG = 0.5  # Wait for Run dialog to open
WAIT_WORD_OPEN = 8  # Wait for Word to fully open
WAIT_PRINT_DIALOG = 2

# Method selection (1=Win+R, 2=Double-click, 3=Enter key twice)
OPEN_METHOD = 1


def log_step(message):
    """Print a timestamped log message."""
    timestamp = time.strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")


def wait_and_log(seconds, action):
    """Wait for specified seconds and log the action."""
    log_step(f"{action} (waiting {seconds}s)")
    time.sleep(seconds)


def check_prerequisites():
    """Check if the document exists in the specified directory."""
    log_step("Checking prerequisites...")
    
    if not os.path.exists(SEARCH_DIRECTORY):
        log_step(f"ERROR: Directory not found: {SEARCH_DIRECTORY}")
        return False
    
    document_path = os.path.join(SEARCH_DIRECTORY, DOCUMENT_NAME)
    if not os.path.exists(document_path):
        log_step(f"WARNING: Document not found at: {document_path}")
        log_step("Script will attempt to open it anyway...")
    else:
        log_step(f"Document found: {document_path}")
    
    return True


def open_document_method_1_run_dialog():
    """
    Method 1: Open document using Win+R (Run dialog) - MOST RELIABLE
    
    This method directly opens the document using the full file path,
    bypassing File Explorer search entirely.
    """
    log_step("Method 1: Using Win+R (Run dialog)...")
    
    # Open Run dialog
    log_step("Opening Run dialog (Win+R)...")
    pyautogui.hotkey('win', 'r')
    time.sleep(WAIT_RUN_DIALOG)
    
    # Type the full document path
    log_step(f"Typing document path: {FULL_DOCUMENT_PATH}")
    pyautogui.write(FULL_DOCUMENT_PATH, interval=0.02)
    time.sleep(WAIT_SHORT)
    
    # Press Enter to open
    log_step("Pressing Enter to open document...")
    pyautogui.press('enter')
    wait_and_log(WAIT_WORD_OPEN, "Waiting for Microsoft Word to fully open")


def open_document_method_2_double_click():
    """
    Method 2: Open document using File Explorer with double-click
    
    This method navigates to the folder and double-clicks the file.
    """
    log_step("Method 2: Using File Explorer with double-click...")
    
    # Open File Explorer
    log_step("Opening File Explorer...")
    pyautogui.hotkey('win', 'e')
    time.sleep(WAIT_MEDIUM)
    
    # Navigate to Documents folder
    log_step("Navigating to Documents folder...")
    pyautogui.hotkey('alt', 'd')
    time.sleep(WAIT_SHORT)
    pyautogui.write(SEARCH_DIRECTORY, interval=0.05)
    pyautogui.press('enter')
    time.sleep(WAIT_MEDIUM)
    
    # Search for document
    log_step(f"Searching for '{DOCUMENT_NAME}'...")
    pyautogui.hotkey('ctrl', 'f')
    time.sleep(WAIT_SHORT)
    pyautogui.write(DOCUMENT_NAME, interval=0.05)
    time.sleep(WAIT_LONG)
    
    # Move focus to first result
    log_step("Moving focus to first search result...")
    pyautogui.press('down')
    time.sleep(WAIT_SHORT)
    
    # Double-click to open
    log_step("Double-clicking to open document...")
    pyautogui.doubleClick()
    wait_and_log(WAIT_WORD_OPEN, "Waiting for Microsoft Word to fully open")


def open_document_method_3_enter_twice():
    """
    Method 3: Open document using File Explorer with Enter key (twice)
    
    This method tries pressing Enter twice quickly.
    """
    log_step("Method 3: Using File Explorer with Enter key (twice)...")
    
    # Open File Explorer
    log_step("Opening File Explorer...")
    pyautogui.hotkey('win', 'e')
    time.sleep(WAIT_MEDIUM)
    
    # Navigate to Documents folder
    log_step("Navigating to Documents folder...")
    pyautogui.hotkey('alt', 'd')
    time.sleep(WAIT_SHORT)
    pyautogui.write(SEARCH_DIRECTORY, interval=0.05)
    pyautogui.press('enter')
    time.sleep(WAIT_MEDIUM)
    
    # Search for document
    log_step(f"Searching for '{DOCUMENT_NAME}'...")
    pyautogui.hotkey('ctrl', 'f')
    time.sleep(WAIT_SHORT)
    pyautogui.write(DOCUMENT_NAME, interval=0.05)
    time.sleep(WAIT_LONG)
    
    # Move focus to first result
    log_step("Moving focus to first search result...")
    pyautogui.press('down')
    time.sleep(WAIT_SHORT)
    
    # Press Enter twice quickly
    log_step("Pressing Enter twice to open document...")
    pyautogui.press('enter')
    time.sleep(0.2)
    pyautogui.press('enter')
    wait_and_log(WAIT_WORD_OPEN, "Waiting for Microsoft Word to fully open")


def open_document_in_word():
    """
    Open the document in Microsoft Word using the selected method.
    
    Method 1 (Win+R) is the most reliable and is used by default.
    """
    if OPEN_METHOD == 1:
        open_document_method_1_run_dialog()
    elif OPEN_METHOD == 2:
        open_document_method_2_double_click()
    elif OPEN_METHOD == 3:
        open_document_method_3_enter_twice()
    else:
        log_step(f"ERROR: Invalid OPEN_METHOD: {OPEN_METHOD}")
        raise ValueError(f"Invalid OPEN_METHOD: {OPEN_METHOD}. Must be 1, 2, or 3.")


def print_document():
    """Print the document using simplified Ctrl+P workflow."""
    log_step("Initiating print...")
    
    # First Ctrl+P - opens print dialog
    log_step("Pressing Ctrl+P (first time - opens print dialog)...")
    pyautogui.hotkey('ctrl', 'p')
    time.sleep(WAIT_PRINT_DIALOG)
    
    # Second Ctrl+P
    log_step("Pressing Ctrl+P (second time)...")
    pyautogui.hotkey('ctrl', 'p')
    time.sleep(WAIT_SHORT)
    
    # Press Enter to confirm and print
    log_step("Pressing Enter to confirm and print...")
    pyautogui.press('enter')
    wait_and_log(WAIT_MEDIUM, "Print command sent")


def close_word():
    """Close Microsoft Word."""
    log_step("Closing Microsoft Word...")
    pyautogui.hotkey('alt', 'f4')
    time.sleep(WAIT_SHORT)


def main():
    """Main automation workflow."""
    print("=" * 60)
    print("Document Printing Automation Script")
    print("=" * 60)
    print(f"Target Document: {DOCUMENT_NAME}")
    print(f"Search Location: {SEARCH_DIRECTORY}")
    print(f"Full Path: {FULL_DOCUMENT_PATH}")
    print(f"Opening Method: {OPEN_METHOD} (1=Win+R, 2=Double-click, 3=Enter twice)")
    print("=" * 60)
    print("\nIMPORTANT: Move mouse to any corner to abort (FAILSAFE)")
    print("Starting in 3 seconds...\n")
    time.sleep(3)
    
    try:
        # Check prerequisites
        if not check_prerequisites():
            log_step("Prerequisites check failed. Exiting...")
            return 1
        
        log_step(f"Using Method {OPEN_METHOD} to open document")
        
        # Step 1: Open document in Word (using selected method)
        open_document_in_word()
        
        # Step 2: Print the document
        print_document()
        
        # Step 3: Close Word
        close_word()
        
        print("\n" + "=" * 60)
        log_step("Automation completed successfully!")
        print("=" * 60)
        print(f"\nDocument has been sent to the printer")
        
        return 0
        
    except pyautogui.FailSafeException:
        print("\n" + "=" * 60)
        log_step("FAILSAFE TRIGGERED - Mouse moved to corner")
        log_step("Automation aborted by user")
        print("=" * 60)
        return 2
        
    except Exception as e:
        print("\n" + "=" * 60)
        log_step(f"ERROR: An unexpected error occurred: {str(e)}")
        print("=" * 60)
        import traceback
        traceback.print_exc()
        return 3


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

# Made with Bob
