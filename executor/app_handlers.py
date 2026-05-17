"""App-Specific Handlers — keyboard-shortcut-based navigation.

This module provides per-app handlers that use keyboard shortcuts and 
app-specific navigation patterns instead of screenshot + coordinate guessing.

Why this works better than vision:
- Uses the app's OWN navigation shortcuts (guaranteed to work)
- No coordinates, no screenshots, no OCR, no AI for execution
- Handles common apps: Discord, Chrome, Notepad, VS Code, etc.

Usage:
    handler = get_app_handler("discord")
    if handler:
        success = handler.navigate_to_dm("Pratham")
        handler.send_message("Hii")
    else:
        # fall back to vision-based approach
"""

import time
import subprocess
import pyautogui
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# ------------------------------------------------------------------
# Base class
# ------------------------------------------------------------------

class AppHandler:
    """Base class for app-specific keyboard handlers."""
    
    APP_NAME: str = ""
    WINDOW_TITLE_PATTERN: str = ""
    
    def is_running(self) -> bool:
        """Check if the app window is currently visible."""
        try:
            import pywinauto
            wins = pywinauto.findwindows.find_windows(title_re=self.WINDOW_TITLE_PATTERN)
            return len(wins) > 0
        except Exception:
            return False
    
    def focus(self) -> bool:
        """Bring the app window to foreground."""
        try:
            from pywinauto import Application
            app = Application(backend="uia").connect(title_re=self.WINDOW_TITLE_PATTERN)
            win = app.top_window()
            win.set_focus()
            time.sleep(0.3)
            return True
        except Exception as e:
            logger.warning(f"[{self.APP_NAME}] Could not focus window: {e}")
            return False

    def _press(self, key: str, delay: float = 0.15):
        pyautogui.press(key)
        time.sleep(delay)

    def _hotkey(self, *keys, delay: float = 0.2):
        pyautogui.hotkey(*keys)
        time.sleep(delay)

    def _type(self, text: str, delay: float = 0.1):
        """Type text via clipboard for reliability."""
        try:
            import pyperclip
            pyperclip.copy(text)
            time.sleep(0.05)
            pyautogui.hotkey('ctrl', 'v')
        except ImportError:
            pyautogui.write(text, interval=0.04)
        time.sleep(delay)

    def _sleep(self, seconds: float):
        time.sleep(seconds)


# ------------------------------------------------------------------
# Discord Handler
# ------------------------------------------------------------------

class DiscordHandler(AppHandler):
    """
    Discord navigation using keyboard shortcuts.
    
    Key shortcuts:
    - Ctrl+K  : Quick Switcher (find any user/channel/server by name)
    - Enter   : Confirm / open selection
    
    This completely bypasses screenshot + coordinate guessing.
    After Ctrl+K -> type username -> Enter, the DM is open and
    the message input is auto-focused. Just type + Enter to send.
    """
    
    APP_NAME = "Discord"
    WINDOW_TITLE_PATTERN = ".*Discord.*"
    
    def navigate_to_dm(self, username: str) -> bool:
        """Open a DM with a user via Discord Quick Switcher (Ctrl+K)."""
        try:
            logger.info(f"[Discord] Opening DM with '{username}' via Ctrl+K")
            
            if not self.focus():
                logger.warning("[Discord] Window not found, cannot navigate")
                return False
            
            # Open Quick Switcher
            self._hotkey('ctrl', 'k')
            self._sleep(0.5)
            
            # Type username
            self._type(username, delay=0.5)
            
            # Wait for search results
            self._sleep(0.7)
            
            # Select first result
            self._press('enter', delay=0.8)
            
            logger.info(f"[Discord] Navigated to DM: {username}")
            return True
            
        except Exception as e:
            logger.error(f"[Discord] navigate_to_dm failed: {e}")
            return False
    
    def focus_message_input(self) -> bool:
        """Focus the message input at the bottom of the chat."""
        try:
            # After Ctrl+K navigation, input is auto-focused.
            # As fallback, click at the bottom-center of the screen.
            screen_w, screen_h = pyautogui.size()
            input_x = screen_w // 2
            input_y = int(screen_h * 0.96)
            pyautogui.click(input_x, input_y)
            time.sleep(0.3)
            return True
        except Exception as e:
            logger.error(f"[Discord] focus_message_input failed: {e}")
            return False
    
    def send_message(self, text: str) -> bool:
        """Type and send a message in the currently open DM."""
        try:
            logger.info(f"[Discord] Sending message: '{text}'")
            
            # Ensure input field is focused
            self.focus_message_input()
            
            # Type the message
            self._type(text, delay=0.3)
            
            # Send with Enter
            self._press('enter', delay=0.2)
            
            logger.info(f"[Discord] Message sent!")
            return True
            
        except Exception as e:
            logger.error(f"[Discord] send_message failed: {e}")
            return False
    
    def full_dm_flow(self, username: str, message: str) -> bool:
        """Complete: navigate to DM + send message."""
        logger.info(f"[Discord] Full DM flow: to={username}, msg='{message}'")
        
        if not self.navigate_to_dm(username):
            logger.error("[Discord] Failed to navigate to DM")
            return False
        
        self._sleep(1.2)  # Wait for chat to load
        
        if not self.send_message(message):
            logger.error("[Discord] Failed to send message")
            return False
        
        logger.info("[Discord] Full DM flow complete!")
        return True


# ------------------------------------------------------------------
# Chrome Handler
# ------------------------------------------------------------------

class ChromeHandler(AppHandler):
    """Chrome browser navigation using keyboard shortcuts."""
    
    APP_NAME = "Chrome"
    WINDOW_TITLE_PATTERN = ".*Google Chrome.*"
    
    def navigate_to_url(self, url: str) -> bool:
        """Navigate to a URL using Ctrl+L (address bar shortcut)."""
        try:
            if not self.focus():
                return False
            self._hotkey('ctrl', 'l')
            self._sleep(0.2)
            self._type(url, delay=0.2)
            self._press('enter', delay=1.0)
            return True
        except Exception as e:
            logger.error(f"[Chrome] navigate_to_url failed: {e}")
            return False


# ------------------------------------------------------------------
# Generic UIA Handler (for native Win32 apps)
# ------------------------------------------------------------------

class UIAHandler(AppHandler):
    """
    Generic UIA handler using pywinauto.
    Works for native Windows apps: Notepad, File Explorer, Settings, etc.
    """
    
    def __init__(self, window_title_pattern: str, app_name: str = ""):
        self.WINDOW_TITLE_PATTERN = window_title_pattern
        self.APP_NAME = app_name or window_title_pattern
    
    def find_and_click(self, element_name: str = None, control_type: str = None,
                       auto_id: str = None) -> bool:
        """Find a UI element by name/type and click it precisely."""
        try:
            from pywinauto import Application
            app = Application(backend="uia").connect(title_re=self.WINDOW_TITLE_PATTERN)
            win = app.top_window()
            win.set_focus()
            
            kwargs = {}
            if element_name:
                kwargs['title'] = element_name
            if control_type:
                kwargs['control_type'] = control_type
            if auto_id:
                kwargs['auto_id'] = auto_id
            
            element = win.child_window(**kwargs)
            element.click_input()
            time.sleep(0.2)
            return True
            
        except Exception as e:
            logger.error(f"[{self.APP_NAME}] find_and_click failed: {e}")
            return False
    
    def find_and_type(self, text: str, element_name: str = None,
                      control_type: str = "Edit", auto_id: str = None) -> bool:
        """Find a text input element and type into it."""
        try:
            from pywinauto import Application
            app = Application(backend="uia").connect(title_re=self.WINDOW_TITLE_PATTERN)
            win = app.top_window()
            win.set_focus()
            
            kwargs = {'control_type': control_type}
            if element_name:
                kwargs['title'] = element_name
            if auto_id:
                kwargs['auto_id'] = auto_id
            
            element = win.child_window(**kwargs)
            element.click_input()
            element.type_keys(text, with_spaces=True)
            time.sleep(0.1)
            return True
            
        except Exception as e:
            logger.error(f"[{self.APP_NAME}] find_and_type failed: {e}")
            return False
    
    def dump_elements(self) -> list:
        """Debug utility: list all accessible UI elements."""
        try:
            from pywinauto import Application
            app = Application(backend="uia").connect(title_re=self.WINDOW_TITLE_PATTERN)
            win = app.top_window()
            elements = []
            def walk(parent, depth=0):
                if depth > 4:
                    return
                for child in parent.children():
                    try:
                        elements.append({
                            'name': child.window_text(),
                            'type': child.element_info.control_type,
                            'rect': str(child.rectangle()),
                            'depth': depth
                        })
                        walk(child, depth + 1)
                    except Exception:
                        pass
            walk(win)
            return elements
        except Exception as e:
            logger.error(f"[{self.APP_NAME}] dump_elements failed: {e}")
            return []


# ------------------------------------------------------------------
# Handler registry
# ------------------------------------------------------------------

_HANDLERS = {
    "discord":      DiscordHandler,
    "chrome":       ChromeHandler,
    "google chrome": ChromeHandler,
}


def get_app_handler(app_name: str) -> Optional[AppHandler]:
    """Get a keyboard/UIA handler for the given app.
    
    Returns None if no specific handler exists (will fall back to vision).
    """
    return _HANDLERS.get(app_name.lower().strip(), lambda: None)()


def parse_task_intent(task: str) -> Optional[dict]:
    """Parse a task string into structured intent for direct execution.
    
    Handles common task patterns WITHOUT calling the LLM.
    Only returns a result if the task is unambiguous.
    
    Returns:
        dict with intent, or None if LLM planning is needed.
    """
    import re
    task_lower = task.lower().strip()
    
    # Discord DM: "message/dm/text [user] [message text]"
    if 'discord' in task_lower or any(w in task_lower for w in ['message', 'dm', 'msg']):
        parts = re.search(
            r'(?:message|msg|dm|text|send|tell|say to|write to)\s+(\w+)[,\s]+["\']?(.+?)["\']?\s*$',
            task_lower
        )
        if parts:
            target = parts.group(1).strip()
            text = parts.group(2).strip()
            text = text[0].upper() + text[1:]  # Capitalize
            return {"app": "discord", "action": "dm", "target": target, "text": text}
    
    # Chrome URL navigation
    url_m = re.search(
        r'(?:go to|open|navigate to|visit)\s+(https?://\S+|www\.\S+|\w+\.(?:com|org|net|io|co)\S*)',
        task_lower
    )
    if url_m and ('chrome' in task_lower or 'browser' in task_lower or 'go to' in task_lower or 'navigate' in task_lower):
        url = url_m.group(1)
        if not url.startswith('http'):
            url = 'https://' + url
        return {"app": "chrome", "action": "navigate", "url": url}
    
    return None


def execute_intent(intent: dict) -> bool:
    """Execute a structured intent using app handlers.
    
    Args:
        intent: Output from parse_task_intent()
        
    Returns:
        True if execution succeeded.
    """
    app_name = intent.get("app", "")
    action = intent.get("action", "")
    
    handler = get_app_handler(app_name)
    if not handler:
        logger.warning(f"[AppHandlers] No handler for '{app_name}'")
        return False
    
    # Open app if not running
    if not handler.is_running():
        logger.info(f"[AppHandlers] {app_name} not running, launching...")
        pyautogui.press('win')
        time.sleep(0.3)
        pyautogui.write(app_name, interval=0.05)
        time.sleep(0.5)
        pyautogui.press('enter')
        time.sleep(4.0)  # Wait for app to fully load
    else:
        handler.focus()
    
    if isinstance(handler, DiscordHandler) and action == "dm":
        return handler.full_dm_flow(intent.get("target", ""), intent.get("text", ""))
    
    if isinstance(handler, ChromeHandler) and action == "navigate":
        return handler.navigate_to_url(intent.get("url", ""))
    
    return False

# Made with Bob
