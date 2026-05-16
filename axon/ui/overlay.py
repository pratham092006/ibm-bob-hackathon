"""Floating cursor widget with status label.

Dev 3 (Pratham) - UI & Demo
Production-level implementation with:
- PyQt6 window that covers entire screen
- Transparent and click-through window
- Always on top
- Displays reticle at predicted cursor position
- Shows status messages and agent state
- Handles multi-monitor setups
- Optimized for performance (minimal CPU usage)
- Toggleable visibility
- Comprehensive error handling and logging
- Performance monitoring with FPS counter
- Memory usage tracking
- Configurable HUD display
"""

from typing import Optional
import sys
import time
import psutil
from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtCore import Qt, QTimer, QPoint
from PyQt6.QtGui import QPainter, QColor, QPen, QFont, QPaintEvent

from .reticle import Reticle
from .logger import get_logger, log_performance
from .exceptions import OverlayException, ErrorCode, handle_exception
from .config_ui import get_config


# Initialize logger
logger = get_logger("overlay")


class PerformanceMonitor:
    """Monitor overlay performance metrics."""
    
    def __init__(self):
        """Initialize performance monitor."""
        self.frame_times = []
        self.frame_count = 0
        self.last_fps_update = time.time()
        self.current_fps = 0.0
        self.process = psutil.Process()
        self.last_memory_check = time.time()
        self.memory_usage_mb = 0.0
    
    def record_frame(self, frame_time: float):
        """Record a frame render time.
        
        Args:
            frame_time: Frame render time in seconds
        """
        self.frame_times.append(frame_time)
        self.frame_count += 1
        
        # Keep only last 60 frames
        if len(self.frame_times) > 60:
            self.frame_times.pop(0)
        
        # Update FPS every second
        current_time = time.time()
        if current_time - self.last_fps_update >= 1.0:
            elapsed = current_time - self.last_fps_update
            self.current_fps = self.frame_count / elapsed
            self.frame_count = 0
            self.last_fps_update = current_time
    
    def get_fps(self) -> float:
        """Get current FPS.
        
        Returns:
            Current frames per second
        """
        return self.current_fps
    
    def get_avg_frame_time(self) -> float:
        """Get average frame time.
        
        Returns:
            Average frame time in milliseconds
        """
        if not self.frame_times:
            return 0.0
        return (sum(self.frame_times) / len(self.frame_times)) * 1000
    
    def update_memory_usage(self):
        """Update memory usage statistics."""
        try:
            current_time = time.time()
            if current_time - self.last_memory_check >= 5.0:
                memory_info = self.process.memory_info()
                self.memory_usage_mb = memory_info.rss / (1024 * 1024)
                self.last_memory_check = current_time
        except Exception as e:
            logger.debug(f"Error updating memory usage: {e}")
    
    def get_memory_usage(self) -> float:
        """Get current memory usage.
        
        Returns:
            Memory usage in MB
        """
        return self.memory_usage_mb


class TransparentOverlay(QWidget):
    """Transparent fullscreen overlay for visual feedback with production features."""
    
    def __init__(self):
        """Initialize the overlay window with error handling."""
        try:
            logger.info("Initializing overlay component")
            super().__init__()
            
            # Load configuration
            self.config = get_config().overlay
            
            # Initialize reticle
            self.reticle = Reticle()
            
            # Status information
            self.status_text = ""
            self.current_task = ""
            self.current_step = ""
            self.response_time = 0.0
            self.action_count = 0
            
            # Performance monitoring
            self.perf_monitor = PerformanceMonitor()
            self.last_update_time = time.time()
            
            # Frame timing
            self.frame_start_time = 0.0
            
            # Initialize UI
            self.init_ui()
            
            logger.info("Overlay initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize overlay: {e}")
            raise OverlayException(
                "Failed to initialize overlay",
                ErrorCode.OVERLAY_CREATION_ERROR,
                {"error": str(e)}
            )
    
    def init_ui(self):
        """Set up the overlay window properties with error handling."""
        try:
            logger.debug("Setting up overlay UI")
            
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
            
            # Set up update timer for smooth animation
            self.update_timer = QTimer()
            self.update_timer.timeout.connect(self._on_timer_update)
            self.update_timer.start(self.config.update_interval_ms)
            
            logger.debug("Overlay UI setup complete")
            
        except Exception as e:
            logger.error(f"Failed to setup overlay UI: {e}")
            raise OverlayException(
                "Failed to setup overlay UI",
                ErrorCode.OVERLAY_CREATION_ERROR,
                {"error": str(e)}
            )
    
    def _on_timer_update(self):
        """Handle timer update for animations with error handling."""
        try:
            current_time = time.time()
            delta_time = current_time - self.last_update_time
            self.last_update_time = current_time
            
            # Update reticle animation
            self.reticle.update(delta_time)
            
            # Update performance monitoring
            self.perf_monitor.update_memory_usage()
            
            # Trigger repaint
            self.update()
            
        except Exception as e:
            logger.error(f"Error in timer update: {e}")
            handle_exception(
                OverlayException(
                    "Timer update failed",
                    ErrorCode.OVERLAY_UPDATE_ERROR,
                    {"error": str(e)}
                ),
                logger,
                "overlay"
            )
    
    def paintEvent(self, a0: Optional[QPaintEvent]):
        """Paint the overlay content with error handling and performance tracking.
        
        Args:
            a0: Paint event
        """
        if a0 is None:
            return
        self.frame_start_time = time.time()
        
        try:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            
            # Draw reticle
            self.reticle.draw(painter, time.time())
            
            # Draw HUD if enabled
            if self.config.show_hud and (self.status_text or self.current_task):
                self._draw_status_hud(painter)
            
            # Draw debug info if enabled
            if self.config.show_fps_counter or self.config.show_performance_metrics:
                self._draw_debug_info(painter)
            
            # Record frame time
            frame_time = time.time() - self.frame_start_time
            self.perf_monitor.record_frame(frame_time)
            
            # Log performance warnings
            if frame_time > 0.033:  # More than 33ms (30 FPS threshold)
                logger.warning(f"Overlay frame time exceeded 33ms: {frame_time*1000:.2f}ms")
            
        except Exception as e:
            logger.error(f"Error painting overlay: {e}")
            handle_exception(
                OverlayException(
                    "Failed to render overlay",
                    ErrorCode.OVERLAY_RENDER_ERROR,
                    {"error": str(e)}
                ),
                logger,
                "overlay"
            )
    
    def _draw_status_hud(self, painter: QPainter):
        """Draw the status HUD with error handling.
        
        Args:
            painter: Qt painter
        """
        try:
            # Set up font and colors
            font = QFont("Segoe UI", self.config.hud_font_size)
            painter.setFont(font)
            
            # Calculate HUD position based on config
            hud_x, hud_y = self._get_hud_position()
            hud_width = 300
            line_height = 20
            
            # Count lines to draw
            line_count = 0
            if self.current_task:
                line_count += 1
            if self.current_step:
                line_count += 1
            if self.status_text:
                line_count += 1
            line_count += 2  # Response time and action count
            
            # Semi-transparent background
            bg_color = QColor(0, 0, 0, self.config.hud_opacity)
            painter.fillRect(
                hud_x,
                hud_y,
                hud_width,
                line_height * line_count + 10,
                bg_color
            )
            
            # Draw text
            text_color = QColor(255, 255, 255, 255)
            painter.setPen(QPen(text_color))
            
            y_offset = hud_y + 20
            
            if self.current_task:
                task_text = self.current_task[:40] + "..." if len(self.current_task) > 40 else self.current_task
                painter.drawText(hud_x + 10, y_offset, f"Task: {task_text}")
                y_offset += line_height
            
            if self.current_step:
                step_text = self.current_step[:40] + "..." if len(self.current_step) > 40 else self.current_step
                painter.drawText(hud_x + 10, y_offset, f"Step: {step_text}")
                y_offset += line_height
            
            if self.status_text:
                painter.drawText(hud_x + 10, y_offset, f"Status: {self.status_text}")
                y_offset += line_height
            
            painter.drawText(hud_x + 10, y_offset, f"Response: {self.response_time:.2f}s")
            y_offset += line_height
            
            painter.drawText(hud_x + 10, y_offset, f"Actions: {self.action_count}")
            
        except Exception as e:
            logger.debug(f"Error drawing HUD: {e}")
    
    def _draw_debug_info(self, painter: QPainter):
        """Draw debug information overlay.
        
        Args:
            painter: Qt painter
        """
        try:
            font = QFont("Consolas", 9)
            painter.setFont(font)
            
            # Position in top-right corner
            x = self.width() - 250
            y = 20
            line_height = 15
            
            # Background
            bg_color = QColor(0, 0, 0, 180)
            painter.fillRect(x - 10, y - 10, 240, line_height * 5 + 10, bg_color)
            
            # Text
            text_color = QColor(0, 255, 0, 255)
            painter.setPen(QPen(text_color))
            
            if self.config.show_fps_counter:
                fps = self.perf_monitor.get_fps()
                painter.drawText(x, y, f"FPS: {fps:.1f}")
                y += line_height
            
            if self.config.show_performance_metrics:
                avg_frame_time = self.perf_monitor.get_avg_frame_time()
                painter.drawText(x, y, f"Frame Time: {avg_frame_time:.2f}ms")
                y += line_height
                
                memory_mb = self.perf_monitor.get_memory_usage()
                painter.drawText(x, y, f"Memory: {memory_mb:.1f}MB")
                y += line_height
                
                # Reticle stats
                reticle_stats = self.reticle.get_performance_stats()
                painter.drawText(x, y, f"Reticle FPS: {reticle_stats.get('fps', 0):.1f}")
                y += line_height
                
                painter.drawText(x, y, f"Reticle Time: {reticle_stats.get('avg_render_time', 0)*1000:.2f}ms")
            
        except Exception as e:
            logger.debug(f"Error drawing debug info: {e}")
    
    def _get_hud_position(self) -> tuple:
        """Get HUD position based on configuration.
        
        Returns:
            Tuple of (x, y) coordinates
        """
        try:
            margin = 10
            
            if self.config.hud_position == "top_left":
                return (margin, margin)
            elif self.config.hud_position == "top_right":
                return (self.width() - 310, margin)
            elif self.config.hud_position == "bottom_left":
                return (margin, self.height() - 150)
            elif self.config.hud_position == "bottom_right":
                return (self.width() - 310, self.height() - 150)
            else:
                return (margin, margin)
        except Exception as e:
            logger.debug(f"Error getting HUD position: {e}")
            return (10, 10)
    
    def set_reticle_position(self, x: int, y: int, animate: bool = True):
        """Update the reticle position with validation.
        
        Args:
            x: X coordinate
            y: Y coordinate
            animate: Whether to animate movement
        """
        try:
            self.reticle.set_position(x, y, animate)
            self.update()
        except Exception as e:
            logger.error(f"Error setting reticle position: {e}")
    
    def set_reticle_state(self, state: str):
        """Set the reticle state with validation.
        
        Args:
            state: Reticle state (idle, thinking, moving, clicking)
        """
        try:
            self.reticle.set_state(state)
            self.update()
        except Exception as e:
            logger.error(f"Error setting reticle state: {e}")
    
    def set_status(self, text: str):
        """Update the status text with validation.
        
        Args:
            text: Status message to display
        """
        try:
            if not isinstance(text, str):
                text = str(text)
            self.status_text = text
            logger.debug(f"Status updated: {text}")
            self.update()
        except Exception as e:
            logger.error(f"Error setting status: {e}")
    
    def set_task_info(
        self,
        task: str = "",
        step: str = "",
        response_time: float = 0.0,
        action_count: int = 0
    ):
        """Update task information in HUD with validation.
        
        Args:
            task: Current task description
            step: Current step description
            response_time: Response time in seconds
            action_count: Number of actions performed
        """
        try:
            self.current_task = str(task) if task else ""
            self.current_step = str(step) if step else ""
            self.response_time = float(response_time) if response_time else 0.0
            self.action_count = int(action_count) if action_count else 0
            
            logger.debug(f"Task info updated: task={task[:30]}..., step={step[:30]}...")
            self.update()
        except Exception as e:
            logger.error(f"Error setting task info: {e}")
    
    def hide_reticle(self):
        """Hide the reticle."""
        try:
            self.reticle.hide()
            self.update()
        except Exception as e:
            logger.error(f"Error hiding reticle: {e}")
    
    def show_reticle(self):
        """Show the reticle."""
        try:
            self.reticle.show()
            self.update()
        except Exception as e:
            logger.error(f"Error showing reticle: {e}")
    
    def show_overlay(self):
        """Show the overlay."""
        try:
            logger.info("Showing overlay")
            self.show()
        except Exception as e:
            logger.error(f"Error showing overlay: {e}")
    
    def hide_overlay(self):
        """Hide the overlay."""
        try:
            logger.info("Hiding overlay")
            self.hide()
        except Exception as e:
            logger.error(f"Error hiding overlay: {e}")
    
    def reload_config(self):
        """Reload configuration from config manager."""
        try:
            logger.info("Reloading overlay configuration")
            self.config = get_config().overlay
            self.reticle.reload_config()
            
            # Update timer interval if changed
            self.update_timer.setInterval(self.config.update_interval_ms)
            
            logger.info("Overlay configuration reloaded")
        except Exception as e:
            logger.error(f"Error reloading config: {e}")
    
    def get_performance_stats(self) -> dict:
        """Get performance statistics.
        
        Returns:
            Dictionary with performance metrics
        """
        try:
            return {
                "fps": self.perf_monitor.get_fps(),
                "avg_frame_time": self.perf_monitor.get_avg_frame_time(),
                "memory_mb": self.perf_monitor.get_memory_usage(),
                "reticle_stats": self.reticle.get_performance_stats()
            }
        except Exception as e:
            logger.error(f"Error getting performance stats: {e}")
            return {}
    
    def __del__(self):
        """Cleanup resources."""
        try:
            logger.info("Overlay component destroyed")
            if hasattr(self, 'update_timer'):
                self.update_timer.stop()
        except:
            pass


def create_overlay() -> TransparentOverlay:
    """Create and return an overlay instance with error handling.
    
    Returns:
        TransparentOverlay: Overlay window instance
        
    Raises:
        OverlayException: If overlay creation fails
    """
    try:
        logger.info("Creating overlay instance")
        
        # Create QApplication if not exists
        app = QApplication.instance()
        if app is None:
            logger.debug("Creating new QApplication instance")
            app = QApplication(sys.argv)
        
        # Create TransparentOverlay instance
        overlay = TransparentOverlay()
        
        # Show overlay
        overlay.show()
        
        logger.info("Overlay created successfully")
        return overlay
        
    except Exception as e:
        logger.error(f"Failed to create overlay: {e}")
        raise OverlayException(
            "Failed to create overlay",
            ErrorCode.OVERLAY_CREATION_ERROR,
            {"error": str(e)}
        )


def run_overlay_app(overlay: TransparentOverlay):
    """Run the Qt application event loop with error handling.
    
    Args:
        overlay: Overlay instance
    """
    try:
        logger.info("Starting overlay application event loop")
        
        # Get QApplication instance
        app = QApplication.instance()
        if app is not None:
            # Run QApplication.exec()
            app.exec()
        else:
            logger.warning("No QApplication instance found")
            
    except Exception as e:
        logger.error(f"Error running overlay app: {e}")
        raise OverlayException(
            "Failed to run overlay application",
            ErrorCode.OVERLAY_UPDATE_ERROR,
            {"error": str(e)}
        )




# Made with Bob
