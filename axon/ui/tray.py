"""System tray icon with status menu.

Dev 3 (Pratham) - UI & Demo
Production-level implementation with:
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
- Comprehensive error handling and logging
- Recent tasks menu
- Quick actions
- Status tooltips
- Notification preferences
"""

from typing import Optional, Callable, List
import pystray
from PIL import Image, ImageDraw, ImageFont
from config import status_queue, kill_event
import threading
import time

from .logger import get_logger, log_error_with_context
from .exceptions import TrayIconException, ErrorCode, handle_exception
from .config_ui import get_config


# Initialize logger
logger = get_logger("tray")


class TrayIcon:
    """System tray icon for AXON with production features."""
    
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
    
    def __init__(
        self,
        overlay=None,
        input_dialog_callback: Optional[Callable] = None
    ):
        """Initialize the tray icon with error handling.
        
        Args:
            overlay: Reference to overlay window (optional)
            input_dialog_callback: Callback to show input dialog (optional)
        """
        try:
            logger.info("Initializing TrayIcon")
            
            # Load configuration
            self.config = get_config().tray
            
            # State
            self.icon: Optional[pystray.Icon] = None
            self.state = self.STATE_IDLE
            self.overlay = overlay
            self.input_dialog_callback = input_dialog_callback
            self.overlay_visible = True
            self.agent_running = False
            self.monitor_thread: Optional[threading.Thread] = None
            self.running = False
            
            # Recent tasks
            self.recent_tasks: List[str] = []
            self.max_recent_tasks = 5
            
            # Notification tracking
            self.last_notification_time = 0.0
            self.notification_cooldown = 2.0  # seconds
            
            logger.info("TrayIcon initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize TrayIcon: {e}")
            raise TrayIconException(
                "Failed to initialize tray icon",
                ErrorCode.TRAY_CREATION_ERROR,
                {"error": str(e)}
            )
    
    def create_icon_image(self, state: str) -> Image.Image:
        """Create an icon image for the given state with error handling.
        
        Args:
            state: Current state
            
        Returns:
            PIL Image for the icon
        """
        try:
            # Create 64x64 image with transparency
            size = self.config.icon_size
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
                font = ImageFont.truetype("arial.ttf", 32)
            except Exception:
                font = ImageFont.load_default()
            
            # Draw "A" in white
            text = "A"
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            text_x = (size - text_width) // 2
            text_y = (size - text_height) // 2 - 2
            
            draw.text((text_x, text_y), text, fill=(255, 255, 255, 255), font=font)
            
            logger.debug(f"Created icon image for state: {state}")
            return image
            
        except Exception as e:
            logger.error(f"Error creating icon image: {e}")
            # Return a simple fallback image
            image = Image.new('RGBA', (64, 64), (100, 200, 255, 255))
            return image
    
    def create_menu(self) -> tuple:
        """Create the context menu with error handling.
        
        Returns:
            Tuple of menu items for pystray
        """
        try:
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
            
            # Recent Tasks submenu (if enabled and has tasks)
            if self.config.show_quick_actions and self.recent_tasks:
                recent_menu_items = []
                for task in self.recent_tasks[-5:]:  # Last 5 tasks
                    task_preview = task[:30] + "..." if len(task) > 30 else task
                    recent_menu_items.append(
                        pystray.MenuItem(
                            task_preview,
                            lambda _, t=task: self._rerun_task(t)
                        )
                    )
                menu_items.append(
                    pystray.MenuItem("📋 Recent Tasks", pystray.Menu(*recent_menu_items))
                )
            
            # Separator
            menu_items.append(pystray.Menu.SEPARATOR)
            
            # Status (if enabled)
            if self.config.show_status_in_menu:
                menu_items.append(
                    pystray.MenuItem(f"ℹ Status: {self.state.upper()}", self.on_show_status)
                )
            
            # Settings
            menu_items.append(
                pystray.MenuItem("⚙ Settings", self.on_settings)
            )
            
            # Separator
            menu_items.append(pystray.Menu.SEPARATOR)
            
            # Exit
            menu_items.append(
                pystray.MenuItem("❌ Exit", self.on_exit)
            )
            
            logger.debug(f"Created menu with {len(menu_items)} items")
            return tuple(menu_items)
            
        except Exception as e:
            logger.error(f"Error creating menu: {e}")
            # Return minimal menu
            return (
                pystray.MenuItem("❌ Exit", self.on_exit),
            )
    
    def start(self):
        """Start the tray icon with error handling."""
        try:
            logger.info("Starting tray icon")
            
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
            self.monitor_thread = threading.Thread(
                target=self._monitor_status_queue,
                daemon=True
            )
            self.monitor_thread.start()
            
            # Run in separate thread
            icon_thread = threading.Thread(target=self.icon.run, daemon=True)
            icon_thread.start()
            
            logger.info("Tray icon started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start tray icon: {e}")
            handle_exception(
                TrayIconException(
                    "Failed to start tray icon",
                    ErrorCode.TRAY_CREATION_ERROR,
                    {"error": str(e)}
                ),
                logger,
                "tray"
            )
    
    def stop(self):
        """Stop the tray icon with cleanup."""
        try:
            logger.info("Stopping tray icon")
            self.running = False
            if self.icon:
                self.icon.stop()
            logger.info("Tray icon stopped")
        except Exception as e:
            logger.error(f"Error stopping tray icon: {e}")
    
    def update_state(self, new_state: str):
        """Update the tray icon state with validation.
        
        Args:
            new_state: New state
        """
        try:
            if new_state not in self.STATE_COLORS:
                logger.warning(f"Invalid state: {new_state}")
                return
            
            if self.state != new_state:
                logger.info(f"Tray state changed: {self.state} -> {new_state}")
                self.state = new_state
                
                # Create new icon image
                if self.icon:
                    new_image = self.create_icon_image(new_state)
                    self.icon.icon = new_image
                    
                    # Update menu
                    self.icon.menu = self.create_menu()
                    
        except Exception as e:
            logger.error(f"Error updating state: {e}")
    
    def show_notification(self, title: str, message: str):
        """Show a system notification with rate limiting.
        
        Args:
            title: Notification title
            message: Notification message
        """
        try:
            if not self.config.enable_notifications:
                logger.debug("Notifications disabled")
                return
            
            # Rate limiting
            current_time = time.time()
            if current_time - self.last_notification_time < self.notification_cooldown:
                logger.debug("Notification rate limited")
                return
            
            if self.icon:
                self.icon.notify(message, title)
                self.last_notification_time = current_time
                logger.info(f"Notification shown: {title} - {message[:50]}...")
                
        except Exception as e:
            logger.debug(f"Error showing notification: {e}")
            handle_exception(
                TrayIconException(
                    "Failed to show notification",
                    ErrorCode.TRAY_NOTIFICATION_ERROR,
                    {"title": title, "message": message}
                ),
                logger,
                "tray"
            )
    
    def on_start_agent(self):
        """Handle Start Agent menu item with error handling."""
        try:
            logger.info("Start Agent clicked")
            
            # Show task input dialog
            if self.input_dialog_callback:
                task = self.input_dialog_callback()
                if task:
                    self.agent_running = True
                    self.update_state(self.STATE_RUNNING)
                    self.show_notification("AXON", f"Starting task: {task[:50]}...")
                    
                    # Add to recent tasks
                    self._add_recent_task(task)
                    
                    # Put task in status queue for agent to pick up
                    status_queue.put({
                        'type': 'task_start',
                        'task': task
                    })
            else:
                self.agent_running = True
                self.update_state(self.STATE_RUNNING)
                self.show_notification("AXON", "Agent started")
                
        except Exception as e:
            logger.error(f"Error starting agent: {e}")
            self.show_notification("AXON Error", "Failed to start agent")
    
    def on_stop_agent(self):
        """Handle Stop Agent menu item with error handling."""
        try:
            logger.info("Stop Agent clicked")
            
            # Set kill_event to stop agent
            kill_event.set()
            
            self.agent_running = False
            self.update_state(self.STATE_STOPPED)
            self.show_notification("AXON", "Agent stopped")
            
            # Clear kill event after a moment
            threading.Timer(1.0, kill_event.clear).start()
            
        except Exception as e:
            logger.error(f"Error stopping agent: {e}")
    
    def on_toggle_overlay(self):
        """Handle Toggle Overlay menu item with error handling."""
        try:
            logger.info("Toggle Overlay clicked")
            
            if self.overlay:
                if self.overlay_visible:
                    self.overlay.hide_overlay()
                    self.overlay_visible = False
                    logger.info("Overlay hidden")
                else:
                    self.overlay.show_overlay()
                    self.overlay_visible = True
                    logger.info("Overlay shown")
                
                # Update menu
                if self.icon:
                    self.icon.menu = self.create_menu()
                    
        except Exception as e:
            logger.error(f"Error toggling overlay: {e}")
    
    def on_new_task(self):
        """Handle New Task menu item with error handling."""
        try:
            logger.info("New Task clicked")
            
            # Show task input dialog
            if self.input_dialog_callback:
                task = self.input_dialog_callback()
                if task:
                    self.show_notification("AXON", f"New task: {task[:50]}...")
                    
                    # Add to recent tasks
                    self._add_recent_task(task)
                    
                    # Put task in status queue
                    status_queue.put({
                        'type': 'task_start',
                        'task': task
                    })
                    
        except Exception as e:
            logger.error(f"Error creating new task: {e}")
    
    def on_show_status(self):
        """Handle Show Status menu item with error handling."""
        try:
            logger.info("Show Status clicked")
            
            # Show notification with current status
            status_msg = f"State: {self.state.upper()}\n"
            status_msg += f"Agent: {'Running' if self.agent_running else 'Stopped'}\n"
            status_msg += f"Overlay: {'Visible' if self.overlay_visible else 'Hidden'}"
            
            self.show_notification("AXON Status", status_msg)
            
        except Exception as e:
            logger.error(f"Error showing status: {e}")
    
    def on_settings(self):
        """Handle Settings menu item."""
        try:
            logger.info("Settings clicked")
            self.show_notification("AXON", "Settings feature coming soon!")
        except Exception as e:
            logger.error(f"Error opening settings: {e}")
    
    def on_exit(self):
        """Handle Exit menu item with cleanup."""
        try:
            logger.info("Exit clicked")
            
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
            
        except Exception as e:
            logger.error(f"Error exiting: {e}")
            import sys
            sys.exit(1)
    
    def _add_recent_task(self, task: str):
        """Add task to recent tasks list.
        
        Args:
            task: Task description
        """
        try:
            if task not in self.recent_tasks:
                self.recent_tasks.append(task)
                
                # Limit to max recent tasks
                if len(self.recent_tasks) > self.max_recent_tasks:
                    self.recent_tasks.pop(0)
                
                # Update menu
                if self.icon:
                    self.icon.menu = self.create_menu()
                
                logger.debug(f"Added recent task: {task[:30]}...")
                
        except Exception as e:
            logger.warning(f"Error adding recent task: {e}")
    
    def _rerun_task(self, task: str):
        """Rerun a recent task.
        
        Args:
            task: Task to rerun
        """
        try:
            logger.info(f"Rerunning task: {task[:50]}...")
            
            self.show_notification("AXON", f"Rerunning: {task[:50]}...")
            
            # Put task in status queue
            status_queue.put({
                'type': 'task_start',
                'task': task
            })
            
            self.agent_running = True
            self.update_state(self.STATE_RUNNING)
            
        except Exception as e:
            logger.error(f"Error rerunning task: {e}")
    
    def _monitor_status_queue(self):
        """Monitor status queue and update tray icon (internal method)."""
        logger.info("Status queue monitoring started")
        
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
                            logger.debug("Task started")
                            
                        elif status_type == 'task_complete':
                            self.agent_running = False
                            self.update_state(self.STATE_IDLE)
                            self.show_notification("AXON", "Task completed!")
                            logger.info("Task completed")
                            
                        elif status_type == 'error':
                            self.update_state(self.STATE_ERROR)
                            error_msg = status.get('message', 'Unknown error')
                            self.show_notification("AXON Error", error_msg)
                            logger.error(f"Error status: {error_msg}")
                            
                        elif status_type == 'thinking':
                            logger.debug("Agent thinking")
                            
                        elif status_type == 'action':
                            action = status.get('action', '')
                            logger.debug(f"Agent action: {action}")
                
                # Small sleep to avoid busy waiting
                time.sleep(self.config.update_interval_ms / 1000.0)
                
            except Exception as e:
                logger.debug(f"Error in status monitoring: {e}")
                time.sleep(0.1)
        
        logger.info("Status queue monitoring stopped")
    
    def reload_config(self):
        """Reload configuration from config manager."""
        try:
            logger.info("Reloading tray configuration")
            self.config = get_config().tray
            logger.info("Tray configuration reloaded")
        except Exception as e:
            logger.error(f"Error reloading config: {e}")
    
    def __del__(self):
        """Cleanup resources."""
        try:
            logger.info("TrayIcon destroyed")
            self.stop()
        except:
            pass


def create_tray_icon(
    overlay=None,
    input_dialog_callback: Optional[Callable] = None
) -> TrayIcon:
    """Create and start the system tray icon with error handling.
    
    Args:
        overlay: Reference to overlay window (optional)
        input_dialog_callback: Callback to show input dialog (optional)
    
    Returns:
        Active tray icon instance
        
    Raises:
        TrayIconException: If tray creation fails
    """
    try:
        logger.info("Creating tray icon")
        
        # Create TrayIcon instance
        tray = TrayIcon(overlay=overlay, input_dialog_callback=input_dialog_callback)
        
        # Start the icon
        tray.start()
        
        logger.info("Tray icon created successfully")
        return tray
        
    except Exception as e:
        logger.error(f"Failed to create tray icon: {e}")
        raise TrayIconException(
            "Failed to create tray icon",
            ErrorCode.TRAY_CREATION_ERROR,
            {"error": str(e)}
        )


def monitor_status_queue(tray_icon: TrayIcon):
    """Monitor status queue and update tray icon.
    
    Args:
        tray_icon: Tray icon to update
        
    Note:
        This is now handled internally by TrayIcon._monitor_status_queue.
        This function is kept for backward compatibility.
    """
    logger.debug("monitor_status_queue called (handled internally)")
    pass


# Made with Bob
