"""Application-specific keyboard shortcuts and handlers.

Dev 2 (Ashish) - Executor & Safety

This module enables AXON to use keyboard shortcuts optimized for specific applications
instead of slow mouse movements. It provides:
- Comprehensive shortcut mappings for popular applications
- Auto-detection of active application
- Safe execution of app-specific shortcuts
- Shortcut suggestion system for tasks

Integration with other modules:
- Uses win_api.get_active_window() to detect active application
- Uses actions.press_key() to execute keyboard shortcuts
"""

import logging
from typing import Optional, Dict, List
from executor.win_api import get_active_window
from executor.actions import press_key

# Set up logging
logger = logging.getLogger(__name__)


# Application-specific shortcut mappings
APP_SHORTCUTS = {
    'chrome.exe': {
        'new_tab': 'ctrl+t',
        'close_tab': 'ctrl+w',
        'reopen_tab': 'ctrl+shift+t',
        'new_window': 'ctrl+n',
        'incognito': 'ctrl+shift+n',
        'refresh': 'f5',
        'hard_refresh': 'ctrl+f5',
        'address_bar': 'ctrl+l',
        'find': 'ctrl+f',
        'bookmark': 'ctrl+d',
        'downloads': 'ctrl+j',
        'history': 'ctrl+h',
        'dev_tools': 'f12',
    },
    'firefox.exe': {
        'new_tab': 'ctrl+t',
        'close_tab': 'ctrl+w',
        'reopen_tab': 'ctrl+shift+t',
        'new_window': 'ctrl+n',
        'private_window': 'ctrl+shift+p',
        'refresh': 'f5',
        'address_bar': 'ctrl+l',
        'find': 'ctrl+f',
        'bookmark': 'ctrl+d',
    },
    'WINWORD.EXE': {  # Microsoft Word
        'save': 'ctrl+s',
        'save_as': 'f12',
        'print': 'ctrl+p',
        'undo': 'ctrl+z',
        'redo': 'ctrl+y',
        'bold': 'ctrl+b',
        'italic': 'ctrl+i',
        'underline': 'ctrl+u',
        'find': 'ctrl+f',
        'replace': 'ctrl+h',
    },
    'EXCEL.EXE': {  # Microsoft Excel
        'save': 'ctrl+s',
        'new_sheet': 'shift+f11',
        'format_cells': 'ctrl+1',
        'insert_row': 'ctrl+shift++',
        'delete_row': 'ctrl+-',
        'find': 'ctrl+f',
        'replace': 'ctrl+h',
    },
    'Code.exe': {  # VS Code
        'command_palette': 'ctrl+shift+p',
        'quick_open': 'ctrl+p',
        'new_file': 'ctrl+n',
        'save': 'ctrl+s',
        'find': 'ctrl+f',
        'replace': 'ctrl+h',
        'comment': 'ctrl+/',
        'terminal': 'ctrl+`',
        'sidebar': 'ctrl+b',
    },
    'explorer.exe': {  # Windows Explorer
        'new_folder': 'ctrl+shift+n',
        'delete': 'delete',
        'rename': 'f2',
        'refresh': 'f5',
        'address_bar': 'alt+d',
        'search': 'ctrl+f',
        'properties': 'alt+enter',
    },
}


def get_app_shortcuts(app_name: Optional[str] = None) -> Dict[str, str]:
    """Get keyboard shortcuts for an application.
    
    This is a CORE FUNCTION that retrieves app-specific shortcuts for optimization.
    If no app_name is provided, it auto-detects the currently active application.
    
    Args:
        app_name (str, optional): Application process name (e.g., 'chrome.exe').
                                 If None, auto-detects from active window.
        
    Returns:
        dict: Shortcut mappings for the application (e.g., {'new_tab': 'ctrl+t'})
              Returns empty dict if app not found or error occurs.
    
    Example:
        >>> # Auto-detect active app
        >>> shortcuts = get_app_shortcuts()
        >>> print(shortcuts.get('new_tab'))  # 'ctrl+t' if Chrome is active
        
        >>> # Explicit app name
        >>> shortcuts = get_app_shortcuts('chrome.exe')
        >>> print(shortcuts)  # {'new_tab': 'ctrl+t', 'close_tab': 'ctrl+w', ...}
    """
    try:
        # If app_name not provided, detect active application
        if app_name is None:
            active_window = get_active_window()
            if not active_window:
                logger.warning("Could not detect active window")
                return {}
            
            app_name = active_window.get('process')
            if not app_name:
                logger.warning("Active window has no process name")
                return {}
            
            logger.debug(f"Auto-detected active app: {app_name}")
        
        # Look up shortcuts in APP_SHORTCUTS dictionary
        shortcuts = APP_SHORTCUTS.get(app_name, {})
        
        if shortcuts:
            logger.info(f"Found {len(shortcuts)} shortcuts for {app_name}")
        else:
            logger.info(f"No shortcuts defined for {app_name}")
        
        return shortcuts
    
    except Exception as e:
        logger.error(f"Error getting shortcuts for {app_name}: {e}")
        return {}


def execute_app_shortcut(shortcut_name: str, app_name: Optional[str] = None) -> bool:
    """Execute an application-specific shortcut.
    
    This is a CORE FUNCTION that executes keyboard shortcuts for app-specific actions.
    Much faster than mouse movements for common operations.
    
    Args:
        shortcut_name (str): Name of the shortcut action (e.g., 'new_tab', 'save', 'find')
        app_name (str, optional): Application process name. If None, uses active app.
        
    Returns:
        bool: True if shortcut executed successfully, False otherwise
    
    Example:
        >>> # Execute shortcut in active app
        >>> execute_app_shortcut('new_tab')  # Opens new tab if browser is active
        
        >>> # Execute shortcut for specific app
        >>> execute_app_shortcut('new_tab', 'chrome.exe')  # Executes Ctrl+T
        
        >>> # Common usage pattern
        >>> if execute_app_shortcut('save'):
        ...     print("File saved")
    """
    try:
        # Get shortcuts for the application
        shortcuts = get_app_shortcuts(app_name)
        
        if not shortcuts:
            logger.warning(f"No shortcuts available for app: {app_name or 'active app'}")
            return False
        
        # Look up the shortcut name
        key_combination = shortcuts.get(shortcut_name)
        
        if not key_combination:
            logger.warning(f"Shortcut '{shortcut_name}' not found for app. Available: {list(shortcuts.keys())}")
            return False
        
        # Safety check: verify shortcut is not dangerous
        if is_dangerous_shortcut(key_combination):
            logger.warning(f"Refusing to execute dangerous shortcut: {key_combination}")
            return False
        
        # Execute the key combination
        logger.info(f"Executing shortcut '{shortcut_name}' -> {key_combination}")
        success = press_key(key_combination)
        
        if success:
            logger.info(f"Successfully executed shortcut: {shortcut_name}")
        else:
            logger.error(f"Failed to execute shortcut: {shortcut_name}")
        
        return success
    
    except Exception as e:
        logger.error(f"Error executing shortcut '{shortcut_name}': {e}")
        return False


def suggest_shortcuts_for_task(task_description: str, app_name: Optional[str] = None) -> List[str]:
    """Suggest relevant shortcuts based on task description.
    
    This is a FUTURE FEATURE that will use AI to suggest relevant shortcuts.
    Currently returns all available shortcuts for the application.
    
    TODO: Enhance with LLM integration to intelligently match task descriptions
    to relevant shortcuts. For example:
    - "open new tab" -> ['new_tab', 'new_window']
    - "save document" -> ['save', 'save_as']
    - "find text" -> ['find', 'replace']
    
    Args:
        task_description (str): Description of what user wants to do
        app_name (str, optional): Application name. If None, uses active app.
        
    Returns:
        list: List of suggested shortcut names that might be relevant
    
    Example:
        >>> suggestions = suggest_shortcuts_for_task("open new tab")
        >>> print(suggestions)  # ['new_tab', 'new_window', 'incognito', ...]
    """
    try:
        # Get shortcuts for the application
        shortcuts = get_app_shortcuts(app_name)
        
        if not shortcuts:
            logger.warning(f"No shortcuts available for app: {app_name or 'active app'}")
            return []
        
        # TODO: Implement intelligent matching with LLM
        # For now, return all available shortcuts
        # Future: Parse task_description and match keywords to shortcut names
        
        shortcut_names = list(shortcuts.keys())
        logger.info(f"Suggesting {len(shortcut_names)} shortcuts for task: '{task_description[:50]}'")
        
        return shortcut_names
    
    except Exception as e:
        logger.error(f"Error suggesting shortcuts for task '{task_description[:50]}': {e}")
        return []


def is_dangerous_shortcut(shortcut: str) -> bool:
    """Check if a shortcut could be dangerous to execute.
    
    This is a SAFETY FEATURE that prevents AXON from executing shortcuts
    that could cause data loss, close windows, or disrupt the system.
    
    Args:
        shortcut (str): Keyboard shortcut string (e.g., 'alt+f4', 'ctrl+w')
        
    Returns:
        bool: True if potentially dangerous, False if safe
    
    Example:
        >>> is_dangerous_shortcut('alt+f4')  # True - closes window
        >>> is_dangerous_shortcut('ctrl+s')  # False - just saves
        >>> is_dangerous_shortcut('ctrl+w')  # True - closes tab/window
    """
    # Normalize shortcut to lowercase for comparison
    shortcut_lower = shortcut.lower().strip()
    
    # List of dangerous shortcuts that could cause data loss or system disruption
    dangerous_shortcuts = [
        'alt+f4',           # Close window
        'ctrl+w',           # Close tab/window (can cause data loss)
        'ctrl+q',           # Quit application
        'ctrl+alt+delete',  # System interrupt
        'ctrl+alt+del',     # System interrupt (alternate)
        'win+l',            # Lock screen
        'win+r',            # Run dialog (could execute commands)
        'alt+tab',          # Switch windows (disruptive)
        'ctrl+shift+esc',   # Task manager
        'win+x',            # Power user menu
        'ctrl+shift+q',     # Sign out (Chrome OS / some apps)
    ]
    
    # Check if shortcut is in dangerous list
    is_dangerous = shortcut_lower in dangerous_shortcuts
    
    if is_dangerous:
        logger.warning(f"Dangerous shortcut detected: {shortcut}")
    
    return is_dangerous

# Made with Bob
