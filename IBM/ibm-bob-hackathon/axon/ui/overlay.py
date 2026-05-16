"""Floating cursor widget with status label.

Dev 3 (Pratham) - UI & Demo
Implements a floating cursor indicator:
- Larger widget (200x200px) that follows predicted cursor position
- Transparent background with only the reticle visible
- Status text label showing current action
- Always on top but click-through
- NO fullscreen window, NO black screen
- Just a cursor indicator beside your normal cursor
"""

from PyQt6.QtWidgets import QApplication, QWidget, QLabel
from PyQt6.QtCore import Qt, QTimer, QPoint, QRect
from PyQt6.QtGui import QPainter, QColor, QPen, QFont
import sys
import time
import queue
from .reticle import Reticle


class TransparentOverlay(QWidget):
    """Floating cursor widget with status label."""
    
    def __init__(self):
        """Initialize the cursor widget."""
        super().__init__()
        self.reticle = Reticle()
        self.status_text = ""
        self._display_status = ""  # Status shown on widget
        self.current_task = ""
        self.current_step = ""
        self.response_time = 0.0
        self.action_count = 0
        self.last_update_time = time.time()
        
        # Widget size - larger for visible glow effects
        self.widget_size = 200
        self.center_offset = self.widget_size // 2
        
        self.init_ui()
        
    def init_ui(self):
        """Set up the floating cursor widget."""
        # Set window flags - floating widget, NOT fullscreen
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool |
            Qt.WindowType.WindowTransparentForInput |  # Click-through
            Qt.WindowType.WindowDoesNotAcceptFocus |  # Don't steal focus
            Qt.WindowType.BypassWindowManagerHint  # Bypass window manager
        )
        
        # Set larger fixed size for better visibility
        self.setFixedSize(self.widget_size, self.widget_size)
        
        # Set transparent background
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground)
        
        # Start hidden at (0, 0)
        self.move(0, 0)
        
        # Set up update timer for smooth animation (60 FPS)
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._on_timer_update)
        self.update_timer.start(16)  # ~60 FPS (16ms per frame)
    
    def _on_timer_update(self):
        """Handle timer update for animations."""
        current_time = time.time()
        delta_time = current_time - self.last_update_time
        self.last_update_time = current_time
        
        # Update reticle animation
        self.reticle.update(delta_time)
        
        # Trigger repaint
        self.update()
    
    def paintEvent(self, event):
        """Paint the reticle cursor and status text.
        
        Args:
            event: Paint event
        """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw reticle at center of widget
        center = QPoint(self.center_offset, self.center_offset)
        
        # Temporarily set reticle position to center of widget for drawing
        old_pos = self.reticle.position
        self.reticle.position = center
        self.reticle.target_position = center
        
        # Draw reticle
        self.reticle.draw(painter, time.time())
        
        # Restore position
        self.reticle.position = old_pos
        
        # Draw status text below the reticle
        if self._display_status:
            font = QFont("Segoe UI", 9, QFont.Weight.Bold)
            painter.setFont(font)
            
            # Draw text background (semi-transparent dark pill)
            text_y = self.center_offset + 45
            metrics = painter.fontMetrics()
            text_width = metrics.horizontalAdvance(self._display_status)
            text_height = metrics.height()
            
            bg_rect = QRect(
                self.center_offset - text_width // 2 - 8,
                text_y - 2,
                text_width + 16,
                text_height + 4
            )
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(20, 20, 20, 180))
            painter.drawRoundedRect(bg_rect, 8, 8)
            
            # Draw text
            painter.setPen(QColor(255, 255, 255, 230))
            painter.drawText(
                QRect(0, text_y, self.widget_size, text_height + 4),
                Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop,
                self._display_status
            )
        
        painter.end()
    
    def set_reticle_position(self, x, y, animate=True):
        """Move the widget to follow the predicted cursor position.
        
        Args:
            x (int): Screen X coordinate
            y (int): Screen Y coordinate
            animate (bool): Whether to animate movement
        """
        # Move the widget so reticle appears at (x, y) on screen
        widget_x = x - self.center_offset
        widget_y = y - self.center_offset
        
        self.move(widget_x, widget_y)
        self.reticle.set_position(x, y, animate)
        self.update()
    
    def set_reticle_state(self, state):
        """Set the reticle state (changes color).
        
        Args:
            state (str): Reticle state (idle, thinking, moving, clicking)
        """
        self.reticle.set_state(state)
        self.update()
    
    def set_status(self, text):
        """Update the status text (for logging, not displayed).
        
        Args:
            text (str): Status message
        """
        self.status_text = text
        print(f"[STATUS] {text}")
    
    def set_status_text(self, text):
        """Update the displayed status text on the widget.
        
        Args:
            text (str): Short status message to show below reticle
        """
        # Truncate long text
        self._display_status = text[:30] if text else ""
        self.update()
    
    def set_task_info(self, task="", step="", response_time=0.0, action_count=0):
        """Update task information (for logging, not displayed).
        
        Args:
            task (str): Current task description
            step (str): Current step description
            response_time (float): Response time in seconds
            action_count (int): Number of actions performed
        """
        self.current_task = task
        self.current_step = step
        self.response_time = response_time
        self.action_count = action_count
        print(f"[TASK] {task} | Step: {step} | Actions: {action_count}")
    
    def hide_reticle(self):
        """Hide the cursor widget."""
        self.hide()
    
    def show_reticle(self):
        """Show the cursor widget."""
        self.reticle.show()
        self.show()
    
    def show_overlay(self):
        """Show the cursor widget."""
        self.show()
    
    def hide_overlay(self):
        """Hide the cursor widget."""
        self.hide()


def create_overlay():
    """Create and return a floating cursor widget.
    
    Returns:
        TransparentOverlay: Cursor widget instance
    """
    # Create QApplication if not exists
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    # Create cursor widget
    overlay = TransparentOverlay()
    
    # Show widget
    overlay.show()
    
    print("[OVERLAY] Floating cursor widget created (NO fullscreen!)")
    
    # Return instance
    return overlay


def run_overlay_app(overlay):
    """Run the Qt application event loop.
    
    Args:
        overlay (TransparentOverlay): Cursor widget instance
    """
    # Get QApplication instance
    app = QApplication.instance()
    if app is not None:
        # Run QApplication.exec()
        app.exec()


def start_overlay_queue_listener(overlay, ui_queue):
    """Listen for status updates from agent and update overlay position.
    
    This function creates a QTimer that periodically checks the ui_queue
    for status updates and updates the overlay accordingly. This is the
    thread-safe way to communicate between the background agent thread
    and the main Qt UI thread.
    
    Args:
        overlay (TransparentOverlay): The overlay widget to update
        ui_queue (queue.Queue): Queue containing status updates from agent
        
    Returns:
        QTimer: The timer object (keep reference to prevent garbage collection)
    """
    timer = QTimer()
    
    def check_queue():
        """Check queue for updates and update overlay."""
        try:
            while not ui_queue.empty():
                status = ui_queue.get_nowait()
                
                if not isinstance(status, dict):
                    continue
                
                status_type = status.get('type', '')
                message = status.get('message', '')
                
                # Update overlay status text
                if message:
                    overlay.set_status_text(message)
                
                # Handle action updates - move cursor BEFORE action executes
                if status_type == 'action':
                    action = status.get('action', {})
                    action_type = action.get('action', '')
                    
                    # Move reticle to coordinates if available
                    if 'coordinate' in action:
                        coord = action['coordinate']
                        if isinstance(coord, (list, tuple)) and len(coord) == 2:
                            overlay.set_reticle_position(coord[0], coord[1], animate=True)
                    elif 'x' in action and 'y' in action:
                        overlay.set_reticle_position(action['x'], action['y'], animate=True)
                    
                    # Set state based on action type
                    state_map = {
                        'left_click': 'clicking',
                        'right_click': 'clicking',
                        'double_click': 'clicking',
                        'click': 'clicking',
                        'mouse_move': 'moving',
                        'type': 'idle',
                        'key': 'idle'
                    }
                    state = state_map.get(action_type, 'thinking')
                    overlay.set_reticle_state(state)
                
                elif status_type == 'thinking':
                    overlay.set_reticle_state('thinking')
                
                elif status_type == 'task_start':
                    overlay.show()
                    overlay.show_reticle()
                
                elif status_type == 'task_complete':
                    overlay.set_reticle_state('idle')
                
                elif status_type == 'error':
                    overlay.set_reticle_state('idle')
                
                elif status_type == 'stopped':
                    overlay.set_reticle_state('idle')
                    
        except queue.Empty:
            pass  # Queue is empty, continue
        except Exception as e:
            # Silently handle queue errors to prevent UI crashes
            print(f"[OVERLAY] Queue error: {e}")
    
    timer.timeout.connect(check_queue)
    timer.start(50)  # Check every 50ms for smooth updates
    return timer

# Made with Bob
