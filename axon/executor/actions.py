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
from axon.config import kill_event, status_queue

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# Configure pyautogui safety settings
pyautogui.FAILSAFE = True  # Move mouse to corner to abort
pyautogui.PAUSE = 0.1  # Small delay between actions

# Action history for stuck-loop detection (tracks last 3 actions)
action_history = deque(maxlen=3)


def _is_stuck_loop(history):
    """Check if the last 3 actions are identical (stuck loop detection).
    
    Two actions are considered the same if:
    - Same action type (e.g., both "left_click")
    - Same coordinates (within 5 pixels tolerance for clicks/moves)
    - Same text (for type/key actions)
    
    Args:
        history (deque): Deque containing last 3 action dictionaries
        
    Returns:
        bool: True if stuck loop detected, False otherwise
    """
    if len(history) < 3:
        return False
    
    # Convert deque to list for easier comparison
    actions = list(history)
    
    # Check if all three actions have the same type
    action_types = [a.get('action') for a in actions]
    if len(set(action_types)) != 1:
        return False
    
    action_type = action_types[0]
    
    # For coordinate-based actions (clicks, moves, scroll)
    if action_type in ['left_click', 'right_click', 'middle_click', 'double_click', 'mouse_move', 'scroll']:
        coords = [a.get('coordinate', []) for a in actions]
        
        # Check if all have valid coordinates
        if not all(len(c) == 2 for c in coords):
            return False
        
        # Check if coordinates are within 5 pixels of each other
        for i in range(1, 3):
            x_diff = abs(coords[i][0] - coords[0][0])
            y_diff = abs(coords[i][1] - coords[0][1])
            if x_diff > 5 or y_diff > 5:
                return False
        
        # For scroll, also check direction and amount
        if action_type == 'scroll':
            directions = [a.get('direction') for a in actions]
            amounts = [a.get('amount') for a in actions]
            if len(set(directions)) != 1 or len(set(amounts)) != 1:
                return False
        
        return True
    
    # For text-based actions (type, key)
    elif action_type in ['type', 'key']:
        texts = [a.get('text', '') for a in actions]
        # All texts must be identical
        return len(set(texts)) == 1 and texts[0] != ''
    
    # For other actions (like 'done'), check if all are the same type
    return True


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
        
        # Check for stuck loop (same action 3 times in a row)
        if len(action_history) == 3 and _is_stuck_loop(action_history):
            logger.warning("🔴 STUCK LOOP DETECTED! Same action repeated 3 times in a row")
            logger.warning(f"Repeated action: {action_type}")
            
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
        if action_type == "mouse_move":
            coordinate = action_dict.get('coordinate', [])
            if len(coordinate) != 2:
                logger.error(f"Invalid coordinate for mouse_move: {coordinate}")
                success = False
            else:
                success = mouse_move(coordinate[0], coordinate[1])
        
        elif action_type == "left_click":
            coordinate = action_dict.get('coordinate', [])
            if len(coordinate) != 2:
                logger.error(f"Invalid coordinate for left_click: {coordinate}")
                success = False
            else:
                success = click(coordinate[0], coordinate[1], button='left')
        
        elif action_type == "right_click":
            coordinate = action_dict.get('coordinate', [])
            if len(coordinate) != 2:
                logger.error(f"Invalid coordinate for right_click: {coordinate}")
                success = False
            else:
                success = click(coordinate[0], coordinate[1], button='right')
        
        elif action_type == "middle_click":
            coordinate = action_dict.get('coordinate', [])
            if len(coordinate) != 2:
                logger.error(f"Invalid coordinate for middle_click: {coordinate}")
                success = False
            else:
                success = click(coordinate[0], coordinate[1], button='middle')
        
        elif action_type == "double_click":
            coordinate = action_dict.get('coordinate', [])
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
            coordinate = action_dict.get('coordinate', [])
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
