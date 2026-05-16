"""Test the full AXON flow with debug output.

This script tests:
1. Task submission
2. Agent loop activation
3. Screen capture
4. LLM call
5. Action execution
"""

import sys
import time
from config import task_queue, status_queue, kill_event
from core.loop import start_monitoring, activate_agent
import threading

def monitor_status():
    """Monitor status queue and print updates."""
    print("[STATUS MONITOR] Started")
    while not kill_event.is_set():
        try:
            if not status_queue.empty():
                status = status_queue.get_nowait()
                print(f"[STATUS] {status}")
        except:
            pass
        time.sleep(0.1)

def main():
    print("="*60)
    print("AXON FULL FLOW TEST")
    print("="*60)
    print()
    
    # Start monitoring thread
    print("[TEST] Starting monitoring thread...")
    monitor_thread = threading.Thread(target=start_monitoring, daemon=True)
    monitor_thread.start()
    time.sleep(1)
    
    # Start status monitor
    print("[TEST] Starting status monitor...")
    status_thread = threading.Thread(target=monitor_status, daemon=True)
    status_thread.start()
    time.sleep(0.5)
    
    # Submit a test task
    test_task = "Click the Start button"
    print(f"\n[TEST] Submitting task: {test_task}")
    activate_agent(test_task)
    
    # Wait and monitor
    print("[TEST] Monitoring for 30 seconds...")
    print("[TEST] Press Ctrl+C to stop\n")
    
    try:
        time.sleep(30)
    except KeyboardInterrupt:
        print("\n[TEST] Interrupted by user")
    
    # Stop
    print("\n[TEST] Setting kill event...")
    kill_event.set()
    time.sleep(1)
    
    print("\n" + "="*60)
    print("TEST COMPLETE")
    print("="*60)

if __name__ == "__main__":
    main()

# Made with Bob