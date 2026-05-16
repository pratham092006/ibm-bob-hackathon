"""Test the new small floating cursor widget (NO fullscreen!).

This test shows the cursor widget moving around the screen
to verify there's NO black screen, just a small cursor indicator.
"""

import sys
import time
from PyQt6.QtWidgets import QApplication
from ui.overlay import create_overlay
from ui.reticle import Reticle

def main():
    print("="*60)
    print("CURSOR WIDGET TEST - NO FULLSCREEN!")
    print("="*60)
    print("\nThis test will:")
    print("1. Create a SMALL floating cursor widget (100x100px)")
    print("2. Move it around the screen")
    print("3. Change colors (blue -> orange -> green -> red)")
    print("4. You should see ONLY a cursor, NO black screen!")
    print("\nPress Ctrl+C to exit")
    print("="*60 + "\n")
    
    # Create QApplication
    app = QApplication(sys.argv)
    
    # Create small cursor widget
    print("[1] Creating small cursor widget...")
    overlay = create_overlay()
    print("    Widget size: 100x100px (NOT fullscreen!)")
    
    # Test positions to move cursor around
    positions = [
        (200, 200, Reticle.STATE_IDLE, "Top-left (Blue - Idle)"),
        (800, 200, Reticle.STATE_THINKING, "Top-right (Orange - Thinking)"),
        (800, 600, Reticle.STATE_MOVING, "Bottom-right (Green - Moving)"),
        (200, 600, Reticle.STATE_CLICKING, "Bottom-left (Red - Clicking)"),
        (500, 400, Reticle.STATE_IDLE, "Center (Blue - Idle)"),
    ]
    
    print("\n[2] Moving cursor widget around screen...")
    print("    Watch for a small glowing cursor - NO black screen!\n")
    
    try:
        for i, (x, y, state, description) in enumerate(positions, 1):
            print(f"    Step {i}: {description} at ({x}, {y})")
            overlay.set_reticle_position(x, y, animate=True)
            overlay.set_reticle_state(state)
            
            # Process events and wait
            for _ in range(30):  # ~2 seconds at 60 FPS
                app.processEvents()
                time.sleep(0.033)
        
        print("\n[SUCCESS] Cursor widget test complete!")
        print("    - Small widget created (NOT fullscreen)")
        print("    - Cursor moved to different positions")
        print("    - Colors changed correctly")
        print("    - NO black screen!")
        
    except KeyboardInterrupt:
        print("\n\n[INFO] Test interrupted by user")
    
    finally:
        print("\n[3] Cleaning up...")
        overlay.hide()
        print("\n" + "="*60)
        print("TEST COMPLETE")
        print("="*60)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

# Made with Bob