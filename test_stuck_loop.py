"""Test script for stuck-loop detection and action logging.

Tests the new safety features added to actions.py:
1. Stuck-loop detection (same action 3 times triggers kill_event)
2. Action logging to session_log.json
"""

import sys
import time
import json
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from executor.actions import execute_action, action_history
from config import kill_event, status_queue


def test_stuck_loop_detection():
    """Test that repeating the same action 3 times triggers stuck-loop detection."""
    print("\n" + "="*60)
    print("TEST 1: Stuck-Loop Detection")
    print("="*60)
    
    # Clear any previous state
    kill_event.clear()
    action_history.clear()
    while not status_queue.empty():
        status_queue.get()
    
    # Create a test action (mouse_move to same location)
    test_action = {
        "action": "mouse_move",
        "coordinate": [500, 500]
    }
    
    print("\n1. Executing action 1st time...")
    result1 = execute_action(test_action)
    print(f"   Result: {result1}, Kill event set: {kill_event.is_set()}")
    
    print("\n2. Executing action 2nd time (same coordinates)...")
    result2 = execute_action(test_action)
    print(f"   Result: {result2}, Kill event set: {kill_event.is_set()}")
    
    print("\n3. Executing action 3rd time (should trigger stuck-loop)...")
    result3 = execute_action(test_action)
    print(f"   Result: {result3}, Kill event set: {kill_event.is_set()}")
    
    # Check if stuck signal was sent to status_queue
    if not status_queue.empty():
        stuck_signal = status_queue.get()
        print(f"\n✅ Stuck signal received:")
        print(f"   Type: {stuck_signal.get('type')}")
        print(f"   Message: {stuck_signal.get('message')}")
    else:
        print("\n❌ No stuck signal in status_queue")
    
    # Verify kill_event was set
    if kill_event.is_set():
        print("✅ Kill event was set correctly")
    else:
        print("❌ Kill event was NOT set")
    
    return kill_event.is_set()


def test_action_logging():
    """Test that actions are logged to session_log.json."""
    print("\n" + "="*60)
    print("TEST 2: Action Logging")
    print("="*60)
    
    # Clear previous state
    kill_event.clear()
    action_history.clear()
    
    # Delete existing log file if it exists
    log_file = Path(__file__).parent / "session_log.json"
    if log_file.exists():
        log_file.unlink()
        print(f"\n✅ Cleared existing log file: {log_file}")
    
    # Execute various actions
    test_actions = [
        {"action": "mouse_move", "coordinate": [100, 100]},
        {"action": "left_click", "coordinate": [200, 200]},
        {"action": "type", "text": "Hello World"},
        {"action": "key", "text": "ctrl+s"},
    ]
    
    print("\nExecuting test actions...")
    for i, action in enumerate(test_actions, 1):
        print(f"{i}. {action.get('action')}")
        execute_action(action)
        time.sleep(0.1)  # Small delay between actions
    
    # Check if log file was created
    if log_file.exists():
        print(f"\n✅ Log file created: {log_file}")
        
        # Read and display log contents
        with open(log_file, 'r', encoding='utf-8') as f:
            logs = json.load(f)
        
        print(f"\n✅ Total actions logged: {len(logs)}")
        print("\nLog entries:")
        for i, log in enumerate(logs, 1):
            print(f"\n  Entry {i}:")
            print(f"    Timestamp: {log.get('timestamp')}")
            print(f"    Action: {log.get('action')}")
            print(f"    Success: {log.get('success')}")
            print(f"    Execution time: {log.get('execution_time_ms'):.2f}ms")
        
        return len(logs) == len(test_actions)
    else:
        print(f"\n❌ Log file NOT created: {log_file}")
        return False


def test_stuck_loop_with_tolerance():
    """Test that coordinates within 5 pixels are considered the same."""
    print("\n" + "="*60)
    print("TEST 3: Stuck-Loop with Coordinate Tolerance")
    print("="*60)
    
    # Clear state
    kill_event.clear()
    action_history.clear()
    while not status_queue.empty():
        status_queue.get()
    
    # Create actions with coordinates within 5 pixels
    actions = [
        {"action": "left_click", "coordinate": [500, 500]},
        {"action": "left_click", "coordinate": [502, 503]},  # Within 5 pixels
        {"action": "left_click", "coordinate": [498, 501]},  # Within 5 pixels
    ]
    
    print("\nExecuting clicks with similar coordinates (within 5px)...")
    for i, action in enumerate(actions, 1):
        coord = action['coordinate']
        print(f"{i}. Click at ({coord[0]}, {coord[1]})")
        result = execute_action(action)
        print(f"   Result: {result}, Kill event: {kill_event.is_set()}")
    
    if kill_event.is_set():
        print("\n✅ Stuck-loop detected with coordinate tolerance")
        return True
    else:
        print("\n❌ Stuck-loop NOT detected")
        return False


def test_different_actions_no_stuck():
    """Test that different actions don't trigger stuck-loop."""
    print("\n" + "="*60)
    print("TEST 4: Different Actions (No Stuck-Loop)")
    print("="*60)
    
    # Clear state
    kill_event.clear()
    action_history.clear()
    
    # Execute different actions
    actions = [
        {"action": "mouse_move", "coordinate": [100, 100]},
        {"action": "left_click", "coordinate": [200, 200]},
        {"action": "type", "text": "test"},
    ]
    
    print("\nExecuting different actions...")
    for i, action in enumerate(actions, 1):
        print(f"{i}. {action.get('action')}")
        execute_action(action)
    
    if not kill_event.is_set():
        print("\n✅ No stuck-loop detected (correct)")
        return True
    else:
        print("\n❌ Stuck-loop incorrectly detected")
        return False


def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("STUCK-LOOP DETECTION & ACTION LOGGING TESTS")
    print("="*60)
    
    results = []
    
    # Run tests
    results.append(("Stuck-Loop Detection", test_stuck_loop_detection()))
    results.append(("Action Logging", test_action_logging()))
    results.append(("Coordinate Tolerance", test_stuck_loop_with_tolerance()))
    results.append(("Different Actions", test_different_actions_no_stuck()))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed!")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

# Made with Bob
