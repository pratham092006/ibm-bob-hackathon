"""System tray icon with status menu.

Dev 3 (Pratham) - UI & Demo
TODO: Implement system tray icon
- Create system tray icon using pystray
- Add context menu with options:
  - Start/Stop agent
  - Show/Hide overlay
  - Open task input
  - View status
  - Settings
  - Exit
- Update icon based on agent state (idle, running, error)
- Show notifications for important events
- Handle tray icon clicks
- Ensure tray persists when main window is hidden
"""

import pystray
from PIL import Image, ImageDraw
from config import status_queue, kill_event
import threading


class TrayIcon:
    """System tray icon for AXON."""
    
    # Icon states
    STATE_IDLE = "idle"
    STATE_RUNNING = "running"
    STATE_ERROR = "error"
    STATE_STOPPED = "stopped"
    
    def __init__(self):
        """Initialize the tray icon."""
        self.icon = None
        self.state = self.STATE_IDLE
        self.menu_items = []
        
    def create_icon_image(self, state):
        """Create an icon image for the given state.
        
        Args:
            state (str): Current state
            
        Returns:
            Image: PIL Image for the icon
        """
        # TODO: Implement icon image creation
        # 1. Create 64x64 image
        # 2. Draw circle with state-specific color:
        #    - IDLE: blue
        #    - RUNNING: green
        #    - ERROR: red
        #    - STOPPED: gray
        # 3. Add "A" letter in center
        # 4. Return image
        pass
    
    def create_menu(self):
        """Create the context menu.
        
        Returns:
            tuple: Menu items for pystray
        """
        # TODO: Implement menu creation
        # 1. Create menu items:
        #    - Start Agent (if stopped)
        #    - Stop Agent (if running)
        #    - Toggle Overlay
        #    - New Task
        #    - Status
        #    - Exit
        # 2. Return as tuple
        pass
    
    def start(self):
        """Start the tray icon."""
        # TODO: Implement tray icon startup
        # 1. Create icon image
        # 2. Create menu
        # 3. Create pystray.Icon instance
        # 4. Run in separate thread
        pass
    
    def stop(self):
        """Stop the tray icon."""
        # TODO: Implement tray icon shutdown
        # 1. Stop the icon
        # 2. Clean up resources
        pass
    
    def update_state(self, new_state):
        """Update the tray icon state.
        
        Args:
            new_state (str): New state
        """
        # TODO: Implement state update
        # 1. Update internal state
        # 2. Create new icon image
        # 3. Update tray icon
        self.state = new_state
    
    def show_notification(self, title, message):
        """Show a system notification.
        
        Args:
            title (str): Notification title
            message (str): Notification message
        """
        # TODO: Implement notification
        # Use icon.notify() to show notification
        pass
    
    def on_start_agent(self):
        """Handle Start Agent menu item."""
        # TODO: Implement start handler
        # 1. Show task input dialog
        # 2. Start agent with task
        # 3. Update state
        pass
    
    def on_stop_agent(self):
        """Handle Stop Agent menu item."""
        # TODO: Implement stop handler
        # 1. Set kill_event
        # 2. Update state
        # 3. Show notification
        pass
    
    def on_toggle_overlay(self):
        """Handle Toggle Overlay menu item."""
        # TODO: Implement overlay toggle
        pass
    
    def on_new_task(self):
        """Handle New Task menu item."""
        # TODO: Implement new task handler
        # Show task input dialog
        pass
    
    def on_show_status(self):
        """Handle Show Status menu item."""
        # TODO: Implement status display
        # Show dialog with current status
        pass
    
    def on_exit(self):
        """Handle Exit menu item."""
        # TODO: Implement exit handler
        # 1. Stop agent if running
        # 2. Stop tray icon
        # 3. Exit application
        pass


def create_tray_icon():
    """Create and start the system tray icon.
    
    Returns:
        TrayIcon: Active tray icon instance
    """
    # TODO: Implement tray icon creation
    # 1. Create TrayIcon instance
    # 2. Start the icon
    # 3. Return instance
    pass


def monitor_status_queue(tray_icon):
    """Monitor status queue and update tray icon.
    
    Args:
        tray_icon (TrayIcon): Tray icon to update
    """
    # TODO: Implement status monitoring
    # 1. Run in separate thread
    # 2. Continuously check status_queue
    # 3. Update tray icon state based on status
    # 4. Show notifications for important events
    pass

# Made with Bob
