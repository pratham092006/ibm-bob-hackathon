"""Simple hand cursor with coordinate tracking.

Custom AI cursor implementation:
- SVG-based pointing hand cursor
- Displays coordinates (X, Y) near the cursor
- No animations, pulsing, or rotating effects
- Clean and minimal design
"""

import math
import os
from PyQt6.QtCore import QPoint, QPointF, Qt, QRectF
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QPolygonF, QFont
from PyQt6.QtSvg import QSvgRenderer


class Reticle:
    """Simple hand cursor with coordinate display."""

    # Reticle states (kept for compatibility)
    STATE_IDLE = "idle"
    STATE_THINKING = "thinking"
    STATE_MOVING = "moving"
    STATE_CLICKING = "clicking"

    def __init__(self):
        self.position = QPoint(0, 0)
        self.target_position = QPoint(0, 0)
        self.state = self.STATE_IDLE
        self.visible = False
        self.interpolation_speed = 0.18
        
        # Load SVG cursor
        svg_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'pointinghand.svg')
        self.svg_renderer = QSvgRenderer(svg_path)
        if not self.svg_renderer.isValid():
            print(f"[WARNING] Failed to load SVG cursor from {svg_path}")
            self.svg_renderer = None
        else:
            print(f"[INFO] SVG cursor loaded successfully from {svg_path}")

    # ------------------------------------------------------------------
    # Drawing
    # ------------------------------------------------------------------

    def draw(self, painter: QPainter, current_time: float = 0.0):
        if not self.visible:
            return

        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        px, py = self.position.x(), self.position.y()

        # Draw hand cursor
        self._draw_hand_cursor(painter, px, py)
        
        # Draw coordinates
        self._draw_coordinates(painter, px, py)

    def _draw_hand_cursor(self, painter: QPainter, px: int, py: int):
        """Draw SVG-based pointing hand cursor."""
        if self.svg_renderer is None or not self.svg_renderer.isValid():
            # Fallback to simple circle if SVG fails to load
            painter.setPen(QPen(QColor(255, 255, 255, 255), 2))
            painter.setBrush(QBrush(QColor(0, 0, 0, 200)))
            painter.drawEllipse(QPoint(px, py), 8, 8)
            return
        
        # SVG cursor size (scale the 32x32 SVG to desired size)
        cursor_size = 32  # Keep original size for clarity
        
        # Calculate position to center the cursor at (px, py)
        # The SVG hotspot should be at the tip of the pointing finger
        # Based on the SVG, the finger tip is roughly at (16, 8) in the 32x32 viewBox
        offset_x = 16
        offset_y = 8
        
        # Define the rectangle where the SVG will be rendered
        svg_rect = QRectF(
            px - offset_x,
            py - offset_y,
            cursor_size,
            cursor_size
        )
        
        # Render the SVG
        self.svg_renderer.render(painter, svg_rect)

    def _draw_coordinates(self, painter: QPainter, px: int, py: int):
        """Draw coordinate display near the cursor."""
        # Format coordinates
        coord_text = f"X: {px}, Y: {py}"
        
        # Set font
        font = QFont("Arial", 10, QFont.Weight.Bold)
        painter.setFont(font)
        
        # Calculate text position (offset from cursor)
        text_x = px + 25
        text_y = py + 5
        
        # Get text dimensions
        metrics = painter.fontMetrics()
        text_width = metrics.horizontalAdvance(coord_text)
        text_height = metrics.height()
        
        # Draw background rectangle (white with slight transparency)
        bg_padding = 4
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(QColor(255, 255, 255, 220)))
        painter.drawRoundedRect(
            text_x - bg_padding,
            text_y - text_height + bg_padding,
            text_width + bg_padding * 2,
            text_height + bg_padding,
            3, 3
        )
        
        # Draw border
        painter.setPen(QPen(QColor(0, 0, 0, 255), 1))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRoundedRect(
            text_x - bg_padding,
            text_y - text_height + bg_padding,
            text_width + bg_padding * 2,
            text_height + bg_padding,
            3, 3
        )
        
        # Draw text
        painter.setPen(QColor(0, 0, 0, 255))
        painter.drawText(text_x, text_y, coord_text)

    # ------------------------------------------------------------------
    # State management
    # ------------------------------------------------------------------

    def set_position(self, x: int, y: int, animate: bool = True):
        self.target_position = QPoint(x, y)
        if not animate:
            self.position = self.target_position
        self.visible = True

    def set_state(self, state: str):
        """Set cursor state (kept for compatibility)."""
        self.state = state

    def update(self, delta_time: float):
        """Update cursor position with smooth interpolation."""
        if self.position != self.target_position:
            dx = self.target_position.x() - self.position.x()
            dy = self.target_position.y() - self.position.y()
            new_x = self.position.x() + int(dx * self.interpolation_speed)
            new_y = self.position.y() + int(dy * self.interpolation_speed)
            self.position = QPoint(new_x, new_y)
            if math.sqrt(dx * dx + dy * dy) < 2:
                self.position = self.target_position

    def hide(self):
        self.visible = False

    def show(self):
        self.visible = True


# Made with Bob
