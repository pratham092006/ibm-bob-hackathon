"""Centralized UI configuration for AXON.

Dev 3 (Pratham) - UI & Demo
Provides configuration management with:
- Centralized UI settings
- User preferences
- Theme settings
- Performance tuning options
- Environment variable support
- Configuration validation
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum


class Theme(Enum):
    """Visual themes for UI components."""
    DEFAULT = "default"
    HIGH_CONTRAST = "high_contrast"
    DARK = "dark"
    LIGHT = "light"


class PerformanceMode(Enum):
    """Performance modes for UI rendering."""
    HIGH_QUALITY = "high_quality"
    BALANCED = "balanced"
    PERFORMANCE = "performance"
    MINIMAL = "minimal"


@dataclass
class ReticleConfig:
    """Configuration for reticle component."""
    
    # Visual settings
    base_radius: int = 20
    pulse_amplitude: int = 3
    pulse_speed: float = 2.0
    glow_layers: int = 3
    
    # Animation settings
    interpolation_speed: float = 0.15
    animation_enabled: bool = True
    smooth_movement: bool = True
    
    # Colors (RGBA)
    color_idle: tuple = (100, 200, 255, 180)
    color_thinking: tuple = (255, 200, 100, 180)
    color_moving: tuple = (100, 255, 150, 180)
    color_clicking: tuple = (255, 100, 100, 200)
    
    # Performance
    max_fps: int = 60
    enable_antialiasing: bool = True
    
    # Accessibility
    high_contrast_mode: bool = False
    reduced_motion: bool = False


@dataclass
class OverlayConfig:
    """Configuration for overlay component."""
    
    # Window settings
    fullscreen: bool = True
    always_on_top: bool = True
    click_through: bool = True
    
    # Update settings
    update_interval_ms: int = 16  # ~60 FPS
    
    # HUD settings
    show_hud: bool = True
    hud_position: str = "top_left"  # top_left, top_right, bottom_left, bottom_right
    hud_opacity: int = 150
    hud_font_size: int = 10
    
    # Performance
    enable_vsync: bool = True
    max_fps: int = 60
    
    # Debug
    show_fps_counter: bool = False
    show_performance_metrics: bool = False


@dataclass
class InputDialogConfig:
    """Configuration for input dialog component."""
    
    # Window settings
    width: int = 500
    height: int = 200
    draggable: bool = True
    
    # Voice settings
    voice_enabled: bool = True
    whisper_model: str = "base"  # tiny, base, small, medium, large
    whisper_device: str = "cpu"  # cpu, cuda
    
    # Input settings
    max_input_length: int = 500
    enable_history: bool = True
    history_size: int = 10
    
    # Visual settings
    font_size: int = 11
    border_radius: int = 10
    opacity: int = 240


@dataclass
class TrayConfig:
    """Configuration for tray icon component."""
    
    # Icon settings
    icon_size: int = 64
    update_interval_ms: int = 100
    
    # Notification settings
    enable_notifications: bool = True
    notification_duration: int = 5  # seconds
    
    # Menu settings
    show_status_in_menu: bool = True
    show_quick_actions: bool = True


@dataclass
class UIConfig:
    """Main UI configuration."""
    
    # General settings
    theme: Theme = Theme.DEFAULT
    performance_mode: PerformanceMode = PerformanceMode.BALANCED
    
    # Logging
    log_level: str = "INFO"
    enable_debug_mode: bool = False
    
    # Multi-monitor
    primary_monitor_only: bool = False
    monitor_index: int = 0
    
    def __post_init__(self):
        """Initialize component configs."""
        self.reticle = ReticleConfig()
        self.overlay = OverlayConfig()
        self.input_dialog = InputDialogConfig()
        self.tray = TrayConfig()


class ConfigManager:
    """Manages UI configuration with persistence."""
    
    _instance: Optional['ConfigManager'] = None
    
    def __new__(cls):
        """Singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize config manager."""
        if not hasattr(self, '_initialized'):
            self.config = UIConfig()
            self.config_file = Path("axon/config/ui_config.json")
            self._initialized = True
            self._load_config()
            self._apply_environment_overrides()
    
    def _load_config(self):
        """Load configuration from file."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    data = json.load(f)
                    self._apply_config_dict(data)
            except Exception as e:
                print(f"Warning: Failed to load config: {e}")
    
    def _apply_config_dict(self, data: Dict[str, Any]):
        """Apply configuration from dictionary."""
        # Apply theme
        if 'theme' in data:
            try:
                self.config.theme = Theme(data['theme'])
            except ValueError:
                pass
        
        # Apply performance mode
        if 'performance_mode' in data:
            try:
                self.config.performance_mode = PerformanceMode(data['performance_mode'])
            except ValueError:
                pass
        
        # Apply component configs
        if 'reticle' in data:
            for key, value in data['reticle'].items():
                if hasattr(self.config.reticle, key):
                    setattr(self.config.reticle, key, value)
        
        if 'overlay' in data:
            for key, value in data['overlay'].items():
                if hasattr(self.config.overlay, key):
                    setattr(self.config.overlay, key, value)
        
        if 'input_dialog' in data:
            for key, value in data['input_dialog'].items():
                if hasattr(self.config.input_dialog, key):
                    setattr(self.config.input_dialog, key, value)
        
        if 'tray' in data:
            for key, value in data['tray'].items():
                if hasattr(self.config.tray, key):
                    setattr(self.config.tray, key, value)
    
    def _apply_environment_overrides(self):
        """Apply configuration overrides from environment variables."""
        # Debug mode
        if os.getenv('AXON_DEBUG', '').lower() in ('1', 'true', 'yes'):
            self.config.enable_debug_mode = True
            self.config.log_level = 'DEBUG'
        
        # Performance mode
        perf_mode = os.getenv('AXON_PERFORMANCE_MODE', '').lower()
        if perf_mode in ('performance', 'minimal'):
            self.config.performance_mode = PerformanceMode(perf_mode)
        
        # Theme
        theme = os.getenv('AXON_THEME', '').lower()
        if theme in ('high_contrast', 'dark', 'light'):
            self.config.theme = Theme(theme)
    
    def save_config(self):
        """Save configuration to file."""
        try:
            # Create config directory
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Convert to dict
            config_dict = {
                'theme': self.config.theme.value,
                'performance_mode': self.config.performance_mode.value,
                'reticle': asdict(self.config.reticle),
                'overlay': asdict(self.config.overlay),
                'input_dialog': asdict(self.config.input_dialog),
                'tray': asdict(self.config.tray),
                'log_level': self.config.log_level,
                'enable_debug_mode': self.config.enable_debug_mode,
            }
            
            # Write to file
            with open(self.config_file, 'w') as f:
                json.dump(config_dict, f, indent=2)
        except Exception as e:
            print(f"Warning: Failed to save config: {e}")
    
    def get_config(self) -> UIConfig:
        """Get current configuration.
        
        Returns:
            Current UI configuration
        """
        return self.config
    
    def update_config(self, **kwargs):
        """Update configuration values.
        
        Args:
            **kwargs: Configuration values to update
        """
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
        self.save_config()
    
    def reset_to_defaults(self):
        """Reset configuration to defaults."""
        self.config = UIConfig()
        self.save_config()
    
    def apply_performance_mode(self, mode: PerformanceMode):
        """Apply a performance mode preset.
        
        Args:
            mode: Performance mode to apply
        """
        self.config.performance_mode = mode
        
        if mode == PerformanceMode.MINIMAL:
            # Minimal mode - maximum performance
            self.config.reticle.animation_enabled = False
            self.config.reticle.glow_layers = 1
            self.config.reticle.enable_antialiasing = False
            self.config.overlay.show_hud = False
            self.config.overlay.enable_vsync = False
        elif mode == PerformanceMode.PERFORMANCE:
            # Performance mode - reduced effects
            self.config.reticle.glow_layers = 2
            self.config.reticle.pulse_amplitude = 2
            self.config.overlay.enable_vsync = True
        elif mode == PerformanceMode.BALANCED:
            # Balanced mode - default settings
            self.config.reticle = ReticleConfig()
            self.config.overlay = OverlayConfig()
        elif mode == PerformanceMode.HIGH_QUALITY:
            # High quality mode - all effects enabled
            self.config.reticle.glow_layers = 3
            self.config.reticle.enable_antialiasing = True
            self.config.overlay.enable_vsync = True
        
        self.save_config()
    
    def apply_theme(self, theme: Theme):
        """Apply a visual theme.
        
        Args:
            theme: Theme to apply
        """
        self.config.theme = theme
        
        if theme == Theme.HIGH_CONTRAST:
            # High contrast colors
            self.config.reticle.color_idle = (255, 255, 255, 255)
            self.config.reticle.color_thinking = (255, 255, 0, 255)
            self.config.reticle.color_moving = (0, 255, 0, 255)
            self.config.reticle.color_clicking = (255, 0, 0, 255)
            self.config.reticle.high_contrast_mode = True
        elif theme == Theme.DARK:
            # Dark theme colors
            self.config.reticle.color_idle = (80, 160, 200, 180)
            self.config.reticle.color_thinking = (200, 160, 80, 180)
            self.config.reticle.color_moving = (80, 200, 120, 180)
            self.config.reticle.color_clicking = (200, 80, 80, 200)
        elif theme == Theme.LIGHT:
            # Light theme colors
            self.config.reticle.color_idle = (50, 100, 200, 150)
            self.config.reticle.color_thinking = (200, 150, 50, 150)
            self.config.reticle.color_moving = (50, 200, 100, 150)
            self.config.reticle.color_clicking = (200, 50, 50, 180)
        else:
            # Default theme
            self.config.reticle = ReticleConfig()
        
        self.save_config()


# Global config manager instance
_config_manager = ConfigManager()


def get_config() -> UIConfig:
    """Get current UI configuration.
    
    Returns:
        Current UI configuration
    """
    return _config_manager.get_config()


def save_config():
    """Save current configuration."""
    _config_manager.save_config()


def reset_config():
    """Reset configuration to defaults."""
    _config_manager.reset_to_defaults()


def apply_performance_mode(mode: PerformanceMode):
    """Apply a performance mode preset.
    
    Args:
        mode: Performance mode to apply
    """
    _config_manager.apply_performance_mode(mode)


def apply_theme(theme: Theme):
    """Apply a visual theme.
    
    Args:
        theme: Theme to apply
    """
    _config_manager.apply_theme(theme)


# Made with Bob