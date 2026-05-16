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
        
    def start(self):
        """Start the kill switch listener in a separate thread.
        
        Returns:
            bool: True if started successfully
        """
        # TODO: Implement kill switch startup
        # 1. Create pynput keyboard listener
        # 2. Set up on_press and on_release handlers
        # 3. Start listener in non-blocking mode (separate thread)
        # 4. Log that kill switch is active
        pass
    
    def stop(self):
        """Stop the kill switch listener."""
        # TODO: Implement kill switch shutdown
        # 1. Stop the listener
        # 2. Clean up resources
        pass
    
    def on_press(self, key):
        """Handle key press events.
        
        Args:
            key: Key that was pressed
        """
        # TODO: Implement key press handler
        # 1. Add key to current_keys set
        # 2. Check if kill hotkey combination is pressed
        # 3. If yes, trigger kill switch
        pass
    
    def on_release(self, key):
        """Handle key release events.
        
        Args:
            key: Key that was released
        """
        # TODO: Implement key release handler
        # 1. Remove key from current_keys set
        pass
    
    def trigger(self):
        """Trigger the kill switch to stop the agent."""
        # TODO: Implement kill switch trigger
        # 1. Set kill_event
        # 2. Update status_queue with stop message
        # 3. Log the trigger
        # 4. Optionally play sound or show notification
        print("🛑 KILL SWITCH ACTIVATED - Stopping agent...")
        kill_event.set()
        status_queue.put({"status": "killed", "message": "Emergency stop activated"})


def start_kill_switch():
    """Start the global kill switch listener.
    
    Returns:
        KillSwitch: Active kill switch instance
    """
    # TODO: Implement kill switch initialization
    # 1. Create KillSwitch instance
    # 2. Start the listener
    # 3. Return instance for later cleanup
    pass


def stop_kill_switch(kill_switch):
    """Stop the kill switch listener.
    
    Args:
        kill_switch (KillSwitch): Kill switch instance to stop
    """
    # TODO: Implement kill switch cleanup
    pass

# Made with Bob
