"""System tray icon with status menu.

Dev 3 (Pratham) - UI & Demo
Implements system tray icon with:
- System tray icon using pystray
- Context menu with options:
  - Start/Stop agent
  - Show/Hide overlay
  - Open task input
  - View status
  - Settings
  - Exit
- Icon updates based on agent state (idle, running, error)
- Notifications for important events
- Tray icon click handling
- Persistent tray when main window is hidden
"""

import pystray
from PIL import Image, ImageDraw, ImageFont
from config import status_queue, kill_event
import threading
import time


class TrayIcon:
    """System tray icon for AXON."""
    
    # Icon states
    STATE_IDLE = "idle"
    STATE_RUNNING = "running"
    STATE_ERROR = "error"
    STATE_STOPPED = "stopped"
    
    # State colors (RGB)
    STATE_COLORS = {
        STATE_IDLE: (100, 200, 255),      # Blue
        STATE_RUNNING: (100, 255, 150),   # Green
        STATE_ERROR: (255, 100, 100),     # Red
        STATE_STOPPED: (150, 150, 150),   # Gray
    }
    
    def __init__(self, overlay=None, input_dialog_callback=None):
        """Initialize the tray icon.
        
        Args:
            overlay: Reference to overlay window (optional)
            input_dialog_callback: Callback to show input dialog (optional)
        """
        self.icon = None
        self.state = self.STATE_IDLE
        self.overlay = overlay
        self.input_dialog_callback = input_dialog_callback
        self.overlay_visible = True
        self.agent_running = False
        self.monitor_thread = None
        self.running = False
        
    def create_icon_image(self, state):
        """Create an icon image for the given state.
        
        Args:
            state (str): Current state
            
        Returns:
            Image: PIL Image for the icon
        """
        # Create 64x64 image with transparency
        size = 64
        image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        
        # Get state-specific color
        color = self.STATE_COLORS.get(state, self.STATE_COLORS[self.STATE_IDLE])
        
        # Draw circle with state color
        margin = 8
        draw.ellipse(
            [margin, margin, size - margin, size - margin],
            fill=color + (255,),
            outline=(255, 255, 255, 200),
            width=2
        )
        
        # Add "A" letter in center
        try:
            # Try to use a nice font
            font = ImageFont.truetype("arial.ttf", 32)
        except:
            # Fallback to default font
            font = ImageFont.load_default()
        
        # Draw "A" in white
        text = "A"
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        text_x = (size - text_width) // 2
        text_y = (size - text_height) // 2 - 2
        
        draw.text((text_x, text_y), text, fill=(255, 255, 255, 255), font=font)
        
        return image
    
    def create_menu(self):
        """Create the context menu.
        
        Returns:
            tuple: Menu items for pystray
        """
        # Create menu items based on current state
        menu_items = []
        
        # Start/Stop Agent
        if self.agent_running:
            menu_items.append(
                pystray.MenuItem("⏹ Stop Agent", self.on_stop_agent)
            )
        else:
            menu_items.append(
                pystray.MenuItem("▶ Start Agent", self.on_start_agent)
            )
        
        # Toggle Overlay
        overlay_text = "Hide Overlay" if self.overlay_visible else "Show Overlay"
        menu_items.append(
            pystray.MenuItem(f"👁 {overlay_text}", self.on_toggle_overlay)
        )
        
        # New Task
        menu_items.append(
            pystray.MenuItem("📝 New Task", self.on_new_task)
        )
        
        # Separator
        menu_items.append(pystray.Menu.SEPARATOR)
        
        # Status
        menu_items.append(
            pystray.MenuItem(f"ℹ Status: {self.state.upper()}", self.on_show_status)
        )
        
        # Separator
        menu_items.append(pystray.Menu.SEPARATOR)
        
        # Exit
        menu_items.append(
            pystray.MenuItem("❌ Exit", self.on_exit)
        )
        
        return tuple(menu_items)
    
    def start(self):
        """Start the tray icon."""
        # Create icon image
        image = self.create_icon_image(self.state)
        
        # Create menu
        menu = self.create_menu()
        
        # Create pystray.Icon instance
        self.icon = pystray.Icon(
            "AXON",
            image,
            "AXON - AI Desktop Agent",
            menu=menu
        )
        
        # Start monitoring status queue
        self.running = True
        self.monitor_thread = threading.Thread(target=self._monitor_status_queue, daemon=True)
        self.monitor_thread.start()
        
        # Run in separate thread
        icon_thread = threading.Thread(target=self.icon.run, daemon=True)
        icon_thread.start()
    
    def stop(self):
        """Stop the tray icon."""
        self.running = False
        if self.icon:
            self.icon.stop()
    
    def update_state(self, new_state):
        """Update the tray icon state.
        
        Args:
            new_state (str): New state
        """
        if new_state not in self.STATE_COLORS:
            return
            
        self.state = new_state
        
        # Create new icon image
        if self.icon:
            new_image = self.create_icon_image(new_state)
            self.icon.icon = new_image
            
            # Update menu
            self.icon.menu = self.create_menu()
    
    def show_notification(self, title, message):
        """Show a system notification.
        
        Args:
            title (str): Notification title
            message (str): Notification message
        """
        if self.icon:
            try:
                self.icon.notify(message, title)
            except:
                # Notifications might not be supported on all platforms
                pass
    
    def on_start_agent(self):
        """Handle Start Agent menu item."""
        # Show task input dialog
        if self.input_dialog_callback:
            task = self.input_dialog_callback()
            if task:
                self.agent_running = True
                self.update_state(self.STATE_RUNNING)
                self.show_notification("AXON", f"Starting task: {task[:50]}...")
                
                # Put task in status queue for agent to pick up
                status_queue.put({
                    'type': 'task_start',
                    'task': task
                })
        else:
            self.agent_running = True
            self.update_state(self.STATE_RUNNING)
            self.show_notification("AXON", "Agent started")
    
    def on_stop_agent(self):
        """Handle Stop Agent menu item."""
        # Set kill_event to stop agent
        kill_event.set()
        
        self.agent_running = False
        self.update_state(self.STATE_STOPPED)
        self.show_notification("AXON", "Agent stopped")
        
        # Clear kill event after a moment
        threading.Timer(1.0, kill_event.clear).start()
    
    def on_toggle_overlay(self):
        """Handle Toggle Overlay menu item."""
        if self.overlay:
            if self.overlay_visible:
                self.overlay.hide_overlay()
                self.overlay_visible = False
            else:
                self.overlay.show_overlay()
                self.overlay_visible = True
            
            # Update menu
            if self.icon:
                self.icon.menu = self.create_menu()
    
    def on_new_task(self):
        """Handle New Task menu item."""
        # Show task input dialog
        if self.input_dialog_callback:
            task = self.input_dialog_callback()
            if task:
                self.show_notification("AXON", f"New task: {task[:50]}...")
                
                # Put task in status queue
                status_queue.put({
                    'type': 'task_start',
                    'task': task
                })
    
    def on_show_status(self):
        """Handle Show Status menu item."""
        # Show notification with current status
        status_msg = f"State: {self.state.upper()}\n"
        status_msg += f"Agent: {'Running' if self.agent_running else 'Stopped'}\n"
        status_msg += f"Overlay: {'Visible' if self.overlay_visible else 'Hidden'}"
        
        self.show_notification("AXON Status", status_msg)
    
    def on_exit(self):
        """Handle Exit menu item."""
        # Stop agent if running
        if self.agent_running:
            kill_event.set()
        
        # Show notification
        self.show_notification("AXON", "Exiting...")
        
        # Stop tray icon
        self.running = False
        if self.icon:
            self.icon.stop()
        
        # Exit application
        import sys
        sys.exit(0)
    
    def _monitor_status_queue(self):
        """Monitor status queue and update tray icon (internal method)."""
        while self.running:
            try:
                # Check for status updates (non-blocking with timeout)
                if not status_queue.empty():
                    status = status_queue.get(timeout=0.1)
                    
                    # Update state based on status
                    if isinstance(status, dict):
                        status_type = status.get('type', '')
                        
                        if status_type == 'task_start':
                            self.agent_running = True
                            self.update_state(self.STATE_RUNNING)
                        elif status_type == 'task_complete':
                            self.agent_running = False
                            self.update_state(self.STATE_IDLE)
                            self.show_notification("AXON", "Task completed!")
                        elif status_type == 'error':
                            self.update_state(self.STATE_ERROR)
                            error_msg = status.get('message', 'Unknown error')
                            self.show_notification("AXON Error", error_msg)
                        elif status_type == 'thinking':
                            # Agent is thinking
                            pass
                        elif status_type == 'action':
                            # Agent is performing action
                            pass
                
                # Small sleep to avoid busy waiting
                time.sleep(0.1)
            except:
                # Handle any errors gracefully
                time.sleep(0.1)


def create_tray_icon(overlay=None, input_dialog_callback=None):
    """Create and start the system tray icon.
    
    Args:
        overlay: Reference to overlay window (optional)
        input_dialog_callback: Callback to show input dialog (optional)
    
    Returns:
        TrayIcon: Active tray icon instance
    """
    # Create TrayIcon instance
    tray = TrayIcon(overlay=overlay, input_dialog_callback=input_dialog_callback)
    
    # Start the icon
    tray.start()
    
    # Return instance
    return tray


def monitor_status_queue(tray_icon):
    """Monitor status queue and update tray icon.
    
    Args:
        tray_icon (TrayIcon): Tray icon to update
    """
    # This is now handled internally by TrayIcon._monitor_status_queue
    # This function is kept for backward compatibility
    pass

# Made with Bob
