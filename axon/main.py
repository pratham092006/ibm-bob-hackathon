"""AXON - Live AI Desktop Agent
Complete integration of all modules.
"""
import sys
import threading
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer

# Import all modules
from ui.overlay import TransparentOverlay
from ui.input_dialog import TaskInputDialog
from ui.answer_overlay import AnswerOverlay
from ui.tray import TrayIcon
from core.loop import start_monitoring, activate_agent
from core.context_help import get_context_help
from executor.global_hotkey import start_global_hotkey, stop_global_hotkey
from config import kill_event, ui_queue


class AxonApplication:
    """Main AXON application class."""
    
    def __init__(self):
        """Initialize the AXON application."""
        self.app = None
        self.overlay = None
        self.input_dialog = None
        self.answer_overlay = None
        self.tray = None
        self.monitor_thread = None
        self.status_timer = None
        self.task_active = False
        self.global_hotkey = None
        
    def initialize(self):
        """Initialize all components."""
        print("AXON - Live AI Desktop Agent")
        print("Initializing...")
        
        # Display current LLM configuration
        from core.llm import get_current_provider, get_current_model, get_model_display_name
        print(f"\n{'='*60}")
        print(f"[LLM CONFIG] Current Provider: {get_current_provider().upper()}")
        print(f"[LLM CONFIG] Current Model: {get_current_model()}")
        print(f"[LLM CONFIG] Display Name: {get_model_display_name()}")
        print(f"{'='*60}\n")
        
        # Create Qt application
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)
        
        # Initialize UI components
        print("Creating UI components...")
        self.overlay = TransparentOverlay()
        self.input_dialog = TaskInputDialog()
        self.answer_overlay = AnswerOverlay()
        
        # Connect signals
        self.input_dialog.task_submitted.connect(self.on_task_submitted)
        self.answer_overlay.closed.connect(self.on_answer_overlay_closed)
        
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
        
        # Start global hotkey listener for Alt+G
        print("Starting global hotkey listener...")
        self.global_hotkey = start_global_hotkey(
            on_task_dialog=self.on_global_hotkey_task_dialog,
            on_context_help=self.on_global_hotkey_context_help
        )
        
        print("Initialization complete!")
        
    def on_task_submitted(self, task):
        """Handle task submission from input dialog.
        
        Args:
            task (str): User's task description
        """
        print(f"\n{'='*60}")
        print(f"[MAIN] Task submitted: {task}")
        print(f"{'='*60}\n")
        
        # Unlock the overlay now that dialog is closing
        print("[MAIN] Unlocking overlay (task starting)")
        self.overlay.set_dialog_open(False)
        
        # CRITICAL: Start the timer now that a task is actually running
        print("[MAIN] Starting overlay timer (task active)")
        self.overlay.start_timer()
        
        # Show the AI cursor overlay when task starts
        print("[MAIN] Showing AI cursor overlay...")
        self.task_active = True
        self.overlay.show_overlay()
        self.overlay.show_reticle()
        
        # Set initial position at center of screen
        import pyautogui
        screen_width, screen_height = pyautogui.size()
        self.overlay.set_reticle_position(screen_width // 2, screen_height // 2)
        self.overlay.set_status_text("Starting task...")
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
        self.input_dialog.task_submitted.connect(on_task)
        
        # Show dialog
        self.input_dialog.show()
        self.input_dialog.exec()
        
        # Disconnect signal
        self.input_dialog.task_submitted.disconnect(on_task)
        
        return result[0]
    
    def on_global_hotkey_task_dialog(self):
        """Handle Alt+G without text selection - open task dialog."""
        print("\n" + "="*60)
        print("[HOTKEY] Alt+G pressed - NO TEXT SELECTED")
        print("[MODE] Task Dialog Mode")
        print("="*60 + "\n")
        
        try:
            # CRITICAL: Stop the timer completely to prevent overlay from appearing
            if self.overlay:
                print("[MAIN] Stopping overlay timer (Alt+G pressed)")
                self.overlay.stop_timer()
                self.overlay.set_dialog_open(True)
                self.overlay.hide()
                self.overlay.hide_reticle()
            
            # Show the input dialog
            print("[MAIN] Opening task input dialog...")
            self.input_dialog.show()
            self.input_dialog.raise_()
            self.input_dialog.activateWindow()
            print("[MAIN] Task dialog opened successfully\n")
        except Exception as e:
            print(f"[ERROR] Failed to show task dialog: {e}")
    
    def on_global_hotkey_context_help(self, selected_text: str):
        """Handle Alt+G with text selection - provide context help.
        
        Args:
            selected_text: The text selected by the user
        """
        print("\n" + "="*60)
        print("[HOTKEY] Alt+G pressed - TEXT SELECTED")
        print("[MODE] Context Help Mode")
        print(f"[TEXT] Selected: '{selected_text[:100]}{'...' if len(selected_text) > 100 else ''}'")
        print("="*60 + "\n")
        
        try:
            # Hide main dialog if visible
            if self.input_dialog.isVisible():
                print("[MAIN] Hiding task dialog (context help mode)")
                self.input_dialog.hide()
            
            # CRITICAL: Stop the timer and ensure overlay stays hidden in context help mode
            if self.overlay:
                print("[MAIN] Stopping overlay timer (context help mode)")
                self.overlay.stop_timer()
                self.overlay.set_dialog_open(True)
                self.overlay.hide()
            
            # Show loading state in answer overlay
            print("[MAIN] Showing answer overlay with loading state...")
            self.answer_overlay.show_loading()
            
            # Get context help in a separate thread to avoid blocking UI
            def get_help_async():
                try:
                    print("[CONTEXT] Requesting AI help for selected text...")
                    answer = get_context_help(selected_text)
                    print(f"[CONTEXT] Received answer ({len(answer)} chars)")
                    # Update UI in main thread
                    QTimer.singleShot(0, lambda: self.answer_overlay.set_answer(answer))
                except Exception as e:
                    print(f"[ERROR] Context help failed: {e}")
                    error_msg = f"Sorry, I encountered an error:\n\n{str(e)}"
                    QTimer.singleShot(0, lambda: self.answer_overlay.set_answer(error_msg))
            
            # Start async help retrieval
            help_thread = threading.Thread(target=get_help_async, daemon=True)
            help_thread.start()
            print("[MAIN] Context help request started\n")
            
        except Exception as e:
            print(f"[ERROR] Failed to show context help: {e}")
            import traceback
            traceback.print_exc()
    
    def on_answer_overlay_closed(self):
        """Handle answer overlay being closed."""
        print("[MAIN] Answer overlay closed")
        # Unlock the overlay when answer overlay closes, but keep timer stopped
        if self.overlay:
            print("[MAIN] Unlocking overlay (answer overlay closed)")
            self.overlay.set_dialog_open(False)
            # Timer remains stopped - will only start when a task is submitted
        
    def update_status(self):
        """Update UI based on ui_queue (dedicated overlay queue)."""
        try:
            while not ui_queue.empty():
                status = ui_queue.get_nowait()
                
                if not isinstance(status, dict):
                    continue
                
                status_type = status.get('type', '')
                message = status.get('message', '')
                
                # Update overlay status text
                if message:
                    self.overlay.set_status_text(message)
                
                # Update task info if available
                if 'task' in status:
                    task = status.get('task', '')
                    action_count = status.get('action_count', 0)
                    response_time = status.get('response_time', 0.0)
                    self.overlay.set_task_info(
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
                        self.overlay.set_reticle_state('clicking')
                    elif action_type == 'mouse_move':
                        self.overlay.set_reticle_state('moving')
                    elif action_type in ['type', 'key']:
                        self.overlay.set_reticle_state('idle')
                    
                    # Move reticle to coordinates if available
                    if 'coordinate' in action:
                        coord = action['coordinate']
                        if isinstance(coord, (list, tuple)) and len(coord) == 2:
                            self.overlay.set_reticle_position(coord[0], coord[1])
                    elif 'x' in action and 'y' in action:
                        self.overlay.set_reticle_position(action['x'], action['y'])
                
                elif status_type == 'thinking':
                    self.overlay.set_reticle_state('thinking')
                    self.overlay.set_status_text("🤔 Thinking...")
                
                elif status_type == 'task_start':
                    self.task_active = True
                    self.overlay.show_overlay()
                    self.overlay.show_reticle()
                    self.overlay.set_status_text("🚀 Starting...")
                
                elif status_type == 'task_complete':
                    self.overlay.set_reticle_state('idle')
                    self.overlay.set_status_text("✅ Done!")
                    self.task_active = False
                    # Stop the timer when task completes
                    print("[MAIN] Stopping overlay timer (task complete)")
                    self.overlay.stop_timer()
                    # Hide after 3 seconds
                    QTimer.singleShot(3000, self._hide_overlay_if_idle)
                
                elif status_type == 'error':
                    self.overlay.set_reticle_state('idle')
                    self.overlay.set_status_text(f"❌ Error: {message[:50]}")
                    self.task_active = False
                    # Stop the timer when error occurs
                    print("[MAIN] Stopping overlay timer (error)")
                    self.overlay.stop_timer()
                    QTimer.singleShot(5000, self._hide_overlay_if_idle)
                
                elif status_type == 'stopped':
                    self.overlay.set_reticle_state('idle')
                    self.overlay.set_status_text("⏹ Stopped")
                    self.task_active = False
                    # Stop the timer when task is stopped
                    print("[MAIN] Stopping overlay timer (stopped)")
                    self.overlay.stop_timer()
                    QTimer.singleShot(3000, self._hide_overlay_if_idle)
                    
        except Exception as e:
            print(f"Error updating status: {e}")
    
    def _hide_overlay_if_idle(self):
        """Hide overlay only if no task is active."""
        if not self.task_active:
            self.overlay.hide_reticle()
    
    def run(self):
        """Run the application."""
        # Show UI components
        print("Showing UI...")
        
        # HIDE overlay initially - only show when task starts
        self.overlay.hide()
        
        # Show input dialog to get task
        self.input_dialog.show()
        
        # Start system tray
        self.tray.start()
        
        print("\nAXON is ready!")
        print("- Enter a task in the dialog to start")
        print("- AI cursor will appear when task begins")
        print("- Press F12 for emergency stop")
        print("- Press Alt+G to open task dialog or get context help")
        print("- Use the system tray icon for controls")
        print()
        
        # Run application event loop
        try:
            sys.exit(self.app.exec())
        finally:
            # Cleanup global hotkey
            if self.global_hotkey:
                stop_global_hotkey(self.global_hotkey)


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
