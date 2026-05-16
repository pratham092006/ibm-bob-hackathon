"""Glowing reticle that predicts next cursor movement.

Dev 3 (Pratham) - UI & Demo
Production-level implementation with:
- Glowing circle at predicted cursor position
- Smooth movement animation with configurable easing
- Pulsing/breathing effect for visual appeal
- State-based colors (idle=blue, thinking=orange, moving=green, clicking=red)
- Fade in/out transitions
- Optimized rendering for smooth 60 FPS
- Comprehensive error handling and logging
- Performance monitoring and optimization
- Configurable visual themes
- Accessibility features
"""

import math
import time
from typing import Optional, Tuple
from PyQt6.QtCore import QPoint, QPointF, Qt
from PyQt6.QtGui import QPainter, QColor, QPen, QRadialGradient, QBrush

from .logger import get_logger, log_performance
from .exceptions import ReticleException, ErrorCode, handle_exception
from .config_ui import get_config


# Initialize logger
logger = get_logger("reticle")


class EasingFunction:
    """Easing functions for smooth animations."""
    
    @staticmethod
    def ease_out_cubic(t: float) -> float:
        """Cubic ease-out function.
        
        Args:
            t: Time value (0.0 to 1.0)
            
        Returns:
            Eased value
        """
        return 1 - pow(1 - t, 3)
    
    @staticmethod
    def ease_in_out_quad(t: float) -> float:
        """Quadratic ease-in-out function.
        
        Args:
            t: Time value (0.0 to 1.0)
            
        Returns:
            Eased value
        """
        return 2 * t * t if t < 0.5 else 1 - pow(-2 * t + 2, 2) / 2
    
    @staticmethod
    def linear(t: float) -> float:
        """Linear interpolation (no easing).
        
        Args:
            t: Time value (0.0 to 1.0)
            
        Returns:
            Same value
        """
        return t


class Reticle:
    """Animated reticle for cursor prediction visualization with production features."""
    
    # Reticle states
    STATE_IDLE = "idle"
    STATE_THINKING = "thinking"
    STATE_MOVING = "moving"
    STATE_CLICKING = "clicking"
    
    def __init__(self):
        """Initialize the reticle with production features."""
        try:
            logger.info("Initializing reticle component")
            
            # Load configuration
            self.config = get_config().reticle
            
            # Position tracking
            self.position = QPoint(0, 0)
            self.target_position = QPoint(0, 0)
            self.state = self.STATE_IDLE
            
            # Animation state
            self.pulse_phase = 0.0
            self.visible = False
            self.fade_alpha = 0.0
            self.target_fade_alpha = 0.0
            
            # Performance tracking
            self.frame_count = 0
            self.last_perf_check = time.time()
            self.render_times = []
            
            # State colors from config
            self._update_colors_from_config()
            
            # Easing function
            self.easing_func = EasingFunction.ease_out_cubic
            
            logger.info("Reticle initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize reticle: {e}")
            raise ReticleException(
                "Failed to initialize reticle",
                ErrorCode.INITIALIZATION_ERROR,
                {"error": str(e)}
            )
    
    def _update_colors_from_config(self):
        """Update colors from configuration."""
        try:
            self.COLORS = {
                self.STATE_IDLE: QColor(*self.config.color_idle),
                self.STATE_THINKING: QColor(*self.config.color_thinking),
                self.STATE_MOVING: QColor(*self.config.color_moving),
                self.STATE_CLICKING: QColor(*self.config.color_clicking),
            }
        except Exception as e:
            logger.warning(f"Failed to load colors from config, using defaults: {e}")
            # Fallback to default colors
            self.COLORS = {
                self.STATE_IDLE: QColor(100, 200, 255, 180),
                self.STATE_THINKING: QColor(255, 200, 100, 180),
                self.STATE_MOVING: QColor(100, 255, 150, 180),
                self.STATE_CLICKING: QColor(255, 100, 100, 200),
            }
    
    def draw(self, painter: Optional[QPainter], current_time: float = 0) -> None:
        """Draw the reticle with error handling and performance monitoring.
        
        Args:
            painter: Qt painter object
            current_time: Current time for animations
        """
        if painter is None or not self.visible or self.fade_alpha <= 0:
            return
        
        start_time = time.time()
        
        try:
            # Set up painter with anti-aliasing (if enabled)
            if self.config.enable_antialiasing:
                painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            
            # Calculate pulsing radius with configurable parameters
            if self.config.animation_enabled:
                pulsing_radius = self._calculate_pulsing_radius()
            else:
                pulsing_radius = self.config.base_radius
            
            # Get current color based on state
            color = self.get_color()
            
            # Apply fade alpha
            color.setAlpha(int(color.alpha() * self.fade_alpha))
            
            # Draw glow layers (configurable count)
            for i in range(self.config.glow_layers):
                layer_radius = pulsing_radius + (10 * (i + 1))
                self._draw_glowing_circle(painter, self.position, layer_radius, color, i)
            
            # Draw inner solid circle
            self._draw_inner_circle(painter, pulsing_radius, color)
            
            # Draw crosshair lines
            self._draw_crosshair(painter, self.position, int(pulsing_radius * 1.5), color)
            
            # Add state-specific effects
            if self.state == self.STATE_CLICKING:
                self._draw_click_effect(painter, pulsing_radius, color)
            
            # Track performance
            self._track_performance(start_time)
            
        except Exception as e:
            logger.error(f"Error drawing reticle: {e}")
            if not handle_exception(
                ReticleException(
                    "Failed to render reticle",
                    ErrorCode.RETICLE_RENDER_ERROR,
                    {"position": (self.position.x(), self.position.y())}
                ),
                logger,
                "reticle"
            ):
                # If not recoverable, disable rendering
                self.visible = False
    
    def _calculate_pulsing_radius(self) -> float:
        """Calculate pulsing radius with smooth animation.
        
        Returns:
            Current pulsing radius
        """
        try:
            pulse_value = math.sin(self.pulse_phase * self.config.pulse_speed)
            return self.config.base_radius + self.config.pulse_amplitude * pulse_value
        except Exception as e:
            logger.warning(f"Error calculating pulse: {e}")
            return self.config.base_radius
    
    def _draw_glowing_circle(
        self,
        painter: QPainter,
        center: QPoint,
        radius: float,
        color: QColor,
        layer_index: int
    ) -> None:
        """Draw a glowing circle layer.
        
        Args:
            painter: Qt painter
            center: Center position
            radius: Circle radius
            color: Base color
            layer_index: Layer index (0 = innermost)
        """
        try:
            # Create radial gradient from center (convert QPoint to QPointF)
            center_f = QPointF(center.x(), center.y())
            gradient = QRadialGradient(center_f, radius)
            
            # Calculate alpha based on layer
            alpha_multiplier = 1.0 - (layer_index * 0.3)
            
            # Set gradient colors
            center_color = QColor(
                color.red(),
                color.green(),
                color.blue(),
                int(color.alpha() * alpha_multiplier)
            )
            edge_color = QColor(color.red(), color.green(), color.blue(), 0)
            
            gradient.setColorAt(0, center_color)
            gradient.setColorAt(0.5, QColor(
                color.red(),
                color.green(),
                color.blue(),
                int(color.alpha() * alpha_multiplier * 0.6)
            ))
            gradient.setColorAt(1, edge_color)
            
            # Draw circle with gradient brush
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(gradient))
            painter.drawEllipse(
                center.x() - int(radius),
                center.y() - int(radius),
                int(radius * 2),
                int(radius * 2)
            )
        except Exception as e:
            logger.debug(f"Error drawing glow layer {layer_index}: {e}")
    
    def _draw_inner_circle(self, painter: QPainter, radius: float, color: QColor) -> None:
        """Draw the inner solid circle.
        
        Args:
            painter: Qt painter
            radius: Circle radius
            color: Circle color
        """
        try:
            painter.setPen(QPen(color, 2))
            painter.setBrush(QBrush(QColor(
                color.red(),
                color.green(),
                color.blue(),
                int(color.alpha() * 0.3)
            )))
            painter.drawEllipse(
                self.position.x() - int(radius * 0.5),
                self.position.y() - int(radius * 0.5),
                int(radius),
                int(radius)
            )
        except Exception as e:
            logger.debug(f"Error drawing inner circle: {e}")
    
    def _draw_crosshair(
        self,
        painter: QPainter,
        center: QPoint,
        size: int,
        color: QColor
    ) -> None:
        """Draw crosshair lines.
        
        Args:
            painter: Qt painter
            center: Center position
            size: Crosshair size
            color: Line color
        """
        try:
            painter.setPen(QPen(color, 2))
            gap = 8
            
            # Horizontal line
            painter.drawLine(center.x() - size, center.y(), center.x() - gap, center.y())
            painter.drawLine(center.x() + gap, center.y(), center.x() + size, center.y())
            
            # Vertical line
            painter.drawLine(center.x(), center.y() - size, center.x(), center.y() - gap)
            painter.drawLine(center.x(), center.y() + gap, center.x(), center.y() + size)
        except Exception as e:
            logger.debug(f"Error drawing crosshair: {e}")
    
    def _draw_click_effect(self, painter: QPainter, radius: float, color: QColor) -> None:
        """Draw click effect animation.
        
        Args:
            painter: Qt painter
            radius: Base radius
            color: Effect color
        """
        try:
            click_ring_radius = int(radius + 5)
            painter.setPen(QPen(color, 3))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawEllipse(
                self.position.x() - click_ring_radius,
                self.position.y() - click_ring_radius,
                click_ring_radius * 2,
                click_ring_radius * 2
            )
        except Exception as e:
            logger.debug(f"Error drawing click effect: {e}")
    
    def _track_performance(self, start_time: float) -> None:
        """Track rendering performance.
        
        Args:
            start_time: Render start time
        """
        try:
            render_time = time.time() - start_time
            self.render_times.append(render_time)
            
            # Keep only last 60 frames
            if len(self.render_times) > 60:
                self.render_times.pop(0)
            
            self.frame_count += 1
            
            # Log performance every 5 seconds
            if time.time() - self.last_perf_check > 5.0:
                avg_render_time = sum(self.render_times) / len(self.render_times)
                fps = self.frame_count / 5.0
                
                log_performance("reticle", "render", avg_render_time)
                logger.debug(f"Reticle FPS: {fps:.1f}, Avg render: {avg_render_time*1000:.2f}ms")
                
                self.frame_count = 0
                self.last_perf_check = time.time()
                
                # Warn if performance is degrading
                if avg_render_time > 0.016:  # More than 16ms (60 FPS threshold)
                    logger.warning(f"Reticle render time exceeds 16ms: {avg_render_time*1000:.2f}ms")
        except Exception as e:
            logger.debug(f"Error tracking performance: {e}")
    
    def set_position(self, x: int, y: int, animate: bool = True) -> None:
        """Set the reticle position with validation.
        
        Args:
            x: X coordinate
            y: Y coordinate
            animate: Whether to animate the movement
        """
        try:
            # Validate coordinates
            if not isinstance(x, (int, float)) or not isinstance(y, (int, float)):
                raise ValueError(f"Invalid coordinates: x={x}, y={y}")
            
            self.target_position = QPoint(int(x), int(y))
            
            if not animate or not self.config.smooth_movement:
                self.position = self.target_position
            
            if not self.visible:
                self.visible = True
                self.target_fade_alpha = 1.0
            
            logger.debug(f"Reticle position set to ({x}, {y}), animate={animate}")
            
        except Exception as e:
            logger.error(f"Error setting reticle position: {e}")
            handle_exception(
                ReticleException(
                    "Failed to set reticle position",
                    ErrorCode.RETICLE_STATE_ERROR,
                    {"x": x, "y": y, "error": str(e)}
                ),
                logger,
                "reticle"
            )
    
    def set_state(self, state: str) -> None:
        """Set the reticle state with validation.
        
        Args:
            state: New state (idle, thinking, moving, clicking)
        """
        try:
            if state not in self.COLORS:
                logger.warning(f"Invalid reticle state: {state}, using idle")
                state = self.STATE_IDLE
            
            if self.state != state:
                logger.debug(f"Reticle state changed: {self.state} -> {state}")
                self.state = state
                
        except Exception as e:
            logger.error(f"Error setting reticle state: {e}")
            self.state = self.STATE_IDLE
    
    def update(self, delta_time: float) -> None:
        """Update reticle animation with error handling.
        
        Args:
            delta_time: Time since last update in seconds
        """
        try:
            # Validate delta_time
            if delta_time < 0 or delta_time > 1.0:
                logger.warning(f"Invalid delta_time: {delta_time}, clamping")
                delta_time = max(0, min(delta_time, 1.0))
            
            # Update pulse phase for breathing animation
            if self.config.animation_enabled:
                self.pulse_phase += delta_time
                
                # Prevent overflow
                if self.pulse_phase > 1000:
                    self.pulse_phase = 0
            
            # Update fade alpha
            if self.fade_alpha != self.target_fade_alpha:
                fade_speed = 5.0 * delta_time
                if abs(self.target_fade_alpha - self.fade_alpha) < fade_speed:
                    self.fade_alpha = self.target_fade_alpha
                else:
                    self.fade_alpha += fade_speed if self.target_fade_alpha > self.fade_alpha else -fade_speed
            
            # Interpolate position towards target
            if self.config.smooth_movement and self.position != self.target_position:
                dx = self.target_position.x() - self.position.x()
                dy = self.target_position.y() - self.position.y()
                
                # Apply interpolation with easing
                t = self.config.interpolation_speed
                eased_t = self.easing_func(t)
                
                new_x = self.position.x() + int(dx * eased_t)
                new_y = self.position.y() + int(dy * eased_t)
                
                self.position = QPoint(new_x, new_y)
                
                # Snap to target if very close
                distance = math.sqrt(dx*dx + dy*dy)
                if distance < 2:
                    self.position = self.target_position
                    
        except Exception as e:
            logger.error(f"Error updating reticle: {e}")
            handle_exception(
                ReticleException(
                    "Failed to update reticle animation",
                    ErrorCode.RETICLE_ANIMATION_ERROR,
                    {"delta_time": delta_time, "error": str(e)}
                ),
                logger,
                "reticle"
            )
    
    def get_color(self) -> QColor:
        """Get the current color based on state.
        
        Returns:
            Current reticle color
        """
        try:
            return self.COLORS.get(self.state, self.COLORS[self.STATE_IDLE])
        except Exception as e:
            logger.warning(f"Error getting color: {e}")
            return QColor(100, 200, 255, 180)
    
    def hide(self) -> None:
        """Hide the reticle with fade out."""
        try:
            logger.debug("Hiding reticle")
            self.target_fade_alpha = 0.0
            # Don't set visible=False immediately, let fade complete
        except Exception as e:
            logger.error(f"Error hiding reticle: {e}")
            self.visible = False
    
    def show(self) -> None:
        """Show the reticle with fade in."""
        try:
            logger.debug("Showing reticle")
            self.visible = True
            self.target_fade_alpha = 1.0
        except Exception as e:
            logger.error(f"Error showing reticle: {e}")
            self.visible = True
            self.fade_alpha = 1.0
    
    def reload_config(self) -> None:
        """Reload configuration from config manager."""
        try:
            logger.info("Reloading reticle configuration")
            self.config = get_config().reticle
            self._update_colors_from_config()
            logger.info("Reticle configuration reloaded")
        except Exception as e:
            logger.error(f"Error reloading config: {e}")
    
    def get_performance_stats(self) -> dict:
        """Get performance statistics.
        
        Returns:
            Dictionary with performance metrics
        """
        try:
            if not self.render_times:
                return {"avg_render_time": 0, "fps": 0}
            
            avg_render_time = sum(self.render_times) / len(self.render_times)
            fps = 1.0 / avg_render_time if avg_render_time > 0 else 0
            
            return {
                "avg_render_time": avg_render_time,
                "fps": fps,
                "frame_count": self.frame_count
            }
        except Exception as e:
            logger.error(f"Error getting performance stats: {e}")
            return {"avg_render_time": 0, "fps": 0}
    
    def __del__(self):
        """Cleanup resources."""
        try:
            logger.info("Reticle component destroyed")
        except:
            pass


# Made with Bob
