"""UI module - Interface & Demo (Dev 3: Pratham)

This module contains all UI components for the AXON desktop agent:
- Reticle: Animated glowing cursor prediction indicator
- Overlay: Transparent fullscreen window for visual feedback
- Input Dialog: Floating task input with voice support
- Tray Icon: System tray integration with menu

Production-level features:
- Comprehensive error handling and logging
- Performance monitoring and optimization
- Configurable themes and settings
- Type hints and documentation
"""

from .reticle import Reticle
from .overlay import TransparentOverlay, create_overlay, run_overlay_app
from .input_dialog import TaskInputDialog, VoiceRecorder, show_task_input_dialog, create_voice_button
from .tray import TrayIcon, create_tray_icon, monitor_status_queue
from .logger import get_logger, enable_debug_mode, disable_debug_mode
from .config_ui import get_config, save_config, reset_config, apply_performance_mode, apply_theme
from .exceptions import (
    UIException, ReticleException, OverlayException,
    InputDialogException, TrayIconException, ErrorCode
)

__all__ = [
    # Reticle
    'Reticle',
    
    # Overlay
    'TransparentOverlay',
    'create_overlay',
    'run_overlay_app',
    
    # Input Dialog
    'TaskInputDialog',
    'VoiceRecorder',
    'show_task_input_dialog',
    'create_voice_button',
    
    # Tray Icon
    'TrayIcon',
    'create_tray_icon',
    'monitor_status_queue',
    
    # Logger
    'get_logger',
    'enable_debug_mode',
    'disable_debug_mode',
    
    # Config
    'get_config',
    'save_config',
    'reset_config',
    'apply_performance_mode',
    'apply_theme',
    
    # Exceptions
    'UIException',
    'ReticleException',
    'OverlayException',
    'InputDialogException',
    'TrayIconException',
    'ErrorCode',
]

# Made with Bob
