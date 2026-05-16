"""AXON - Live AI Desktop Agent
Complete integration of all modules.
"""
import sys
import threading
import queue
from typing import Optional, Any
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer

# Import all modules
from ui.overlay import TransparentOverlay
from ui.input_dialog import TaskInputDialog
from ui.tray import TrayIcon
from core.loop import start_monitoring, activate_agent
from executor.kill_switch import start_kill_switch, KillSwitch
from config import kill_event, ui_queue


class AxonApplication:
    """Main AXON application class."""
    
    def __init__(self):
        """Initialize the AXON application."""
        self.app: Optional[QApplication] = None
        self.overlay: Optional[TransparentOverlay] = None
        self.input_dialog: Optional[TaskInputDialog] = None
        self.tray: Optional[TrayIcon] = None
        self.monitor_thread: Optional[threading.Thread] = None
        self.status_timer: Optional[QTimer] = None
        self.task_active: bool = False
        self.kill_switch: Optional[KillSwitch] = None
        
    def initialize(self):
        """Initialize all components."""
        print("AXON - Live AI Desktop Agent")
        print("Initializing...")
        
        # Start kill switch first (emergency stop functionality)
        print("Starting kill switch...")
        self.kill_switch = start_kill_switch()
        if self.kill_switch:
            print("Kill switch active - Press F12 for emergency stop")
        else:
            print("WARNING: Kill switch failed to start")
        
        # Create Qt application
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)
        
        # Initialize UI components
        print("Creating UI components...")
        self.overlay = TransparentOverlay()
        self.input_dialog = TaskInputDialog()
        
        # Connect signals
        self.input_dialog.task_submitted.connect(self.on_task_submitted)
        
        # Create tray icon with callbacks
        print("Creating system tray...")
        self.tray = TrayIcon(
            overlay=self.overlay,
            input_dialog_callback=self.show_input_dialog
        )
        
        # Start monitoring loop in background thread
        print("Starting monitoring thread...")
        self.monitor_thread = threading.Thread(target=start_monitoring, daemon=True)
        self.monitor_thread.start()
        
        # Set up status update timer - reads from ui_queue (dedicated for overlay)
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_status)
        self.status_timer.start(50)  # Check every 50ms for smoother cursor updates
        
        print("Initialization complete!")
        
    def on_task_submitted(self, task):
        """Handle task submission from input dialog.
        
        Args:
            task (str): User's task description
        """
        print(f"\n{'='*60}")
        print(f"[MAIN] Task submitted: {task}")
        print(f"{'='*60}\n")
        
        # Show the AI cursor overlay when task starts
        print("[MAIN] Showing AI cursor overlay...")
        self.task_active = True
        self.overlay.show()  # type: ignore
        self.overlay.show_reticle()  # type: ignore
        
        # Set initial position at center of screen
        import pyautogui
        screen_width, screen_height = pyautogui.size()
        self.overlay.set_reticle_position(screen_width // 2, screen_height // 2)  # type: ignore
        self.overlay.set_status("Starting task...")  # type: ignore
        print(f"[MAIN] Overlay shown at center ({screen_width//2}, {screen_height//2})")
        
        # Activate the agent with the task
        print("[MAIN] Activating agent...")
        activate_agent(task)
        print("[MAIN] Agent activated\n")
        
    def show_input_dialog(self):
        """Show the input dialog and return the task.
        
        Returns:
            str: User's task or None if cancelled
        """
        # Store result
        result = [None]
        
        def on_task(task):
            result[0] = task
        
        # Connect signal temporarily
        self.input_dialog.task_submitted.connect(on_task)  # type: ignore
        
        # Show dialog
        self.input_dialog.show()  # type: ignore
        self.input_dialog.exec()  # type: ignore
        
        # Disconnect signal
        self.input_dialog.task_submitted.disconnect(on_task)  # type: ignore
        
        return result[0]
        
    def update_status(self):
        """Update UI based on ui_queue (dedicated overlay queue)."""
        try:
            while not ui_queue.empty():
                try:
                    status = ui_queue.get_nowait()
                except queue.Empty:
                    break
                
                if not isinstance(status, dict):
                    continue
                
                status_type = status.get('type', '')
                message = status.get('message', '')
                
                # Update overlay status text
                if message:
                    self.overlay.set_status(message)  # type: ignore
                
                # Update task info if available
                if 'task' in status:
                    task = status.get('task', '')
                    action_count = status.get('action_count', 0)
                    response_time = status.get('response_time', 0.0)
                    self.overlay.set_task_info(  # type: ignore
                        task=task,
                        step=message,
                        response_time=response_time,
                        action_count=action_count
                    )
                
                # Update reticle based on action
                if status_type == 'action':
                    action = status.get('action', {})
                    action_type = action.get('action', '')
                    
                    # Set reticle state
                    if action_type in ['click', 'left_click', 'right_click', 'double_click']:
                        self.overlay.set_reticle_state('clicking')  # type: ignore
                    elif action_type == 'mouse_move':
                        self.overlay.set_reticle_state('moving')  # type: ignore
                    elif action_type in ['type', 'key']:
                        self.overlay.set_reticle_state('idle')  # type: ignore
                    
                    # Move reticle to coordinates if available
                    if 'coordinate' in action:
                        coord = action['coordinate']
                        if isinstance(coord, (list, tuple)) and len(coord) == 2:
                            self.overlay.set_reticle_position(coord[0], coord[1])  # type: ignore
                    elif 'x' in action and 'y' in action:
                        self.overlay.set_reticle_position(action['x'], action['y'])  # type: ignore
                
                elif status_type == 'thinking':
                    self.overlay.set_reticle_state('thinking')  # type: ignore
                    self.overlay.set_status("🤔 Thinking...")  # type: ignore
                
                elif status_type == 'task_start':
                    self.task_active = True
                    self.overlay.show()  # type: ignore
                    self.overlay.show_reticle()  # type: ignore
                    self.overlay.set_status("🚀 Starting...")  # type: ignore
                
                elif status_type == 'task_complete':
                    self.overlay.set_reticle_state('idle')  # type: ignore
                    self.overlay.set_status("✅ Done!")  # type: ignore
                    self.task_active = False
                    # Hide after 3 seconds
                    QTimer.singleShot(3000, self._hide_overlay_if_idle)
                
                elif status_type == 'error':
                    self.overlay.set_reticle_state('idle')  # type: ignore
                    self.overlay.set_status(f"❌ Error: {message[:50]}")  # type: ignore
                    self.task_active = False
                    QTimer.singleShot(5000, self._hide_overlay_if_idle)
                
                elif status_type == 'stopped':
                    self.overlay.set_reticle_state('idle')  # type: ignore
                    self.overlay.set_status("⏹ Stopped")  # type: ignore
                    self.task_active = False
                    QTimer.singleShot(3000, self._hide_overlay_if_idle)
                    
        except Exception as e:
            print(f"Error updating status: {e}")
    
    def _hide_overlay_if_idle(self):
        """Hide overlay only if no task is active."""
        if not self.task_active:
            self.overlay.hide_reticle()  # type: ignore
    
    def run(self):
        """Run the application."""
        # Show UI components
        print("Showing UI...")
        
        # HIDE overlay initially - only show when task starts
        self.overlay.hide()  # type: ignore
        
        # Show input dialog to get task
        self.input_dialog.show()  # type: ignore
        
        # Start system tray
        self.tray.start()  # type: ignore
        
        print("\nAXON is ready!")
        print("- Enter a task in the dialog to start")
        print("- AI cursor will appear when task begins")
        print("- Press F12 for emergency stop")
        print("- Use the system tray icon for controls")
        print()
        
        # Run application event loop
        sys.exit(self.app.exec())  # type: ignore


def main():
    """Main entry point."""
    try:
        # Create and initialize application
        axon = AxonApplication()
        axon.initialize()
        
        # Run the application
        axon.run()
        
    except KeyboardInterrupt:
        print("\nShutting down AXON...")
        kill_event.set()
        sys.exit(0)
    except Exception as e:
        print(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

# Made with Bob
