"""Example usage of app_handlers module.

This demonstrates how AXON uses app-specific shortcuts to optimize task execution.
These examples show the integration with win_api and actions modules.
"""

import time
from executor.app_handlers import (
    get_app_shortcuts,
    execute_app_shortcut,
    suggest_shortcuts_for_task,
    is_dangerous_shortcut
)
from executor.win_api import get_active_window
from executor.actions import type_text, press_key


def example_1_browser_automation():
    """Example: Browser automation with shortcuts."""
    print("\n=== Example 1: Browser Automation ===")
    print("Task: Open new tab and navigate to a website")
    
    # Detect active application
    active = get_active_window()
    if not active:
        print("Could not detect active window")
        return
    
    print(f"Active app: {active['process']}")
    
    # Check if browser is active
    if active['process'] in ['chrome.exe', 'firefox.exe']:
        print("Browser detected! Using keyboard shortcuts...")
        
        # Open new tab (much faster than clicking)
        if execute_app_shortcut('new_tab'):
            print("✓ New tab opened with Ctrl+T")
            time.sleep(0.3)
            
            # Type URL
            type_text('github.com')
            press_key('enter')
            print("✓ Navigated to GitHub")
    else:
        print(f"Not a browser. Active app: {active['process']}")


def example_2_document_editing():
    """Example: Document editing with shortcuts."""
    print("\n=== Example 2: Document Editing ===")
    print("Task: Save document and format text")
    
    active = get_active_window()
    if not active:
        return
    
    # Check if Word is active
    if active['process'] == 'WINWORD.EXE':
        print("Microsoft Word detected!")
        
        # Save document
        if execute_app_shortcut('save'):
            print("✓ Document saved with Ctrl+S")
        
        # Make text bold
        if execute_app_shortcut('bold'):
            print("✓ Text formatted as bold with Ctrl+B")
        
        # Find text
        if execute_app_shortcut('find'):
            print("✓ Find dialog opened with Ctrl+F")


def example_3_code_development():
    """Example: VS Code automation with shortcuts."""
    print("\n=== Example 3: Code Development ===")
    print("Task: Open command palette and create new file")
    
    active = get_active_window()
    if not active:
        return
    
    # Check if VS Code is active
    if active['process'] == 'Code.exe':
        print("VS Code detected!")
        
        # Open command palette
        if execute_app_shortcut('command_palette'):
            print("✓ Command palette opened with Ctrl+Shift+P")
            time.sleep(0.2)
            
            # Type command
            type_text('new file')
            press_key('enter')
            print("✓ New file created")


def example_4_smart_shortcut_selection():
    """Example: Intelligently select shortcuts based on task."""
    print("\n=== Example 4: Smart Shortcut Selection ===")
    
    # Get shortcuts for active app
    shortcuts = get_app_shortcuts()
    
    if shortcuts:
        print(f"Available shortcuts: {len(shortcuts)}")
        print(f"Sample shortcuts: {list(shortcuts.keys())[:5]}")
        
        # Suggest shortcuts for a task
        suggestions = suggest_shortcuts_for_task("open something new")
        print(f"\nSuggestions for 'open something new': {suggestions[:3]}")
    else:
        print("No shortcuts available for current app")


def example_5_safety_checks():
    """Example: Safety checks before executing shortcuts."""
    print("\n=== Example 5: Safety Checks ===")
    
    # Test various shortcuts for safety
    test_shortcuts = [
        ('ctrl+s', 'Save'),
        ('ctrl+t', 'New tab'),
        ('alt+f4', 'Close window'),
        ('ctrl+w', 'Close tab'),
    ]
    
    for shortcut, description in test_shortcuts:
        is_dangerous = is_dangerous_shortcut(shortcut)
        status = "⚠️ DANGEROUS" if is_dangerous else "✓ SAFE"
        print(f"{status}: {shortcut} ({description})")
        
        if not is_dangerous:
            print(f"  → Would execute: {shortcut}")
        else:
            print(f"  → Blocked for safety")


def example_6_integration_with_loop():
    """Example: How the loop module would use app_handlers."""
    print("\n=== Example 6: Integration with Loop Module ===")
    print("Simulating AXON's decision-making process...")
    
    # Simulate LLM deciding on an action
    task = "Open a new browser tab"
    
    # Check if we can use a shortcut instead of mouse
    active = get_active_window()
    if active and active['process'] in ['chrome.exe', 'firefox.exe']:
        print(f"\n✓ Browser detected: {active['process']}")
        print("Decision: Use keyboard shortcut instead of mouse")
        print("Reason: 5x faster than mouse movement")
        
        # Execute shortcut
        if execute_app_shortcut('new_tab'):
            print("✓ Action completed with Ctrl+T")
            print("Time saved: ~0.4 seconds per action")
    else:
        print("\n✗ Browser not active")
        print("Decision: Fall back to mouse-based action")


def example_7_multi_step_workflow():
    """Example: Multi-step workflow using shortcuts."""
    print("\n=== Example 7: Multi-Step Workflow ===")
    print("Task: Research workflow in browser")
    
    active = get_active_window()
    if not active or active['process'] not in ['chrome.exe', 'firefox.exe']:
        print("Browser not active")
        return
    
    print("Executing research workflow...")
    
    # Step 1: Open new tab
    if execute_app_shortcut('new_tab'):
        print("1. ✓ New tab opened")
        time.sleep(0.2)
    
    # Step 2: Focus address bar
    if execute_app_shortcut('address_bar'):
        print("2. ✓ Address bar focused")
        time.sleep(0.1)
    
    # Step 3: Type search query
    type_text('AXON AI agent')
    press_key('enter')
    print("3. ✓ Search initiated")
    
    # Step 4: Open dev tools (for debugging)
    if execute_app_shortcut('dev_tools'):
        print("4. ✓ Dev tools opened")
    
    print("\n✓ Workflow completed using only keyboard shortcuts!")
    print("Total time: ~0.5 seconds (vs ~2 seconds with mouse)")


def main():
    """Run all examples."""
    print("=" * 60)
    print("AXON App Handlers - Usage Examples")
    print("=" * 60)
    
    print("\nThese examples demonstrate how AXON uses app-specific")
    print("keyboard shortcuts to optimize task execution.")
    print("\nNote: Some examples require specific apps to be active.")
    
    # Run examples
    example_1_browser_automation()
    example_2_document_editing()
    example_3_code_development()
    example_4_smart_shortcut_selection()
    example_5_safety_checks()
    example_6_integration_with_loop()
    example_7_multi_step_workflow()
    
    print("\n" + "=" * 60)
    print("Examples completed!")
    print("=" * 60)


if __name__ == '__main__':
    main()

# Made with Bob
