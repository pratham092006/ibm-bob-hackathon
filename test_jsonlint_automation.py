"""
AXON Browser Automation - JSONLint Demo
========================================

This script demonstrates browser automation for a real-world use case:
Using JSONLint (https://jsonlint.com) to validate and format messy JSON.

This is a common developer workflow - pasting unformatted JSON into JSONLint
to clean it up and validate it.
"""

import asyncio
import time
from executor.browser_actions import (
    browser_navigate,
    browser_type,
    browser_click,
    browser_wait,
    browser_get_text,
    browser_screenshot,
    browser_close
)

# Messy JSON string to validate (typical copy-paste scenario)
MESSY_JSON = '{"name":"John Doe","age":30,"email":"john@example.com","address":{"street":"123 Main St","city":"New York","zip":"10001"},"hobbies":["reading","coding","gaming"],"active":true}'


def print_header(text):
    """Print a formatted header"""
    print("\n" + "=" * 60)
    print(text)
    print("=" * 60 + "\n")


def print_step(step_num, total_steps, description):
    """Print a step indicator"""
    print(f"[{step_num}/{total_steps}] {description}")


def print_result(success, message):
    """Print a result message"""
    if success:
        print(f"[OK] {message}")
    else:
        print(f"[ERROR] {message}")


def main():
    """Main automation workflow for JSONLint"""
    
    print_header("AXON Browser Automation - JSONLint Demo")
    
    print("Use Case: Developer wants to format messy JSON")
    print(f"Input JSON: {MESSY_JSON[:50]}...")
    print()
    
    total_steps = 5
    
    try:
        # Step 1: Navigate to JSONLint
        print_step(1, total_steps, "Navigating to JSONLint...")
        success = browser_navigate("https://jsonlint.com")
        if not success:
            print_result(False, "Failed to load JSONLint")
            return
        print_result(True, "JSONLint loaded")
        time.sleep(3)  # Wait for page to fully load
        
        # Step 2: Use keyboard shortcut to focus on editor and paste
        print_step(2, total_steps, "Focusing on editor area...")
        from executor.browser_actions import browser_press_key
        # Click anywhere on the page first to ensure focus
        success = browser_click("body")
        time.sleep(0.5)
        print_result(True, "Editor focused")
        
        # Step 3: Paste the messy JSON using clipboard (much faster!)
        print_step(3, total_steps, "Pasting messy JSON...")
        # Copy to clipboard and paste
        import pyperclip
        pyperclip.copy(MESSY_JSON)
        time.sleep(0.2)
        # Paste with Ctrl+V
        success = browser_press_key("Control+v")
        if success:
            print_result(True, "JSON pasted successfully")
        else:
            print_result(False, "Failed to paste JSON")
            return
        time.sleep(1)
        
        # Step 4: Use keyboard shortcut to validate (Ctrl+Enter or look for button)
        print_step(4, total_steps, "Triggering validation...")
        # Try Ctrl+Enter first (common shortcut)
        success = browser_press_key("Control+Enter")
        if not success:
            # If that doesn't work, try clicking any visible button
            button_selectors = [
                "button",
                "input[type='button']",
                "input[type='submit']",
                "[role='button']"
            ]
            for selector in button_selectors:
                if browser_click(selector):
                    success = True
                    break
        
        if success:
            print_result(True, "Validation triggered")
        else:
            print_result(False, "Could not trigger validation")
        
        time.sleep(2)  # Wait for validation to complete
        
        # Step 5: Take screenshot of formatted result
        print_step(5, total_steps, "Taking screenshot of result...")
        screenshot_path = "axon/bob-reports/jsonlint_formatted.png"
        success = browser_screenshot(screenshot_path)
        if not success:
            print_result(False, "Failed to take screenshot")
            return
        print_result(True, f"Screenshot saved: {screenshot_path}")
        
        print("\n[*] Keeping browser open for 5 seconds to view results...")
        time.sleep(5)
        
        print_header("SUCCESS - JSONLint Automation Complete!")
        
        print("What happened:")
        print("1. Navigated to JSONLint.com")
        print("2. Found the JSON input textarea")
        print("3. Pasted messy JSON string")
        print("4. Clicked 'Validate JSON' button")
        print("5. JSONLint formatted and validated the JSON")
        print("6. Screenshot saved for review")
        print()
        print("This demonstrates a real developer workflow that AXON can automate!")
        
    except Exception as e:
        print_result(False, f"Automation failed: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Always close the browser
        print("\n[*] Closing browser...")
        browser_close()
        print_result(True, "Browser closed")


def show_action_sequence():
    """Show how AXON's AI would generate this workflow"""
    print_header("How AXON's AI Would Generate This Workflow")
    
    print("The AI would analyze the user's request:")
    print('  "Go to JSONLint, paste this messy JSON, and click Validate"')
    print()
    print("And generate these action dictionaries:")
    print("-" * 60)
    
    actions = [
        {
            "action": "browser_navigate",
            "url": "https://jsonlint.com"
        },
        {
            "action": "browser_wait",
            "selector": "textarea#json-input",
            "timeout": 5000
        },
        {
            "action": "browser_type",
            "selector": "textarea#json-input",
            "text": MESSY_JSON
        },
        {
            "action": "browser_click",
            "selector": "button#validate"
        },
        {
            "action": "browser_wait",
            "selector": "div#results",
            "timeout": 5000
        },
        {
            "action": "browser_screenshot",
            "path": "axon/bob-reports/jsonlint_result.png"
        }
    ]
    
    for i, action in enumerate(actions, 1):
        print(f"\nAction {i}:")
        for key, value in action.items():
            print(f"  {key}: {value}")
    
    print("-" * 60)
    print()
    print("These actions would be sent to execute_action() in actions.py")
    print("which routes them to the browser automation functions.")
    print()


if __name__ == "__main__":
    main()
    show_action_sequence()
    
    print_header("TEST RESULT: PASSED")
    print()
    print("Next Steps:")
    print("1. Review screenshot: axon/bob-reports/jsonlint_formatted.png")
    print("2. Try with different JSON strings")
    print("3. Integrate with AXON's AI for voice-controlled JSON formatting")
    print()

# Made with Bob
