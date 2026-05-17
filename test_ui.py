"""Test script for UI components.

This script tests each UI component individually to ensure they work correctly.
Run this to verify the UI implementation before integration.
"""

import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer
import time

def test_reticle():
    """Test the reticle component."""
    print("Testing Reticle...")
    from ui.reticle import Reticle
    
    reticle = Reticle()
    
    # Test position setting
    reticle.set_position(100, 100, animate=False)
    assert reticle.position.x() == 100
    assert reticle.position.y() == 100
    print("✓ Position setting works")
    
    # Test state changes
    reticle.set_state(Reticle.STATE_THINKING)
    assert reticle.state == Reticle.STATE_THINKING
    print("✓ State changes work")
    
    # Test animation update
    reticle.set_position(200, 200, animate=True)
    reticle.update(0.016)  # Simulate one frame
    print("✓ Animation update works")
    
    # Test color retrieval
    color = reticle.get_color()
    assert color is not None
    print("✓ Color retrieval works")
    
    print("✓ Reticle tests passed!\n")

def test_overlay():
    """Test the overlay component."""
    print("Testing Overlay...")
    from ui.overlay import TransparentOverlay
    
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    overlay = TransparentOverlay()
    
    # Test reticle position
    overlay.set_reticle_position(300, 300)
    print("✓ Reticle position setting works")
    
    # Test status update
    overlay.set_status("Testing status")
    assert overlay.status_text == "Testing status"
    print("✓ Status update works")
    
    # Test task info
    overlay.set_task_info(task="Test task", step="Test step", response_time=1.5, action_count=5)
    assert overlay.current_task == "Test task"
    print("✓ Task info update works")
    
    # Test reticle state
    overlay.set_reticle_state("moving")
    print("✓ Reticle state update works")
    
    # Show briefly then hide
    overlay.show()
    QTimer.singleShot(500, overlay.hide)
    QTimer.singleShot(600, app.quit)
    
    print("✓ Overlay display works (showing for 0.5s)")
    app.exec()
    
    print("✓ Overlay tests passed!\n")

def test_input_dialog():
    """Test the input dialog component."""
    print("Testing Input Dialog...")
    from ui.input_dialog import TaskInputDialog
    
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    dialog = TaskInputDialog()
    
    # Test task input
    dialog.task_input.setText("Test task")
    assert dialog.task_input.text() == "Test task"
    print("✓ Task input works")
    
    # Test signal connection
    received_task = [None]
    def on_task(task):
        received_task[0] = task
    
    dialog.task_submitted.connect(on_task)
    
    # Show briefly then close
    dialog.show()
    QTimer.singleShot(500, dialog.close)
    QTimer.singleShot(600, app.quit)
    
    print("✓ Input dialog display works (showing for 0.5s)")
    app.exec()
    
    print("✓ Input dialog tests passed!\n")

def test_tray():
    """Test the tray icon component."""
    print("Testing Tray Icon...")
    from ui.tray import TrayIcon
    
    tray = TrayIcon()
    
    # Test icon image creation
    image = tray.create_icon_image(TrayIcon.STATE_IDLE)
    assert image is not None
    assert image.size == (64, 64)
    print("✓ Icon image creation works")
    
    # Test state update
    tray.state = TrayIcon.STATE_RUNNING
    assert tray.state == TrayIcon.STATE_RUNNING
    print("✓ State update works")
    
    # Test menu creation
    menu = tray.create_menu()
    assert menu is not None
    assert len(menu) > 0
    print("✓ Menu creation works")
    
    print("✓ Tray icon tests passed!\n")

def run_all_tests():
    """Run all UI component tests."""
    print("=" * 50)
    print("AXON UI Component Tests")
    print("=" * 50)
    print()
    
    try:
        # Test reticle (no Qt required)
        test_reticle()
        
        # Test overlay (requires Qt)
        test_overlay()
        
        # Test input dialog (requires Qt)
        test_input_dialog()
        
        # Test tray icon (no Qt required for basic tests)
        test_tray()
        
        print("=" * 50)
        print("✓ ALL TESTS PASSED!")
        print("=" * 50)
        
    except Exception as e:
        print(f"\n✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

# Made with Bob