"""Test script for custom AI cursor with coordinate tracking.

This script demonstrates the new hand cursor implementation:
- Simple hand cursor icon (solid black, no glowing effects)
- Real-time coordinate display (X, Y)
- Follows main mouse cursor at a slight offset
- Always visible and tracks coordinates
"""

import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer
from ui.overlay import TransparentOverlay


def main():
    """Test the custom AI cursor."""
    print("=" * 60)
    print("Custom AI Cursor Test")
    print("=" * 60)
    print("\nFeatures:")
    print("- Simple hand cursor icon (solid black)")
    print("- Real-time coordinate display")
    print("- Follows your mouse at a slight offset (25px right, 25px down)")
    print("- No glowing effects or animations")
    print("\nInstructions:")
    print("1. Move your mouse around the screen")
    print("2. The AI cursor should follow at a slight offset")
    print("3. Coordinates should update in real-time")
    print("4. Press Ctrl+C in terminal to exit")
    print("=" * 60)
    
    # Create Qt application
    app = QApplication(sys.argv)
    
    # Create overlay with custom cursor
    overlay = TransparentOverlay()
    
    # Show the overlay
    overlay.show_reticle()
    overlay.show()
    
    print("\n[OK] Custom AI cursor is now active!")
    print("[OK] Move your mouse to see the cursor follow with coordinates")
    print("\nPress Ctrl+C to exit...\n")
    
    # Run the application
    sys.exit(app.exec())


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[OK] Test completed. Cursor stopped.")
        sys.exit(0)

# Made with Bob
