"""Emergency kill switch using global keyboard listener.

Dev 2 (Ashish) - Executor & Safety
TODO: Implement kill switch functionality
- Use pynput to create global keyboard listener
- Listen for emergency stop hotkey (e.g., Ctrl+Shift+Esc or F12)
- Set kill_event from config.py when triggered
- Run listener in separate thread
- Provide visual/audio feedback when triggered
- Ensure kill switch works even when AXON has focus
- Log kill switch activations
"""

from pynput import keyboard
import threading
from config import kill_event, status_queue


# Default kill switch hotkey
KILL_HOTKEY = {keyboard.Key.f12}  # Press F12 to stop
# Alternative: {keyboard.Key.ctrl, keyboard.Key.shift, keyboard.Key.esc}


class KillSwitch:
    """Global keyboard listener for emergency stop."""
    
    def __init__(self):
        """Initialize kill switch."""
        self.listener = None
        self.current_keys = set()
        self.is_running = False
        print("[KILL SWITCH] Initialized (Press F12 to stop)")
        
    def start(self):
        """Start the kill switch listener in a separate thread.
        
        Returns:
            bool: True if started successfully
        """
        if self.is_running:
            print("[WARNING] Kill switch is already running")
            return False
        
        try:
            # Create pynput keyboard listener with on_press and on_release handlers
            self.listener = keyboard.Listener(
                on_press=self.on_press,
                on_release=self.on_release
            )
            
            # Start listener as daemon thread (non-blocking)
            self.listener.daemon = True
            self.listener.start()
            
            self.is_running = True
            print("[SUCCESS] Kill switch active - Press F12 to emergency stop")
            return True
            
        except Exception as e:
            print(f"[ERROR] Failed to start kill switch: {e}")
            return False
    
    def stop(self):
        """Stop the kill switch listener."""
        if not self.is_running:
            return
        
        try:
            if self.listener:
                self.listener.stop()
                self.listener = None
            
            self.is_running = False
            self.current_keys.clear()
            print("[KILL SWITCH] Deactivated")
            
        except Exception as e:
            print(f"[WARNING] Error stopping kill switch: {e}")
    
    def on_press(self, key):
        """Handle key press events.
        
        Args:
            key: Key that was pressed
        """
        try:
            # Add key to current_keys set
            self.current_keys.add(key)
            
            # Check if kill hotkey (F12) is pressed
            if key in KILL_HOTKEY:
                print(f"[KILL SWITCH] Kill hotkey detected: {key}")
                self.trigger()
                
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
    
    def trigger(self):
        """Trigger the kill switch to stop the agent."""
        print("\n" + "="*60)
        print("*** KILL SWITCH ACTIVATED - EMERGENCY STOP! ***")
        print("="*60 + "\n")
        
        # Set the kill event to signal all threads to stop
        kill_event.set()
        
        # Update status queue with stop message for UI
        try:
            status_queue.put({
                "status": "killed",
                "message": "Emergency stop activated by kill switch"
            })
        except Exception as e:
            print(f"[WARNING] Error updating status queue: {e}")
        
        print("[SUCCESS] Kill event set - Agent will stop gracefully")


def start_kill_switch():
    """Start the global kill switch listener.
    
    Returns:
        KillSwitch: Active kill switch instance or None if failed
    """
    try:
        # Create KillSwitch instance
        kill_switch = KillSwitch()
        
        # Start the listener
        if kill_switch.start():
            return kill_switch
        else:
            print("[ERROR] Failed to start kill switch")
            return None
            
    except Exception as e:
        print(f"[ERROR] Error initializing kill switch: {e}")
        return None


def stop_kill_switch(kill_switch):
    """Stop the kill switch listener.
    
    Args:
        kill_switch (KillSwitch): Kill switch instance to stop
    """
    if kill_switch is None:
        return
    
    try:
        kill_switch.stop()
    except Exception as e:
        print(f"[WARNING] Error during kill switch cleanup: {e}")

# Made with Bob
