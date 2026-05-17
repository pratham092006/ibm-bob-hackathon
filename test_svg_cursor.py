"""Test script for SVG cursor implementation.

This script creates a simple window to test the SVG-based pointing hand cursor.
"""

import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt, QTimer, QPoint
from PyQt6.QtGui import QCursor
from ui.reticle import Reticle
from ui.overlay import TransparentOverlay


def test_svg_cursor():
    """Test the SVG cursor implementation."""
    print("Testing SVG Cursor Implementation")
    print("=" * 50)
    
    # Create Qt application
    app = QApplication(sys.argv)
    
    # Create overlay with SVG cursor
    print("\n1. Creating overlay with SVG cursor...")
    overlay = TransparentOverlay()
    
    # Show overlay
    overlay.show()
    overlay.show_reticle()
    
    # Position cursor at center of screen
    import pyautogui
    screen_width, screen_height = pyautogui.size()
    center_x = screen_width // 2
    center_y = screen_height // 2
    
    print(f"2. Positioning cursor at screen center ({center_x}, {center_y})...")
    overlay.set_reticle_position(center_x, center_y, animate=False)
    
    # Create a simple control window
    control_window = QWidget()
    control_window.setWindowTitle("SVG Cursor Test - Control Panel")
    control_window.setGeometry(100, 100, 400, 200)
    
    layout = QVBoxLayout()
    
    info_label = QLabel(
        "SVG Cursor Test Running\n\n"
        "The AI cursor should be visible at the center of your screen.\n"
        "It should display a pointing hand from the SVG file.\n\n"
        "Move your mouse - the AI cursor will follow with an offset.\n\n"
        "Close this window to exit the test."
    )
    info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    layout.addWidget(info_label)
    
    control_window.setLayout(layout)
    control_window.show()
    
    print("3. Test window created")
    print("\nTest Instructions:")
    print("- The AI cursor should appear at screen center")
    print("- It should show the pointing hand from pointinghand.svg")
    print("- Move your mouse to see the cursor follow with offset")
    print("- Close the control window to exit")
    print("\nIf you see a simple circle instead of a hand:")
    print("- The SVG file may not have loaded correctly")
    print("- Check the console for error messages")
    print("- Ensure PyQt6-SVG is installed: pip install PyQt6-SVG")
    
    # Run application
    sys.exit(app.exec())


if __name__ == "__main__":
    test_svg_cursor()

# Made with Bob
