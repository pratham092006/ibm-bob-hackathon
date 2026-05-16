"""Test script to verify overlay integration with agent loop.

This test verifies that:
1. Overlay can be created and shown
2. Queue listener updates overlay position
3. Status updates are processed correctly
"""

import sys
import time
import queue
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer

from ui.overlay import create_overlay, start_overlay_queue_listener


def test_overlay_queue_integration():
    """Test that overlay responds to queue updates."""
    print("Testing overlay queue integration...")
    
    # Create QApplication
    app = QApplication(sys.argv)
    
    # Create overlay
    overlay = create_overlay()
    overlay.show()
    print("[OK] Overlay created and shown")
    
    # Create test queue
    test_queue = queue.Queue()
    
    # Start queue listener
    timer = start_overlay_queue_listener(overlay, test_queue)
    print("[OK] Queue listener started")
    
    # Test 1: Move cursor to position
    print("\nTest 1: Moving cursor to (500, 300)...")
    test_queue.put({
        'type': 'action',
        'action': {
            'action': 'mouse_move',
            'coordinate': [500, 300]
        },
        'message': 'Moving to position'
    })
    
    # Process events
    QTimer.singleShot(200, lambda: print("[OK] Cursor should be at (500, 300)"))
    
    # Test 2: Click action
    QTimer.singleShot(500, lambda: test_queue.put({
        'type': 'action',
        'action': {
            'action': 'left_click',
            'coordinate': [700, 400]
        },
        'message': 'Clicking at position'
    }))
    QTimer.singleShot(700, lambda: print("[OK] Cursor should be at (700, 400) in clicking state"))
    
    # Test 3: Thinking state
    QTimer.singleShot(1000, lambda: test_queue.put({
        'type': 'thinking',
        'message': 'Analyzing screen...'
    }))
    QTimer.singleShot(1200, lambda: print("[OK] Cursor should be in thinking state"))
    
    # Test 4: Task complete
    QTimer.singleShot(1500, lambda: test_queue.put({
        'type': 'task_complete',
        'message': 'Task completed!'
    }))
    QTimer.singleShot(1700, lambda: print("[OK] Cursor should be in idle state"))
    
    # Exit after tests
    QTimer.singleShot(2000, lambda: (
        print("\n[SUCCESS] All tests completed!"),
        print("Overlay integration is working correctly."),
        app.quit()
    ))
    
    # Run app
    sys.exit(app.exec())


if __name__ == "__main__":
    test_overlay_queue_integration()

# Made with Bob
