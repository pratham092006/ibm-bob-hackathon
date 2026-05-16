"""UI module - Interface & Demo (Dev 3: Pratham)

This module contains all UI components for the AXON desktop agent:
- Reticle: Animated glowing cursor prediction indicator
- Overlay: Transparent fullscreen window for visual feedback
- Input Dialog: Floating task input with voice support
- Tray Icon: System tray integration with menu
"""

from .reticle import Reticle, draw_glowing_circle, draw_crosshair
from .overlay import TransparentOverlay, create_overlay, run_overlay_app
from .input_dialog import TaskInputDialog, VoiceRecorder, show_task_input_dialog, create_voice_button
from .tray import TrayIcon, create_tray_icon, monitor_status_queue

__all__ = [
    # Reticle
    'Reticle',
    'draw_glowing_circle',
    'draw_crosshair',
    
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
]

# Made with Bob
