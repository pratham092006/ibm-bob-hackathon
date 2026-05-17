"""Test script for global hotkey feature.

This script tests the Alt+G global hotkey functionality including:
1. Task dialog mode (no text selected)
2. Context help mode (text selected)
"""

import sys
import time
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer

# Import the modules we need to test
from executor.global_hotkey import GlobalHotkey
from ui.answer_overlay import AnswerOverlay
from ui.input_dialog import TaskInputDialog


def test_task_dialog_mode():
    """Test Alt+G without text selection - should open task dialog."""
    print("\n" + "="*60)
    print("TEST 1: Task Dialog Mode (Alt+G without text selection)")
    print("="*60)
    print("\nInstructions:")
    print("1. Press Alt+G (without selecting any text)")
    print("2. The task input dialog should appear")
    print("3. Close the dialog to continue")
    print("\nWaiting for Alt+G...")
    
    app = QApplication.instance() or QApplication(sys.argv)
    
    dialog = TaskInputDialog()
    dialog_shown = [False]
    
    def on_task_dialog():
        print("\n✓ Task dialog callback triggered!")
        dialog_shown[0] = True
        dialog.show()
        dialog.raise_()
        dialog.activateWindow()
    
    def on_context_help(text):
        print(f"\n✗ ERROR: Context help triggered instead! Text: {text[:50]}")
    
    # Create hotkey listener
    hotkey = GlobalHotkey(on_task_dialog, on_context_help)
    hotkey.start()
    
    # Wait for user to press Alt+G
    def check_result():
        if dialog_shown[0]:
            print("\n✓ TEST 1 PASSED: Task dialog mode works!")
            app.quit()
        else:
            # Keep waiting
            QTimer.singleShot(1000, check_result)
    
    QTimer.singleShot(1000, check_result)
    
    # Run for 30 seconds max
    QTimer.singleShot(30000, lambda: (
        print("\n✗ TEST 1 TIMEOUT: Alt+G not pressed within 30 seconds"),
        app.quit()
    ))
    
    app.exec()
    hotkey.stop()


def test_context_help_mode():
    """Test Alt+G with text selection - should show context help."""
    print("\n" + "="*60)
    print("TEST 2: Context Help Mode (Alt+G with text selection)")
    print("="*60)
    print("\nInstructions:")
    print("1. Open Notepad or any text editor")
    print("2. Type some text (e.g., 'Python programming language')")
    print("3. Select the text")
    print("4. Press Alt+G")
    print("5. The answer overlay should appear with AI help")
    print("\nWaiting for Alt+G with selected text...")
    
    app = QApplication.instance() or QApplication(sys.argv)
    
    overlay = AnswerOverlay()
    help_shown = [False]
    
    def on_task_dialog():
        print("\n✗ ERROR: Task dialog triggered instead!")
    
    def on_context_help(text):
        print(f"\n✓ Context help callback triggered!")
        print(f"Selected text: '{text[:100]}...'")
        help_shown[0] = True
        
        # Show overlay with mock response
        mock_response = f"""**Selected Text Analysis**

You selected: "{text[:100]}..."

This is a test response. In production, this would be an AI-generated explanation about the selected text.

**Key Points:**
- Text length: {len(text)} characters
- First word: {text.split()[0] if text.split() else 'N/A'}
- Context help is working correctly!

Click anywhere or press Esc to close."""
        
        overlay.set_answer(mock_response)
    
    # Create hotkey listener
    hotkey = GlobalHotkey(on_task_dialog, on_context_help)
    hotkey.start()
    
    # Wait for user to press Alt+G with text
    def check_result():
        if help_shown[0]:
            print("\n✓ TEST 2 PASSED: Context help mode works!")
            # Keep running to show overlay
            QTimer.singleShot(5000, app.quit)
        else:
            # Keep waiting
            QTimer.singleShot(1000, check_result)
    
    QTimer.singleShot(1000, check_result)
    
    # Run for 60 seconds max
    QTimer.singleShot(60000, lambda: (
        print("\n✗ TEST 2 TIMEOUT: Alt+G with text not pressed within 60 seconds"),
        app.quit()
    ))
    
    app.exec()
    hotkey.stop()


def test_text_selection_detection():
    """Test the text selection detection mechanism."""
    print("\n" + "="*60)
    print("TEST 3: Text Selection Detection")
    print("="*60)
    
    from executor.global_hotkey import GlobalHotkey
    
    hotkey = GlobalHotkey(lambda: None, lambda x: None)
    
    print("\nTest 3a: No text selected")
    result = hotkey._get_selected_text()
    if result is None:
        print("✓ Correctly detected no selection")
    else:
        print(f"✗ ERROR: Got text when none selected: '{result}'")
    
    print("\nTest 3b: With text selected")
    print("Instructions:")
    print("1. Select some text in any application")
    print("2. Press Enter in this console")
    input("Press Enter when text is selected...")
    
    result = hotkey._get_selected_text()
    if result and len(result) > 0:
        print(f"✓ Successfully captured: '{result[:50]}...'")
    else:
        print("✗ ERROR: Failed to capture selected text")
    
    print("\n✓ TEST 3 COMPLETED")


def run_all_tests():
    """Run all tests in sequence."""
    print("\n" + "="*60)
    print("GLOBAL HOTKEY FEATURE TEST SUITE")
    print("="*60)
    print("\nThis will test the Alt+G global hotkey feature.")
    print("Make sure AXON is not already running to avoid conflicts.")
    print("\nPress Ctrl+C to cancel at any time.")
    
    try:
        # Test 3: Text selection detection (non-interactive)
        test_text_selection_detection()
        
        # Test 1: Task dialog mode
        print("\n\nStarting Test 1 in 3 seconds...")
        time.sleep(3)
        test_task_dialog_mode()
        
        # Test 2: Context help mode
        print("\n\nStarting Test 2 in 3 seconds...")
        time.sleep(3)
        test_context_help_mode()
        
        print("\n" + "="*60)
        print("ALL TESTS COMPLETED!")
        print("="*60)
        
    except KeyboardInterrupt:
        print("\n\nTests cancelled by user.")
    except Exception as e:
        print(f"\n\nERROR during testing: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("Global Hotkey Test Script")
    print("=" * 60)
    print("\nOptions:")
    print("1. Run all tests")
    print("2. Test task dialog mode only")
    print("3. Test context help mode only")
    print("4. Test text selection detection only")
    
    choice = input("\nEnter choice (1-4) or press Enter for all tests: ").strip()
    
    if choice == "2":
        test_task_dialog_mode()
    elif choice == "3":
        test_context_help_mode()
    elif choice == "4":
        test_text_selection_detection()
    else:
        run_all_tests()


# Made with Bob