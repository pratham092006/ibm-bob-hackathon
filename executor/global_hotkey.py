"""Global hotkey listener for Alt+G functionality.

Implements two modes:
1. Alt+G without text selection: Opens task input dialog
2. Alt+G with text selection: Provides context-aware help
"""

from pynput import keyboard
import threading
import pyperclip
import time
from typing import Callable, Optional


class GlobalHotkey:
    """Global keyboard listener for Alt+G hotkey."""
    
    def __init__(self, on_task_dialog: Callable, on_context_help: Callable[[str], None]):
        """Initialize global hotkey listener.
        
        Args:
            on_task_dialog: Callback to open task input dialog
            on_context_help: Callback for context help with selected text
        """
        self.listener = None
        self.current_keys = set()
        self.is_running = False
        self.on_task_dialog = on_task_dialog
        self.on_context_help = on_context_help
        print("[GLOBAL HOTKEY] Initialized (Press Alt+G for task dialog or context help)")
        
    def start(self):
        """Start the global hotkey listener in a separate thread.
        
        Returns:
            bool: True if started successfully
        """
        if self.is_running:
            print("[WARNING] Global hotkey is already running")
            return False
        
        try:
            # Create pynput keyboard listener
            self.listener = keyboard.Listener(
                on_press=self.on_press,
                on_release=self.on_release
            )
            
            # Start listener as daemon thread (non-blocking)
            self.listener.daemon = True
            self.listener.start()
            
            self.is_running = True
            print("[SUCCESS] Global hotkey active - Press Alt+G to activate")
            return True
            
        except Exception as e:
            print(f"[ERROR] Failed to start global hotkey: {e}")
            return False
    
    def stop(self):
        """Stop the global hotkey listener."""
        if not self.is_running:
            return
        
        try:
            if self.listener:
                self.listener.stop()
                self.listener = None
            
            self.is_running = False
            self.current_keys.clear()
            print("[GLOBAL HOTKEY] Deactivated")
            
        except Exception as e:
            print(f"[WARNING] Error stopping global hotkey: {e}")
    
    def on_press(self, key):
        """Handle key press events.
        
        Args:
            key: Key that was pressed
        """
        try:
            # Add key to current_keys set
            self.current_keys.add(key)
            
            # Check if Alt+G is pressed
            # Alt key can be either alt_l or alt_r
            alt_pressed = (keyboard.Key.alt_l in self.current_keys or 
                          keyboard.Key.alt_r in self.current_keys or
                          keyboard.Key.alt in self.current_keys)
            
            # Check for 'g' key (both lowercase and uppercase)
            g_pressed = False
            try:
                if hasattr(key, 'char') and key.char and key.char.lower() == 'g':
                    g_pressed = True
            except AttributeError:
                pass
            
            if alt_pressed and g_pressed:
                print(f"[GLOBAL HOTKEY] Alt+G detected!")
                self.trigger_hotkey()
                
        except Exception as e:
            print(f"[WARNING] Error in on_press: {e}")
    
    def on_release(self, key):
        """Handle key release events.
        
        Args:
            key: Key that was released
        """
        try:
            # Remove key from current_keys set when released
            self.current_keys.discard(key)
            
        except Exception as e:
            print(f"[WARNING] Error in on_release: {e}")
    
    def trigger_hotkey(self):
        """Trigger the Alt+G hotkey action."""
        print("\n" + "="*60)
        print("*** ALT+G ACTIVATED ***")
        print("="*60 + "\n")
        
        # Try to get selected text from clipboard
        selected_text = self._get_selected_text()
        
        if selected_text and len(selected_text.strip()) > 0:
            # Context help mode - text is selected
            print(f"[GLOBAL HOTKEY] Context help mode - Selected text: '{selected_text[:50]}...'")
            try:
                self.on_context_help(selected_text)
            except Exception as e:
                print(f"[ERROR] Error in context help callback: {e}")
        else:
            # Task dialog mode - no text selected
            print("[GLOBAL HOTKEY] Task dialog mode - No text selected")
            try:
                self.on_task_dialog()
            except Exception as e:
                print(f"[ERROR] Error in task dialog callback: {e}")
    
    def _get_selected_text(self) -> Optional[str]:
        """Get currently selected text using clipboard.
        
        This method:
        1. Saves current clipboard content
        2. Simulates Ctrl+C to copy selected text
        3. Gets the new clipboard content
        4. Restores original clipboard content
        
        Returns:
            str: Selected text or None if no text selected
        """
        try:
            # Save current clipboard content
            original_clipboard = None
            try:
                original_clipboard = pyperclip.paste()
            except Exception:
                pass
            
            # Clear clipboard
            pyperclip.copy("")
            time.sleep(0.05)  # Small delay
            
            # Simulate Ctrl+C to copy selected text
            from pynput.keyboard import Controller, Key
            kb = Controller()
            
            # Press Ctrl+C
            kb.press(Key.ctrl)
            kb.press('c')
            kb.release('c')
            kb.release(Key.ctrl)
            
            # Wait for clipboard to update
            time.sleep(0.1)
            
            # Get clipboard content (selected text)
            selected_text = pyperclip.paste()
            
            # Restore original clipboard if it was different
            if original_clipboard is not None and original_clipboard != selected_text:
                # Wait a bit before restoring to avoid conflicts
                time.sleep(0.1)
                pyperclip.copy(original_clipboard)
            
            # Return selected text if it's not empty
            if selected_text and len(selected_text.strip()) > 0:
                return selected_text.strip()
            
            return None
            
        except Exception as e:
            print(f"[WARNING] Error getting selected text: {e}")
            return None


def start_global_hotkey(on_task_dialog: Callable, on_context_help: Callable[[str], None]):
    """Start the global hotkey listener.
    
    Args:
        on_task_dialog: Callback to open task input dialog
        on_context_help: Callback for context help with selected text
    
    Returns:
        GlobalHotkey: Active hotkey instance or None if failed
    """
    try:
        # Create GlobalHotkey instance
        hotkey = GlobalHotkey(on_task_dialog, on_context_help)
        
        # Start the listener
        if hotkey.start():
            return hotkey
        else:
            print("[ERROR] Failed to start global hotkey")
            return None
            
    except Exception as e:
        print(f"[ERROR] Error initializing global hotkey: {e}")
        return None


def stop_global_hotkey(hotkey):
    """Stop the global hotkey listener.
    
    Args:
        hotkey (GlobalHotkey): Hotkey instance to stop
    """
    if hotkey is None:
        return
    
    try:
        hotkey.stop()
    except Exception as e:
        print(f"[WARNING] Error during global hotkey cleanup: {e}")


# Made with Bob