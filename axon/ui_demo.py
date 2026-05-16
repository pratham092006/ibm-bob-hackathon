"""Demo script showing all UI components working together.

This demonstrates the complete UI integration for AXON.
Run this to see the reticle, overlay, input dialog, and tray icon in action.
"""

import sys
import time
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer
from ui import (
    create_overlay,
    show_task_input_dialog,
    create_tray_icon,
    Reticle
)
from config import status_queue


def demo_reticle_animation(overlay):
    """Demonstrate reticle animation through different states."""
    print("Starting reticle animation demo...")
    
    # Sequence of positions and states to demonstrate
    sequence = [
        (100, 100, Reticle.STATE_IDLE, "Idle state"),
        (300, 200, Reticle.STATE_THINKING, "Thinking..."),
        (500, 300, Reticle.STATE_MOVING, "Moving cursor"),
        (700, 400, Reticle.STATE_CLICKING, "Clicking!"),
        (900, 500, Reticle.STATE_MOVING, "Moving again"),
        (500, 300, Reticle.STATE_IDLE, "Back to idle"),
    ]
    
    def animate_step(index):
        if index >= len(sequence):
            print("Animation demo complete!")
            return
        
        x, y, state, description = sequence[index]
        print(f"  Step {index + 1}: {description} at ({x}, {y})")
        
        overlay.set_reticle_position(x, y, animate=True)
        overlay.set_reticle_state(state)
        overlay.set_status(description)
        
        # Schedule next step
        QTimer.singleShot(1500, lambda: animate_step(index + 1))
    
    # Start animation
    animate_step(0)


def demo_status_updates(overlay):
    """Demonstrate status HUD updates."""
    print("Starting status HUD demo...")
    
    updates = [
        ("Open Notepad", "Searching for Notepad", 0.5, 1),
        ("Open Notepad", "Clicking Start menu", 1.2, 2),
        ("Open Notepad", "Typing 'notepad'", 1.8, 3),
        ("Open Notepad", "Pressing Enter", 2.1, 4),
        ("Open Notepad", "Task complete!", 2.5, 5),
    ]
    
    def update_step(index):
        if index >= len(updates):
            print("Status demo complete!")
            return
        
        task, step, response_time, action_count = updates[index]
        print(f"  Update {index + 1}: {step}")
        
        overlay.set_task_info(
            task=task,
            step=step,
            response_time=response_time,
            action_count=action_count
        )
        
        # Schedule next update
        QTimer.singleShot(2000, lambda: update_step(index + 1))
    
    # Start updates after reticle animation
    QTimer.singleShot(10000, lambda: update_step(0))


def run_full_demo():
    """Run the complete UI demo."""
    print("=" * 60)
    print("AXON UI Components Demo")
    print("=" * 60)
    print()
    
    # Create QApplication
    app = QApplication(sys.argv)
    
    # Create overlay
    print("Creating overlay...")
    overlay = create_overlay()
    overlay.show()
    print("✓ Overlay created and shown")
    
    # Create tray icon
    print("Creating tray icon...")
    tray = create_tray_icon(
        overlay=overlay,
        input_dialog_callback=show_task_input_dialog
    )
    print("✓ Tray icon created")
    print()
    
    # Show initial task input dialog
    print("Showing task input dialog...")
    print("(You can type a task or just close it)")
    
    def on_dialog_closed():
        task = show_task_input_dialog()
        if task:
            print(f"✓ Task received: {task}")
            overlay.set_task_info(task=task, step="Starting...", response_time=0.0, action_count=0)
        else:
            print("✓ Dialog closed without task")
        
        # Start demos
        print()
        print("Starting automated demos...")
        print()
        demo_reticle_animation(overlay)
        demo_status_updates(overlay)
        
        # Auto-exit after demos
        QTimer.singleShot(20000, app.quit)
    
    # Show dialog after a short delay
    QTimer.singleShot(500, on_dialog_closed)
    
    print()
    print("=" * 60)
    print("Demo Controls:")
    print("  - Right-click tray icon for menu")
    print("  - Watch the reticle animate across the screen")
    print("  - See status HUD in top-left corner")
    print("  - Demo will auto-exit in 20 seconds")
    print("=" * 60)
    print()
    
    # Run application
    sys.exit(app.exec())


def quick_test():
    """Quick test to verify all components load."""
    print("Running quick component test...")
    
    try:
        from ui.reticle import Reticle
        print("✓ Reticle imported")
        
        from ui.overlay import TransparentOverlay
        print("✓ Overlay imported")
        
        from ui.input_dialog import TaskInputDialog
        print("✓ Input dialog imported")
        
        from ui.tray import TrayIcon
        print("✓ Tray icon imported")
        
        print()
        print("✓ All components loaded successfully!")
        return True
    except Exception as e:
        print(f"✗ Error loading components: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    # Check if we should run quick test or full demo
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        success = quick_test()
        sys.exit(0 if success else 1)
    else:
        run_full_demo()

# Made with Bob