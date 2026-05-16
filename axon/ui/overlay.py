"""Transparent fullscreen overlay using PyQt6.

Dev 3 (Pratham) - UI & Demo
Implements transparent overlay with:
- PyQt6 window that covers entire screen
- Transparent and click-through window
- Always on top
- Displays reticle at predicted cursor position
- Shows status messages and agent state
- Handles multi-monitor setups
- Optimized for performance (minimal CPU usage)
- Toggleable visibility
"""

from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtCore import Qt, QTimer, QPoint
from PyQt6.QtGui import QPainter, QColor, QPen, QFont
import sys
import time
from .reticle import Reticle


class TransparentOverlay(QWidget):
    """Transparent fullscreen overlay for visual feedback."""
    
    def __init__(self):
        """Initialize the overlay window."""
        super().__init__()
        self.reticle = Reticle()
        self.status_text = ""
        self.current_task = ""
        self.current_step = ""
        self.response_time = 0.0
        self.action_count = 0
        self.last_update_time = time.time()
        self.init_ui()
        
    def init_ui(self):
        """Set up the overlay window properties."""
        # Set window flags for transparency and always-on-top
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool |
            Qt.WindowType.WindowTransparentForInput  # Click-through
        )
        
        # Set window to fullscreen
        self.showFullScreen()
        
        # Set transparent background
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        
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
        """Paint the overlay content.
        
        Args:
            event: Paint event
        """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw reticle
        self.reticle.draw(painter, time.time())
        
        # Draw status HUD in top-left corner
        if self.status_text or self.current_task:
            self._draw_status_hud(painter)
    
    def _draw_status_hud(self, painter):
        """Draw the status HUD.
        
        Args:
            painter (QPainter): Qt painter
        """
        # Set up font and colors
        font = QFont("Segoe UI", 10)
        painter.setFont(font)
        
        # Background for HUD
        hud_x = 10
        hud_y = 10
        hud_width = 300
        line_height = 20
        
        # Semi-transparent background
        bg_color = QColor(0, 0, 0, 150)
        painter.fillRect(hud_x, hud_y, hud_width, line_height * 5 + 10, bg_color)
        
        # Draw text
        text_color = QColor(255, 255, 255, 255)
        painter.setPen(QPen(text_color))
        
        y_offset = hud_y + 20
        
        if self.current_task:
            painter.drawText(hud_x + 10, y_offset, f"Task: {self.current_task[:40]}...")
            y_offset += line_height
        
        if self.current_step:
            painter.drawText(hud_x + 10, y_offset, f"Step: {self.current_step[:40]}...")
            y_offset += line_height
        
        if self.status_text:
            painter.drawText(hud_x + 10, y_offset, f"Status: {self.status_text}")
            y_offset += line_height
        
        painter.drawText(hud_x + 10, y_offset, f"Response: {self.response_time:.2f}s")
        y_offset += line_height
        
        painter.drawText(hud_x + 10, y_offset, f"Actions: {self.action_count}")
    
    def set_reticle_position(self, x, y, animate=True):
        """Update the reticle position.
        
        Args:
            x (int): X coordinate
            y (int): Y coordinate
            animate (bool): Whether to animate movement
        """
        self.reticle.set_position(x, y, animate)
        self.update()
    
    def set_reticle_state(self, state):
        """Set the reticle state.
        
        Args:
            state (str): Reticle state (idle, thinking, moving, clicking)
        """
        self.reticle.set_state(state)
        self.update()
    
    def set_status(self, text):
        """Update the status text.
        
        Args:
            text (str): Status message to display
        """
        self.status_text = text
        self.update()
    
    def set_task_info(self, task="", step="", response_time=0.0, action_count=0):
        """Update task information in HUD.
        
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
        self.update()
    
    def hide_reticle(self):
        """Hide the reticle."""
        self.reticle.hide()
        self.update()
    
    def show_reticle(self):
        """Show the reticle."""
        self.reticle.show()
        self.update()
    
    def show_overlay(self):
        """Show the overlay."""
        self.show()
    
    def hide_overlay(self):
        """Hide the overlay."""
        self.hide()


def create_overlay():
    """Create and return an overlay instance.
    
    Returns:
        TransparentOverlay: Overlay window instance
    """
    # Create QApplication if not exists
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    # Create TransparentOverlay instance
    overlay = TransparentOverlay()
    
    # Show overlay
    overlay.show()
    
    # Return instance
    return overlay


def run_overlay_app(overlay):
    """Run the Qt application event loop.
    
    Args:
        overlay (TransparentOverlay): Overlay instance
    """
    # Get QApplication instance
    app = QApplication.instance()
    if app is not None:
        # Run QApplication.exec()
        app.exec()

# Made with Bob
