"""Action execution module for mouse, keyboard, and system control.

Dev 2 (Ashish) - Executor & Safety
Implements all action execution functions for the AXON system.
Receives action dictionaries from Computer Use API and executes them using pyautogui.
"""

import pyautogui
import time
import logging
import json
from collections import deque
from datetime import datetime
from pathlib import Path
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import kill_event, status_queue

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# Configure pyautogui safety settings
pyautogui.FAILSAFE = True  # Move mouse to corner to abort
pyautogui.PAUSE = 0.1  # Small delay between actions


def _get_coordinates(action_dict):
    """Extract coordinates from action dict, supporting both formats.
    
    Supports:
    - {"coordinate": [x, y]}  (primary format from executor spec)
    - {"x": 100, "y": 200}    (legacy format from some LLM responses)
    
    Args:
        action_dict (dict): Action dictionary
        
    Returns:
        list: [x, y] coordinates or empty list if not found
    """
    # Try 'coordinate' array first (primary format)
    coord = action_dict.get('coordinate', [])
    if isinstance(coord, (list, tuple)) and len(coord) == 2:
        return [int(coord[0]), int(coord[1])]
    
    # Fallback: try 'x' and 'y' keys
    x = action_dict.get('x')
    y = action_dict.get('y')
    if x is not None and y is not None:
        return [int(x), int(y)]
    
    return []

# Action history for stuck-loop detection (tracks last 10 actions)
action_history = deque(maxlen=10)
last_progress_time = time.time()
MAX_NO_PROGRESS_TIME = 15  # seconds


def _all_in_same_region(coords, radius=100):
    """Check if all coordinates are within radius of each other.
    
    Args:
        coords (list): List of [x, y] coordinate pairs
        radius (int): Maximum distance in pixels (default 100)
        
    Returns:
        bool: True if all coordinates are within radius of first coordinate
    """
    if len(coords) < 2:
        return False
    first = coords[0]
    if not first or len(first) != 2:
        return False
    for coord in coords[1:]:
        if not coord or len(coord) != 2:
            continue
        distance = ((coord[0] - first[0])**2 + (coord[1] - first[1])**2)**0.5
        if distance > radius:
            return False
    return True


def _is_stuck_loop(history):
    """Check if actions indicate a stuck loop (enhanced detection).
    
    Detects three types of loops:
    1. Exact repetition: Same action repeated 3+ times (EXCEPT open_app which may need retries)
    2. Semantic loop: Last 5 actions in same 100px region without progress
    3. Timeout: No progress for 20+ seconds (increased from 15)
    
    Args:
        history (deque): Deque containing last 10 action dictionaries
        
    Returns:
        bool: True if stuck loop detected, False otherwise
    """
    global last_progress_time
    
    if len(history) < 3:
        return False
    
    # Convert deque to list for easier comparison
    actions = list(history)
    
    # Check 1: Timeout detection (20 seconds without progress - increased tolerance)
    current_time = time.time()
    if current_time - last_progress_time > 20:  # Increased from 15 to 20
        logger.warning(f"Timeout detected: No progress for 20 seconds")
        return True
    
    # Check 2: Exact repetition (last 3 actions identical)
    if len(history) >= 3:
        last_three = actions[-3:]
        action_types = [a.get('action') for a in last_three]
        
        # All three must be same type
        if len(set(action_types)) == 1:
            action_type = action_types[0]
            
            # EXCEPTION: open_app actions are allowed to repeat (app may take time to open)
            if action_type == 'open_app':
                # Check if same app is being opened repeatedly
                app_names = [a.get('text', '') for a in last_three]
                if len(set(app_names)) == 1 and app_names[0] != '':
                    # Only flag as stuck if repeated more than 3 times
                    if len(history) >= 4:
                        last_four = actions[-4:]
                        if all(a.get('action') == 'open_app' and a.get('text') == app_names[0] for a in last_four):
                            logger.warning(f"Stuck loop: open_app '{app_names[0]}' repeated 4+ times")
                            return True
                    # Otherwise allow it (app might be loading)
                    return False
            
            # For coordinate-based actions
            if action_type in ['left_click', 'right_click', 'middle_click', 'double_click', 'mouse_move', 'scroll']:
                coords = [a.get('coordinate', []) for a in last_three]
                
                # Check if all have valid coordinates
                if all(len(c) == 2 for c in coords):
                    # Check if coordinates are within 5 pixels of each other
                    all_close = True
                    for i in range(1, 3):
                        x_diff = abs(coords[i][0] - coords[0][0])
                        y_diff = abs(coords[i][1] - coords[0][1])
                        if x_diff > 5 or y_diff > 5:
                            all_close = False
                            break
                    
                    if all_close:
                        # For scroll, also check direction and amount
                        if action_type == 'scroll':
                            directions = [a.get('direction') for a in last_three]
                            amounts = [a.get('amount') for a in last_three]
                            if len(set(directions)) == 1 and len(set(amounts)) == 1:
                                logger.warning("Exact repetition detected: Same scroll action 3 times")
                                return True
                        else:
                            logger.warning(f"Exact repetition detected: Same {action_type} 3 times")
                            return True
            
            # For text-based actions (but not open_app which we handled above)
            elif action_type in ['type', 'key']:
                texts = [a.get('text', '') for a in last_three]
                if len(set(texts)) == 1 and texts[0] != '':
                    logger.warning(f"Exact repetition detected: Same {action_type} 3 times")
                    return True
    
    # Check 3: Semantic loop (last 5 actions in same region)
    if len(history) >= 5:
        last_five = actions[-5:]
        
        # Extract coordinates from coordinate-based actions
        coords = []
        for action in last_five:
            action_type = action.get('action')
            if action_type in ['left_click', 'right_click', 'middle_click', 'double_click', 'mouse_move', 'scroll']:
                coord = action.get('coordinate', [])
                if len(coord) == 2:
                    coords.append(coord)
        
        # If we have at least 4 coordinate-based actions in same region
        if len(coords) >= 4 and _all_in_same_region(coords, radius=100):
            logger.warning("Semantic loop detected: 5 actions in same 100px region")
            return True
    
    return False


def log_action_to_file(action_dict, success, execution_time=None):
    """Log action execution to session_log.json.
    
    Appends each action to a JSON log file with timestamp and execution details.
    Creates the file if it doesn't exist.
    
    Args:
        action_dict (dict): The action that was executed
        success (bool): Whether the action succeeded
        execution_time (float, optional): Execution time in milliseconds
    """
    try:
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action_dict.get("action"),
            "details": action_dict,
            "success": success,
            "execution_time_ms": execution_time
        }
        
        # Get log file path (in axon directory, not executor subdirectory)
        log_file = Path(__file__).parent.parent / "session_log.json"
        
        # Read existing logs or create new list
        logs = []
        if log_file.exists():
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    logs = json.load(f)
                    if not isinstance(logs, list):
                        logs = []
            except (json.JSONDecodeError, IOError):
                # If file is corrupted or empty, start fresh
                logs = []
        
        # Append new log entry
        logs.append(log_entry)
        
        # Write back to file
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(logs, f, indent=2, ensure_ascii=False)
        
        logger.debug(f"Action logged to {log_file}")
        
    except Exception as e:
        # Don't let logging errors break action execution
        logger.error(f"Error logging action to file: {e}")


def _open_app_via_search(app_name):
    """Open application using Windows Search (atomic operation).
    
    This executes the entire sequence atomically:
    1. Press Windows key
    2. Type app name
    3. Press Enter
    4. Wait for app to launch
    
    Args:
        app_name (str): Name of the application to open
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        logger.info(f"Opening app via Windows Search: {app_name}")
        
        # Press Windows key
        pyautogui.press('win')
        time.sleep(0.3)  # Wait for Start menu
        
        # Type app name
        pyautogui.write(app_name, interval=0.05)
        time.sleep(0.5)  # Wait for search results
        
        # Press Enter
        pyautogui.press('enter')
        time.sleep(1.0)  # Wait for app to launch
        
        logger.info(f"Successfully opened {app_name}")
        return True
        
    except Exception as e:
        logger.error(f"Error opening app {app_name}: {e}")
        return False


def execute_action(action_dict):
    """Execute an action based on Computer Use API response.
    
    Main dispatcher function that routes actions to appropriate handlers.
    This is the function Dev 1's loop will call.
    
    Features:
    - Stuck-loop detection: Detects if same action repeats 3 times
    - Action logging: Logs all actions to session_log.json
    
    Args:
        action_dict (dict): Action specification from Computer Use API
            Examples:
            {"action": "left_click", "coordinate": [420, 310]}
            {"action": "type", "text": "Hello World"}
            {"action": "scroll", "coordinate": [340, 400], "direction": "down", "amount": 3}
            {"action": "key", "text": "ctrl+s"}
            {"action": "mouse_move", "coordinate": [200, 150]}
            {"action": "open_app", "text": "chrome"}
            {"action": "done"}
    
    Returns:
        bool: True if action executed successfully, False otherwise
    """
    start_time = time.time()
    success = False
    
    try:
        action_type = action_dict.get('action')
        
        if not action_type:
            logger.error("No action type specified in action_dict")
            log_action_to_file(action_dict, False)
            return False
        
        # Add action to history for stuck-loop detection
        action_history.append(action_dict)
        
        # Check for stuck loop (enhanced detection)
        if _is_stuck_loop(action_history):
            logger.warning("🔴 STUCK LOOP DETECTED!")
            logger.warning(f"Current action: {action_type}")
            
            # Set kill_event to pause execution
            kill_event.set()
            
            # Push stuck signal to status_queue
            status_queue.put({
                "type": "stuck",
                "message": f"Stuck loop detected - '{action_type}' action repeated 3 times",
                "action": action_dict,
                "timestamp": datetime.now().isoformat()
            })
            
            # Log the stuck loop
            execution_time = (time.time() - start_time) * 1000
            log_action_to_file(action_dict, False, execution_time)
            
            return False
        
        logger.info(f"Executing action: {action_type}")
        
        # Route to appropriate action handler
        # NEW: Handle open_app as atomic operation
        if action_type == "open_app":
            app_name = action_dict.get('text', '')
            if not app_name:
                logger.error("No app name specified for open_app action")
                success = False
            else:
                success = _open_app_via_search(app_name)
        
        elif action_type == "mouse_move":
            coordinate = _get_coordinates(action_dict)
            if len(coordinate) != 2:
                logger.error(f"Invalid coordinate for mouse_move: {coordinate}")
                success = False
            else:
                success = mouse_move(coordinate[0], coordinate[1])
        
        elif action_type == "click" or action_type == "left_click":
            # Support both "click" and "left_click" for compatibility
            coordinate = _get_coordinates(action_dict)
            if len(coordinate) != 2:
                logger.error(f"Invalid coordinate for left_click: {coordinate}")
                success = False
            else:
                success = click(coordinate[0], coordinate[1], button='left')
        
        elif action_type == "right_click":
            coordinate = _get_coordinates(action_dict)
            if len(coordinate) != 2:
                logger.error(f"Invalid coordinate for right_click: {coordinate}")
                success = False
            else:
                success = click(coordinate[0], coordinate[1], button='right')
        
        elif action_type == "middle_click":
            coordinate = _get_coordinates(action_dict)
            if len(coordinate) != 2:
                logger.error(f"Invalid coordinate for middle_click: {coordinate}")
                success = False
            else:
                success = click(coordinate[0], coordinate[1], button='middle')
        
        elif action_type == "double_click":
            coordinate = _get_coordinates(action_dict)
            if len(coordinate) != 2:
                logger.error(f"Invalid coordinate for double_click: {coordinate}")
                success = False
            else:
                success = click(coordinate[0], coordinate[1], clicks=2)
        
        elif action_type == "type":
            text = action_dict.get('text', '')
            if not text:
                logger.error("No text specified for type action")
                success = False
            else:
                success = type_text(text)
        
        elif action_type == "key":
            key_combination = action_dict.get('text', '')
            if not key_combination:
                logger.error("No key specified for key action")
                success = False
            else:
                success = press_key(key_combination)
        
        elif action_type == "scroll":
            coordinate = _get_coordinates(action_dict)
            direction = action_dict.get('direction', 'down')
            amount = action_dict.get('amount', 3)
            
            if len(coordinate) != 2:
                logger.error(f"Invalid coordinate for scroll: {coordinate}")
                success = False
            else:
                success = scroll(coordinate[0], coordinate[1], direction, amount)
        
        elif action_type == "done":
            logger.info("Task complete - setting kill_event")
            kill_event.set()
            success = True
        
        else:
            logger.error(f"Unknown action type: {action_type}")
            success = False
        
        # Calculate execution time and log the action
        execution_time = (time.time() - start_time) * 1000  # Convert to milliseconds
        log_action_to_file(action_dict, success, execution_time)
        
        # Reset progress timer on successful actions
        if success:
            global last_progress_time
            last_progress_time = time.time()
        
        return success
    
    except Exception as e:
        logger.error(f"Error executing action {action_dict}: {e}")
        execution_time = (time.time() - start_time) * 1000
        log_action_to_file(action_dict, False, execution_time)
        return False


def mouse_move(x, y, duration=0.1):
    """Move mouse cursor to coordinates with smooth animation.
    
    Args:
        x (int): Target x coordinate
        y (int): Target y coordinate
        duration (float): Animation duration in seconds (default 0.1)
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Validate coordinates first
        if not validate_coordinates(x, y):
            logger.error(f"Invalid coordinates for mouse_move: ({x}, {y})")
            return False
        
        # Perform smooth mouse movement
        pyautogui.moveTo(x, y, duration=duration)
        logger.info(f"Mouse moved to ({x}, {y})")
        return True
    
    except Exception as e:
        logger.error(f"Error moving mouse to ({x}, {y}): {e}")
        return False


def click(x, y, button='left', clicks=1):
    """Click at coordinates.
    
    Args:
        x (int): Click x coordinate
        y (int): Click y coordinate
        button (str): 'left', 'right', or 'middle' (default 'left')
        clicks (int): Number of clicks - 1 for single, 2 for double (default 1)
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Validate coordinates first
        if not validate_coordinates(x, y):
            logger.error(f"Invalid coordinates for click: ({x}, {y})")
            return False
        
        # Validate button type
        valid_buttons = ['left', 'right', 'middle']
        if button not in valid_buttons:
            logger.error(f"Invalid button type: {button}. Must be one of {valid_buttons}")
            return False
        
        # Perform click action
        pyautogui.click(x=x, y=y, clicks=clicks, button=button)
        
        click_type = "double-click" if clicks == 2 else "click"
        logger.info(f"{button.capitalize()} {click_type} at ({x}, {y})")
        return True
    
    except Exception as e:
        logger.error(f"Error clicking at ({x}, {y}) with button {button}: {e}")
        return False


def type_text(text, interval=0.03):
    """Type text with realistic timing.
    
    Args:
        text (str): Text to type
        interval (float): Delay between keystrokes in seconds (default 0.03)
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Use pyautogui.write for better special character handling
        pyautogui.write(text, interval=interval)
        logger.info(f"Typed text: '{text[:50]}{'...' if len(text) > 50 else ''}'")
        return True
    
    except Exception as e:
        logger.error(f"Error typing text '{text[:50]}': {e}")
        return False


def scroll(x, y, direction='down', amount=3):
    """Scroll at specified coordinates.
    
    Args:
        x (int): X coordinate to scroll at
        y (int): Y coordinate to scroll at
        direction (str): 'up' or 'down' (default 'down')
        amount (int): Scroll amount in clicks (default 3)
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Validate coordinates
        if not validate_coordinates(x, y):
            logger.error(f"Invalid coordinates for scroll: ({x}, {y})")
            return False
        
        # Move to coordinates first
        pyautogui.moveTo(x, y, duration=0.1)
        
        # Convert direction to scroll amount
        # pyautogui.scroll: positive = up, negative = down
        scroll_amount = amount if direction == 'up' else -amount
        
        # Perform scroll
        pyautogui.scroll(scroll_amount)
        logger.info(f"Scrolled {direction} by {amount} at ({x}, {y})")
        return True
    
    except Exception as e:
        logger.error(f"Error scrolling {direction} at ({x}, {y}): {e}")
        return False


def press_key(key_combination):
    """Press a key or key combination.
    
    Args:
        key_combination (str): Key name or combination (e.g., 'enter', 'ctrl+c', 'alt+tab')
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Check if it's a key combination (contains '+')
        if '+' in key_combination:
            # Parse key combination and use hotkey
            keys = [k.strip().lower() for k in key_combination.split('+')]
            pyautogui.hotkey(*keys)
            logger.info(f"Pressed key combination: {key_combination}")
        else:
            # Single key press
            pyautogui.press(key_combination.lower())
            logger.info(f"Pressed key: {key_combination}")
        
        return True
    
    except Exception as e:
        logger.error(f"Error pressing key '{key_combination}': {e}")
        return False


def validate_coordinates(x, y):
    """Validate that coordinates are within screen bounds.
    
    Args:
        x (int): X coordinate
        y (int): Y coordinate
        
    Returns:
        bool: True if valid, False otherwise
    """
    try:
        # Get screen dimensions
        screen_width, screen_height = pyautogui.size()
        
        # Check if coordinates are within bounds
        if 0 <= x < screen_width and 0 <= y < screen_height:
            return True
        else:
            logger.warning(f"Coordinates ({x}, {y}) out of bounds. Screen size: {screen_width}x{screen_height}")
            return False
    
    except Exception as e:
        logger.error(f"Error validating coordinates ({x}, {y}): {e}")
        return False

# Made with Bob
