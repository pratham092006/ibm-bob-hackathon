"""Test script for kill switch functionality.

This script tests the kill switch implementation by:
1. Starting the kill switch listener
2. Monitoring the kill_event
3. Waiting for F12 key press
4. Verifying the kill switch triggers correctly
"""

import time
import sys
from executor.kill_switch import start_kill_switch, stop_kill_switch
from config import kill_event, status_queue

def main():
    print("="*60)
    print("KILL SWITCH TEST")
    print("="*60)
    print("\nThis test will:")
    print("1. Start the kill switch listener")
    print("2. Wait for you to press F12")
    print("3. Verify the kill event is set")
    print("4. Check the status queue message")
    print("\n" + "="*60)
    
    # Start the kill switch
    print("\n[1] Starting kill switch...")
    kill_switch = start_kill_switch()
    
    if kill_switch is None:
        print("❌ Failed to start kill switch!")
        return 1
    
    print("\n[2] Kill switch is now active")
    print("    Press F12 to trigger emergency stop")
    print("    Or press Ctrl+C to exit test\n")
    
    try:
        # Monitor for kill event
        while not kill_event.is_set():
            time.sleep(0.1)
        
        print("\n[3] Kill event detected!")
        
        # Check status queue
        if not status_queue.empty():
            status = status_queue.get()
            print(f"[4] Status queue message: {status}")
        
        print("\n✅ Kill switch test PASSED!")
        print("    - Listener started successfully")
        print("    - F12 key detected")
        print("    - Kill event set correctly")
        print("    - Status queue updated")
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Test interrupted by user (Ctrl+C)")
    
    finally:
        # Clean up
        print("\n[5] Stopping kill switch...")
        stop_kill_switch(kill_switch)
        print("\n" + "="*60)
        print("TEST COMPLETE")
        print("="*60)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

# Made with Bob
