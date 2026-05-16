"""Glowing reticle that predicts next cursor movement.

Dev 3 (Pratham) - UI & Demo
Implements animated reticle with:
- Glowing circle at predicted cursor position
- Smooth movement animation to new positions
- Pulsing/breathing effect for visual appeal
- State-based colors (idle=blue, thinking=orange, moving=green, clicking=red)
- Fade in/out transitions
- Optimized rendering for smooth 60 FPS
- Larger size for better visibility
"""

import math
from PyQt6.QtCore import QPropertyAnimation, QEasingCurve, QPoint, QPointF, Qt
from PyQt6.QtGui import QPainter, QColor, QPen, QRadialGradient, QBrush
from PyQt6.QtWidgets import QWidget


class Reticle:
    """Animated reticle for cursor prediction visualization."""
    
    # Reticle states
    STATE_IDLE = "idle"
    STATE_THINKING = "thinking"
    STATE_MOVING = "moving"
    STATE_CLICKING = "clicking"
    
    # State colors - brighter and more opaque for visibility
    COLORS = {
        STATE_IDLE: QColor(80, 180, 255, 220),       # Bright blue
        STATE_THINKING: QColor(255, 180, 50, 220),    # Bright orange
        STATE_MOVING: QColor(80, 255, 130, 220),      # Bright green
        STATE_CLICKING: QColor(255, 80, 80, 240),     # Bright red
    }
    
    def __init__(self):
        """Initialize the reticle."""
        self.position = QPoint(0, 0)
        self.target_position = QPoint(0, 0)
        self.state = self.STATE_IDLE
        self.radius = 25  # Larger base radius for visibility
        self.pulse_phase = 0
        self.visible = False
        self.interpolation_speed = 0.15  # Smooth interpolation factor
        self.click_animation_phase = 0  # For click ring animation
        
    def draw(self, painter, current_time=0.0):
        """Draw the reticle.
        
        Args:
            painter (QPainter): Qt painter object
            current_time (float): Current time for animations
        """
        if not self.visible:
            return
            
        # Set up painter with anti-aliasing
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Calculate pulsing radius based on time (breathing effect)
        pulse_amplitude = 4
        pulse_speed = 2.5
        pulsing_radius = int(self.radius + pulse_amplitude * math.sin(self.pulse_phase * pulse_speed))
        
        # Get current color based on state
        color = self.get_color()
        
        # Draw outer glow circle (larger, more transparent)
        draw_glowing_circle(painter, self.position, pulsing_radius + 15, color)
        
        # Draw middle glow circle
        draw_glowing_circle(painter, self.position, pulsing_radius + 5, color)
        
        # Draw inner solid circle
        inner_color = QColor(color.red(), color.green(), color.blue(), 80)
        painter.setPen(QPen(color, 2.5))
        painter.setBrush(QBrush(inner_color))
        inner_r = int(pulsing_radius * 0.5)
        painter.drawEllipse(
            self.position.x() - inner_r,
            self.position.y() - inner_r,
            inner_r * 2,
            inner_r * 2
        )
        
        # Draw crosshair lines
        draw_crosshair(painter, self.position, int(pulsing_radius * 1.8), color)
        
        # Draw center dot
        center_color = QColor(255, 255, 255, 200)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(center_color))
        painter.drawEllipse(self.position.x() - 3, self.position.y() - 3, 6, 6)
        
        # Add state-specific effects
        if self.state == self.STATE_CLICKING:
            # Draw expanding ring for click effect
            self.click_animation_phase += 0.15
            ring_expand = 5 + int(10 * abs(math.sin(self.click_animation_phase)))
            click_ring_radius = int(pulsing_radius) + ring_expand
            ring_color = QColor(color.red(), color.green(), color.blue(), 
                               max(50, 200 - ring_expand * 10))
            painter.setPen(QPen(ring_color, 3))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawEllipse(
                self.position.x() - click_ring_radius,
                self.position.y() - click_ring_radius,
                click_ring_radius * 2,
                click_ring_radius * 2
            )
        
        elif self.state == self.STATE_THINKING:
            # Draw rotating dots for thinking effect
            dot_count = 4
            dot_radius = int(pulsing_radius) + 12
            for i in range(dot_count):
                angle = (self.pulse_phase * 3) + (i * 2 * math.pi / dot_count)
                dot_x = self.position.x() + int(dot_radius * math.cos(angle))
                dot_y = self.position.y() + int(dot_radius * math.sin(angle))
                dot_color = QColor(color.red(), color.green(), color.blue(), 180)
                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(QBrush(dot_color))
                painter.drawEllipse(dot_x - 3, dot_y - 3, 6, 6)
    
    def set_position(self, x, y, animate=True):
        """Set the reticle position.
        
        Args:
            x (int): X coordinate
            y (int): Y coordinate
            animate (bool): Whether to animate the movement
        """
        self.target_position = QPoint(x, y)
        if not animate:
            self.position = self.target_position
        self.visible = True
    
    def set_state(self, state):
        """Set the reticle state.
        
        Args:
            state (str): New state (idle, thinking, moving, clicking)
        """
        if state in self.COLORS:
            self.state = state
            if state == self.STATE_CLICKING:
                self.click_animation_phase = 0  # Reset click animation
    
    def update(self, delta_time):
        """Update reticle animation.
        
        Args:
            delta_time (float): Time since last update in seconds
        """
        # Update pulse phase for breathing animation
        self.pulse_phase += delta_time
        
        # Interpolate position towards target (smooth movement)
        if self.position != self.target_position:
            dx = self.target_position.x() - self.position.x()
            dy = self.target_position.y() - self.position.y()
            
            # Apply interpolation
            new_x = self.position.x() + int(dx * self.interpolation_speed)
            new_y = self.position.y() + int(dy * self.interpolation_speed)
            
            self.position = QPoint(new_x, new_y)
            
            # Snap to target if very close
            distance = math.sqrt(dx*dx + dy*dy)
            if distance < 2:
                self.position = self.target_position
    
    def get_color(self):
        """Get the current color based on state.
        
        Returns:
            QColor: Current reticle color
        """
        return self.COLORS.get(self.state, self.COLORS[self.STATE_IDLE])
    
    def hide(self):
        """Hide the reticle."""
        self.visible = False
    
    def show(self):
        """Show the reticle."""
        self.visible = True


def draw_glowing_circle(painter, center, radius, color):
    """Draw a glowing circle with gradient.
    
    Args:
        painter (QPainter): Qt painter
        center (QPoint): Center position
        radius (int): Circle radius
        color (QColor): Base color
    """
    # Create radial gradient from center (QRadialGradient needs QPointF and float)
    center_f = QPointF(float(center.x()), float(center.y()))
    gradient = QRadialGradient(center_f, float(radius))
    
    # Set gradient colors (solid at center, transparent at edge)
    center_color = QColor(color.red(), color.green(), color.blue(), color.alpha())
    edge_color = QColor(color.red(), color.green(), color.blue(), 0)
    
    gradient.setColorAt(0, center_color)
    gradient.setColorAt(0.4, QColor(color.red(), color.green(), color.blue(), int(color.alpha() * 0.7)))
    gradient.setColorAt(0.7, QColor(color.red(), color.green(), color.blue(), int(color.alpha() * 0.3)))
    gradient.setColorAt(1, edge_color)
    
    # Draw circle with gradient brush
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QBrush(gradient))
    r = int(radius)
    painter.drawEllipse(
        center.x() - r,
        center.y() - r,
        r * 2,
        r * 2
    )


def draw_crosshair(painter, center, size, color):
    """Draw crosshair lines.
    
    Args:
        painter (QPainter): Qt painter
        center (QPoint): Center position
        size (int): Crosshair size
        color (QColor): Line color
    """
    # Set pen with color - thicker for visibility
    painter.setPen(QPen(color, 2.5))
    
    # Gap in center
    gap = 10
    
    # Draw horizontal line (left and right segments)
    painter.drawLine(
        center.x() - size, center.y(),
        center.x() - gap, center.y()
    )
    painter.drawLine(
        center.x() + gap, center.y(),
        center.x() + size, center.y()
    )
    
    # Draw vertical line (top and bottom segments)
    painter.drawLine(
        center.x(), center.y() - size,
        center.x(), center.y() - gap
    )
    painter.drawLine(
        center.x(), center.y() + gap,
        center.x(), center.y() + size
    )

# Made with Bob
