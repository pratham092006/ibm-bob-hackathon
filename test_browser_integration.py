"""Test script for integrated browser automation with AXON.

This demonstrates how AXON's AI can control browser automation
through the action system using Playwright.

Usage:
    python axon/test_browser_integration.py
"""

import sys
import os
import time

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from executor.browser_actions import (
    browser_navigate,
    browser_press_key,
    browser_wait,
    browser_screenshot,
    browser_close
)


def test_github_search_workflow():
    """Test the GitHub search workflow using AXON's browser actions."""
    
    print("=" * 60)
    print("AXON Browser Automation Test - GitHub Search")
    print("=" * 60)
    print()
    
    try:
        # Step 1: Navigate to GitHub
        print("[1/5] Navigating to GitHub...")
        if not browser_navigate("https://github.com"):
            print("[ERROR] Failed to navigate to GitHub")
            return False
        print("[OK] GitHub loaded")
        time.sleep(1)
        
        # Step 2: Open search using keyboard shortcut
        print("\n[2/5] Opening search (pressing '/')...")
        if not browser_press_key("/"):
            print("[ERROR] Failed to press '/' key")
            return False
        print("[OK] Search opened")
        time.sleep(1)
        
        # Step 3: Type search query
        print("\n[3/5] Typing 'React'...")
        # Use keyboard to type (since search is already focused)
        if not browser_press_key("R"):
            return False
        if not browser_press_key("e"):
            return False
        if not browser_press_key("a"):
            return False
        if not browser_press_key("c"):
            return False
        if not browser_press_key("t"):
            return False
        print("[OK] Typed 'React'")
        time.sleep(1)
        
        # Step 4: Submit search
        print("\n[4/5] Submitting search (pressing Enter)...")
        if not browser_press_key("Enter"):
            print("[ERROR] Failed to press Enter")
            return False
        print("[OK] Search submitted")
        time.sleep(3)  # Wait for results to load
        
        # Step 5: Take screenshot
        print("\n[5/5] Taking screenshot...")
        screenshot_path = "axon/bob-reports/github_search_results.png"
        if not browser_screenshot(screenshot_path):
            print("[ERROR] Failed to take screenshot")
            return False
        print(f"[OK] Screenshot saved to: {screenshot_path}")
        
        # Keep browser open for a moment
        print("\n[*] Keeping browser open for 5 seconds...")
        time.sleep(5)
        
        print("\n[SUCCESS] Browser automation test completed!")
        return True
        
    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Cleanup
        print("\n[*] Closing browser...")
        browser_close()
        print("[OK] Browser closed")


def test_action_dict_format():
    """Demonstrate how AXON's AI would send browser actions.
    
    This shows the action dictionary format that would be used
    by AXON's AI loop to control the browser.
    """
    
    print("\n" + "=" * 60)
    print("Example: How AXON's AI Would Control the Browser")
    print("=" * 60)
    print()
    
    # Example action sequence that AXON's AI might generate
    action_sequence = [
        {
            "action": "browser_navigate",
            "url": "https://github.com"
        },
        {
            "action": "browser_press_key",
            "key": "/"
        },
        {
            "action": "browser_type",
            "selector": "input[type='text']",
            "text": "React"
        },
        {
            "action": "browser_press_key",
            "key": "Enter"
        },
        {
            "action": "browser_wait",
            "selector": ".repo-list",
            "timeout": 10000
        },
        {
            "action": "browser_screenshot",
            "path": "axon/bob-reports/ai_controlled_screenshot.png"
        },
        {
            "action": "browser_close"
        }
    ]
    
    print("Action sequence that AXON's AI would generate:")
    print("-" * 60)
    for i, action in enumerate(action_sequence, 1):
        print(f"\nAction {i}:")
        for key, value in action.items():
            print(f"  {key}: {value}")
    
    print("\n" + "-" * 60)
    print("\nThese actions would be sent to execute_action() in actions.py")
    print("which would route them to the appropriate browser_* functions.")


def main():
    """Main test runner."""
    
    print("\n" + "=" * 60)
    print("AXON Integrated Browser Automation Test Suite")
    print("=" * 60)
    print()
    print("This test demonstrates:")
    print("1. Browser automation integrated with AXON's action system")
    print("2. How the AI can control web browsers through actions")
    print("3. Playwright working alongside pyautogui actions")
    print()
    
    # Run the actual browser test
    success = test_github_search_workflow()
    
    # Show the action format example
    test_action_dict_format()
    
    # Summary
    print("\n" + "=" * 60)
    if success:
        print("TEST RESULT: PASSED")
        print("\nNext Steps:")
        print("1. Add browser action handlers to executor/actions.py")
        print("2. Update AXON's AI prompt to include browser actions")
        print("3. Test with full AXON AI loop")
    else:
        print("TEST RESULT: FAILED")
        print("\nCheck the error messages above for details.")
    print("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[WARNING] Test interrupted by user")
        browser_close()
    except Exception as e:
        print(f"\n\n[ERROR] Fatal error: {e}")
        import traceback
        traceback.print_exc()
        browser_close()

# Made with Bob
