"""Application-specific keyboard shortcuts and handlers.

Dev 2 (Ashish) - Executor & Safety
TODO: Implement app-specific handlers
- Define common keyboard shortcuts for popular applications
- Browser shortcuts (Chrome, Firefox, Edge)
- Office shortcuts (Word, Excel, PowerPoint)
- Code editor shortcuts (VS Code, PyCharm)
- File explorer shortcuts
- System shortcuts (Windows)
- Provide helper functions to execute app-specific actions
- Auto-detect active application and suggest relevant shortcuts
"""

from executor.win_api import get_active_window
from executor.actions import press_key


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


def get_app_shortcuts(app_name=None):
    """Get keyboard shortcuts for an application.
    
    Args:
        app_name (str, optional): Application name. If None, uses active app.
        
    Returns:
        dict: Shortcut mappings for the application
    """
    # TODO: Implement shortcut retrieval
    # 1. If app_name not provided, get active window
    # 2. Look up shortcuts in APP_SHORTCUTS
    # 3. Return shortcuts or empty dict
    pass


def execute_app_shortcut(action_name, app_name=None):
    """Execute an application-specific shortcut.
    
    Args:
        action_name (str): Name of the action (e.g., 'new_tab')
        app_name (str, optional): Application name. If None, uses active app.
        
    Returns:
        bool: True if shortcut executed successfully
    """
    # TODO: Implement shortcut execution
    # 1. Get shortcuts for app
    # 2. Look up action_name in shortcuts
    # 3. Execute the key combination using press_key()
    # 4. Return success status
    pass


def suggest_shortcuts_for_task(task_description):
    """Suggest relevant shortcuts based on task description.
    
    Args:
        task_description (str): Description of what user wants to do
        
    Returns:
        list: List of suggested shortcut names
    """
    # TODO: Implement shortcut suggestion
    # 1. Get active application
    # 2. Parse task description for keywords
    # 3. Match keywords to shortcut names
    # 4. Return relevant shortcuts
    pass


def is_dangerous_shortcut(shortcut):
    """Check if a shortcut could be dangerous to execute.
    
    Args:
        shortcut (str): Keyboard shortcut string
        
    Returns:
        bool: True if potentially dangerous
    """
    # TODO: Implement safety check
    # Flag shortcuts like:
    # - alt+f4 (close window)
    # - ctrl+alt+delete (system interrupt)
    # - win+l (lock screen)
    # - shutdown commands
    dangerous = ['alt+f4', 'ctrl+alt+delete', 'win+l']
    return shortcut.lower() in dangerous

# Made with Bob
