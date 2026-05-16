"""Windows API integration for window and application detection.

Dev 2 (Ashish) - Executor & Safety

This module provides Windows-specific functionality for detecting and interacting
with application windows. It enables AXON to:
- Detect which application is currently active
- Get window information (title, process, position)
- Enumerate all visible windows
- Bring windows to foreground
- Check window visibility

All functions handle errors gracefully and return None/False on failure.
"""

import sys
import logging
from typing import Optional, Dict, List, Any

# Set up logging
logger = logging.getLogger(__name__)

# Windows-specific imports with type stubs
if sys.platform == 'win32':
    try:
        import win32gui  # type: ignore
        import win32process  # type: ignore
        import psutil
    except ImportError as e:
        logger.error(f"Failed to import Windows dependencies: {e}")
        logger.error("Install with: pip install pywin32 psutil")
        win32gui = None  # type: ignore
        win32process = None  # type: ignore
        psutil = None  # type: ignore
else:
    logger.warning("win_api.py is Windows-specific and will not function on this platform")
    win32gui = None  # type: ignore
    win32process = None  # type: ignore
    psutil = None  # type: ignore


def get_active_window() -> Optional[Dict[str, Any]]:
    """Get information about the currently active window.
    
    This is the CORE FUNCTION used by app_handlers.py to detect which
    application is currently active for app-specific optimizations.
    
    Returns:
        dict: Window information with keys:
            - 'hwnd': int (window handle)
            - 'title': str (window title)
            - 'pid': int (process ID)
            - 'process': str (process name, e.g., 'chrome.exe')
        None: If error occurs or not on Windows
    
    Example:
        >>> info = get_active_window()
        >>> if info:
        ...     print(f"Active app: {info['process']}")
        ...     print(f"Window title: {info['title']}")
    """
    # Check if on Windows and imports are available
    if sys.platform != 'win32' or not win32gui:
        logger.error("get_active_window() only works on Windows")
        return None
    
    try:
        # Get the foreground window handle
        hwnd = win32gui.GetForegroundWindow()
        if not hwnd:
            logger.warning("No foreground window found")
            return None
        
        # Get window title
        title = win32gui.GetWindowText(hwnd) if win32gui else ""
        
        # Get process ID
        if not win32process:
            logger.error("win32process module not available")
            return None
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        
        # Get process name
        if not psutil:
            logger.error("psutil module not available")
            process = "unknown"
        else:
            try:
                process = psutil.Process(pid).name()
            except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                logger.warning(f"Could not get process name for PID {pid}: {e}")
                process = "unknown"
        
        result = {
            "hwnd": hwnd,
            "title": title,
            "pid": pid,
            "process": process
        }
        
        logger.debug(f"Active window: {process} - {title}")
        return result
        
    except Exception as e:
        logger.error(f"Error getting active window: {e}")
        return None


def get_window_title(hwnd: int) -> str:
    """Get the title of a window by handle.
    
    Args:
        hwnd (int): Window handle
        
    Returns:
        str: Window title or empty string if error
    
    Example:
        >>> hwnd = 12345
        >>> title = get_window_title(hwnd)
        >>> print(title)
    """
    if sys.platform != 'win32' or not win32gui:
        return ""
    
    try:
        if not win32gui:
            return ""
        title = win32gui.GetWindowText(hwnd)
        return title
    except Exception as e:
        logger.error(f"Error getting window title for handle {hwnd}: {e}")
        return ""


def get_process_name(pid: int) -> Optional[str]:
    """Get the process name from process ID.
    
    Args:
        pid (int): Process ID
        
    Returns:
        str: Process name (e.g., 'chrome.exe') or None if error
    
    Example:
        >>> pid = 1234
        >>> name = get_process_name(pid)
        >>> print(name)  # 'notepad.exe'
    """
    if sys.platform != 'win32' or not psutil:
        return None
    
    try:
        if not psutil:
            return None
        process = psutil.Process(pid)
        return process.name()
    except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
        logger.error(f"Error getting process name for PID {pid}: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error getting process name for PID {pid}: {e}")
        return None


def list_all_windows() -> List[Dict[str, Any]]:
    """List all visible windows.
    
    Useful for debugging and understanding what windows are currently open.
    Only returns windows that are visible (not hidden or minimized to tray).
    
    Returns:
        list: List of dicts, each containing:
            - 'hwnd': int (window handle)
            - 'title': str (window title)
            - 'pid': int (process ID)
            - 'process': str (process name)
        Empty list if error or not on Windows
    
    Example:
        >>> windows = list_all_windows()
        >>> for win in windows:
        ...     print(f"{win['process']}: {win['title']}")
    """
    if sys.platform != 'win32' or not win32gui:
        logger.error("list_all_windows() only works on Windows")
        return []
    
    windows = []
    
    def callback(hwnd, extra):
        """Callback function for EnumWindows."""
        try:
            # Only include visible windows with titles
            if win32gui and win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd) if win32gui else ""
                if title:  # Skip windows without titles
                    if win32process:
                        _, pid = win32process.GetWindowThreadProcessId(hwnd)
                        try:
                            process = psutil.Process(pid).name() if psutil else "unknown"
                        except:
                            process = "unknown"
                    else:
                        pid = 0
                        process = "unknown"
                    
                    windows.append({
                        "hwnd": hwnd,
                        "title": title,
                        "pid": pid,
                        "process": process
                    })
        except Exception as e:
            logger.debug(f"Error processing window {hwnd}: {e}")
        return True  # Continue enumeration
    
    try:
        if not win32gui:
            return []
        win32gui.EnumWindows(callback, None)
        logger.debug(f"Found {len(windows)} visible windows")
        return windows
    except Exception as e:
        logger.error(f"Error enumerating windows: {e}")
        return []


def bring_window_to_front(hwnd: int) -> bool:
    """Bring a window to the foreground.
    
    Useful for future features where AXON might need to switch between
    applications or bring a specific window to focus.
    
    Args:
        hwnd (int): Window handle
        
    Returns:
        bool: True if successful, False otherwise
    
    Example:
        >>> hwnd = 12345
        >>> if bring_window_to_front(hwnd):
        ...     print("Window activated")
    """
    if sys.platform != 'win32' or not win32gui:
        logger.error("bring_window_to_front() only works on Windows")
        return False
    
    try:
        if not win32gui:
            return False
        win32gui.SetForegroundWindow(hwnd)
        logger.debug(f"Brought window {hwnd} to front")
        return True
    except Exception as e:
        logger.error(f"Error bringing window {hwnd} to front: {e}")
        return False


def get_window_at_position(x: int, y: int) -> Optional[int]:
    """Get the window at specific screen coordinates.
    
    Useful for detecting which window is under the mouse cursor.
    
    Args:
        x (int): X coordinate (screen coordinates)
        y (int): Y coordinate (screen coordinates)
        
    Returns:
        int: Window handle (hwnd) or None if error
    
    Example:
        >>> hwnd = get_window_at_position(100, 200)
        >>> if hwnd:
        ...     title = get_window_title(hwnd)
        ...     print(f"Window at (100, 200): {title}")
    """
    if sys.platform != 'win32' or not win32gui:
        logger.error("get_window_at_position() only works on Windows")
        return None
    
    try:
        if not win32gui:
            return None
        hwnd = win32gui.WindowFromPoint((x, y))
        if hwnd:
            logger.debug(f"Found window {hwnd} at position ({x}, {y})")
            return hwnd
        return None
    except Exception as e:
        logger.error(f"Error getting window at position ({x}, {y}): {e}")
        return None


def is_window_visible(hwnd: int) -> bool:
    """Check if a window is visible.
    
    A window is considered visible if it's not hidden or minimized to tray.
    This doesn't necessarily mean it's on top or in the foreground.
    
    Args:
        hwnd (int): Window handle
        
    Returns:
        bool: True if visible, False otherwise
    
    Example:
        >>> hwnd = 12345
        >>> if is_window_visible(hwnd):
        ...     print("Window is visible")
    """
    if sys.platform != 'win32' or not win32gui:
        logger.error("is_window_visible() only works on Windows")
        return False
    
    try:
        if not win32gui:
            return False
        visible = win32gui.IsWindowVisible(hwnd)
        logger.debug(f"Window {hwnd} visible: {visible}")
        return bool(visible)
    except Exception as e:
        logger.error(f"Error checking visibility for window {hwnd}: {e}")
        return False

# Made with Bob
