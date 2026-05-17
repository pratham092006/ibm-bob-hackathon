"""Test script for browser actions through execute_action().

This tests the full integration of browser automation with AXON's
action execution system.

Usage:
    python axon/test_execute_action_browser.py
"""

import sys
import os
import time

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from executor.actions import execute_action


def test_browser_actions_via_execute_action():
    """Test browser automation through AXON's execute_action function."""
    
    print("=" * 60)
    print("Testing Browser Actions via execute_action()")
    print("=" * 60)
    print()
    
    # Define action sequence using AXON's action dictionary format
    actions = [
        {
            "action": "browser_navigate",
            "url": "https://github.com"
        },
        {
            "action": "browser_press_key",
            "key": "/"
        },
        {
            "action": "browser_press_key",
            "key": "p"
        },
        {
            "action": "browser_press_key",
            "key": "y"
        },
        {
            "action": "browser_press_key",
            "key": "t"
        },
        {
            "action": "browser_press_key",
            "key": "h"
        },
        {
            "action": "browser_press_key",
            "key": "o"
        },
        {
            "action": "browser_press_key",
            "key": "n"
        },
        {
            "action": "browser_press_key",
            "key": "Enter"
        },
        {
            "action": "browser_screenshot",
            "path": "axon/bob-reports/execute_action_test.png"
        },
        {
            "action": "browser_close"
        }
    ]
    
    print("Executing action sequence:")
    print("-" * 60)
    
    success_count = 0
    fail_count = 0
    
    for i, action in enumerate(actions, 1):
        action_type = action.get('action')
        print(f"\n[{i}/{len(actions)}] Executing: {action_type}")
        
        # Show action details
        for key, value in action.items():
            if key != 'action':
                print(f"  {key}: {value}")
        
        # Execute the action
        result = execute_action(action)
        
        if result:
            print(f"  ✅ SUCCESS")
            success_count += 1
        else:
            print(f"  ❌ FAILED")
            fail_count += 1
        
        # Small delay between actions
        time.sleep(0.5)
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"Total Actions: {len(actions)}")
    print(f"Successful: {success_count}")
    print(f"Failed: {fail_count}")
    print(f"Success Rate: {(success_count/len(actions)*100):.1f}%")
    
    if fail_count == 0:
        print("\n✅ ALL TESTS PASSED!")
        return True
    else:
        print(f"\n⚠️  {fail_count} test(s) failed")
        return False


def main():
    """Main test runner."""
    
    print("\n" + "=" * 60)
    print("AXON Browser Actions Integration Test")
    print("Testing execute_action() with browser automation")
    print("=" * 60)
    print()
    
    try:
        success = test_browser_actions_via_execute_action()
        
        print("\n" + "=" * 60)
        if success:
            print("RESULT: ✅ INTEGRATION TEST PASSED")
            print("\nBrowser actions are fully integrated with AXON!")
            print("The AI can now control web browsers through execute_action().")
        else:
            print("RESULT: ⚠️  SOME TESTS FAILED")
            print("\nCheck the error messages above for details.")
        print("=" * 60)
        
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        return 1
    except Exception as e:
        print(f"\n\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())

# Made with Bob
