"""UI module - Interface & Demo (Dev 3: Pratham)

This module contains all UI components for the AXON desktop agent:
- Reticle: Simple hand cursor with coordinate tracking
- Overlay: Transparent cursor widget with coordinate display
- Input Dialog: Floating task input with voice support
- Tray Icon: System tray integration with menu
"""

from .reticle import Reticle
from .overlay import TransparentOverlay, create_overlay, run_overlay_app
from .input_dialog import TaskInputDialog, show_task_input_dialog
from .tray import TrayIcon, create_tray_icon, monitor_status_queue

__all__ = [
    # Reticle
    'Reticle',
    
    # Overlay
    'TransparentOverlay',
    'create_overlay',
    'run_overlay_app',
    
    # Input Dialog
    'TaskInputDialog',
    'show_task_input_dialog',
    
    # Tray Icon
    'TrayIcon',
    'create_tray_icon',
    'monitor_status_queue',
]

# Made with Bob
