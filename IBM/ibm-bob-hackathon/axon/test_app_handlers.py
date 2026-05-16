"""Test suite for app_handlers module.

Tests the app-specific shortcut functionality including:
- Auto-detection of active application
- Shortcut retrieval
- Shortcut execution
- Safety checks
"""

import sys
import logging
from executor.app_handlers import (
    get_app_shortcuts,
    execute_app_shortcut,
    suggest_shortcuts_for_task,
    is_dangerous_shortcut,
    APP_SHORTCUTS
)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def test_get_app_shortcuts_explicit():
    """Test getting shortcuts for a specific application."""
    print("\n=== Test: get_app_shortcuts with explicit app name ===")
    
    # Test Chrome shortcuts
    shortcuts = get_app_shortcuts('chrome.exe')
    print(f"Chrome shortcuts: {len(shortcuts)} found")
    print(f"Sample shortcuts: {list(shortcuts.keys())[:5]}")
    
    assert 'new_tab' in shortcuts, "Chrome should have 'new_tab' shortcut"
    assert shortcuts['new_tab'] == 'ctrl+t', "new_tab should be ctrl+t"
    print("✓ Chrome shortcuts retrieved correctly")
    
    # Test VS Code shortcuts
    shortcuts = get_app_shortcuts('Code.exe')
    print(f"\nVS Code shortcuts: {len(shortcuts)} found")
    assert 'command_palette' in shortcuts, "VS Code should have 'command_palette' shortcut"
    print("✓ VS Code shortcuts retrieved correctly")
    
    # Test unknown app
    shortcuts = get_app_shortcuts('unknown.exe')
    print(f"\nUnknown app shortcuts: {len(shortcuts)} found")
    assert len(shortcuts) == 0, "Unknown app should return empty dict"
    print("✓ Unknown app returns empty dict")


def test_get_app_shortcuts_auto_detect():
    """Test auto-detection of active application."""
    print("\n=== Test: get_app_shortcuts with auto-detection ===")
    
    # This will attempt to detect the active window
    shortcuts = get_app_shortcuts()
    print(f"Auto-detected app shortcuts: {len(shortcuts)} found")
    
    if shortcuts:
        print(f"Sample shortcuts: {list(shortcuts.keys())[:5]}")
        print("✓ Auto-detection successful")
    else:
        print("⚠ No shortcuts found (might not be on Windows or no supported app active)")


def test_execute_app_shortcut():
    """Test executing app-specific shortcuts."""
    print("\n=== Test: execute_app_shortcut ===")
    
    # Test with explicit app name (won't actually execute on non-Windows)
    print("\nTesting shortcut execution for Chrome...")
    
    # This should work even if Chrome isn't active (just tests the logic)
    result = execute_app_shortcut('new_tab', 'chrome.exe')
    print(f"Execute 'new_tab' for Chrome: {result}")
    
    # Test with non-existent shortcut
    result = execute_app_shortcut('nonexistent_action', 'chrome.exe')
    print(f"Execute non-existent shortcut: {result}")
    assert result == False, "Non-existent shortcut should return False"
    print("✓ Non-existent shortcut handled correctly")
    
    # Test with unknown app
    result = execute_app_shortcut('new_tab', 'unknown.exe')
    print(f"Execute shortcut for unknown app: {result}")
    assert result == False, "Unknown app should return False"
    print("✓ Unknown app handled correctly")


def test_suggest_shortcuts_for_task():
    """Test shortcut suggestion system."""
    print("\n=== Test: suggest_shortcuts_for_task ===")
    
    # Test with Chrome
    suggestions = suggest_shortcuts_for_task("open new tab", 'chrome.exe')
    print(f"Suggestions for 'open new tab' in Chrome: {len(suggestions)} shortcuts")
    print(f"Sample suggestions: {suggestions[:5]}")
    
    assert len(suggestions) > 0, "Should return suggestions for Chrome"
    assert 'new_tab' in suggestions, "Should include 'new_tab' in suggestions"
    print("✓ Suggestions returned correctly")
    
    # Test with unknown app
    suggestions = suggest_shortcuts_for_task("do something", 'unknown.exe')
    print(f"\nSuggestions for unknown app: {len(suggestions)} shortcuts")
    assert len(suggestions) == 0, "Unknown app should return empty list"
    print("✓ Unknown app returns empty suggestions")


def test_is_dangerous_shortcut():
    """Test dangerous shortcut detection."""
    print("\n=== Test: is_dangerous_shortcut ===")
    
    # Test dangerous shortcuts
    dangerous_tests = [
        ('alt+f4', True, "Close window"),
        ('ctrl+w', True, "Close tab"),
        ('ctrl+alt+delete', True, "System interrupt"),
        ('win+l', True, "Lock screen"),
        ('ctrl+q', True, "Quit application"),
    ]
    
    for shortcut, expected, description in dangerous_tests:
        result = is_dangerous_shortcut(shortcut)
        status = "✓" if result == expected else "✗"
        print(f"{status} {shortcut} ({description}): {result}")
        assert result == expected, f"{shortcut} should be {'dangerous' if expected else 'safe'}"
    
    # Test safe shortcuts
    safe_tests = [
        ('ctrl+s', False, "Save"),
        ('ctrl+c', False, "Copy"),
        ('ctrl+v', False, "Paste"),
        ('ctrl+t', False, "New tab"),
        ('f5', False, "Refresh"),
    ]
    
    print("\nTesting safe shortcuts:")
    for shortcut, expected, description in safe_tests:
        result = is_dangerous_shortcut(shortcut)
        status = "✓" if result == expected else "✗"
        print(f"{status} {shortcut} ({description}): {result}")
        assert result == expected, f"{shortcut} should be {'dangerous' if expected else 'safe'}"
    
    print("✓ All dangerous shortcut checks passed")


def test_app_shortcuts_dictionary():
    """Test the APP_SHORTCUTS dictionary structure."""
    print("\n=== Test: APP_SHORTCUTS dictionary ===")
    
    print(f"Total applications with shortcuts: {len(APP_SHORTCUTS)}")
    
    for app_name, shortcuts in APP_SHORTCUTS.items():
        print(f"\n{app_name}: {len(shortcuts)} shortcuts")
        # Verify all shortcuts are strings
        for action, key_combo in shortcuts.items():
            assert isinstance(action, str), f"Action name should be string: {action}"
            assert isinstance(key_combo, str), f"Key combo should be string: {key_combo}"
    
    print("\n✓ APP_SHORTCUTS dictionary is valid")


def test_integration_example():
    """Test the integration example from the task description."""
    print("\n=== Test: Integration Example ===")
    
    print("Example usage flow:")
    print("1. Detect active app")
    print("2. Execute shortcut if Chrome is active")
    
    # Simulate the example from task description
    from executor.win_api import get_active_window
    
    active = get_active_window()
    if active:
        print(f"Active window: {active.get('process')} - {active.get('title')}")
        
        if active.get('process') == 'chrome.exe':
            print("Chrome is active, executing 'new_tab' shortcut...")
            result = execute_app_shortcut('new_tab')
            print(f"Result: {result}")
        else:
            print(f"Active app is {active.get('process')}, not Chrome")
    else:
        print("Could not detect active window (might not be on Windows)")
    
    print("✓ Integration example completed")


def main():
    """Run all tests."""
    print("=" * 60)
    print("AXON App Handlers Test Suite")
    print("=" * 60)
    
    try:
        test_app_shortcuts_dictionary()
        test_get_app_shortcuts_explicit()
        test_get_app_shortcuts_auto_detect()
        test_is_dangerous_shortcut()
        test_suggest_shortcuts_for_task()
        test_execute_app_shortcut()
        test_integration_example()
        
        print("\n" + "=" * 60)
        print("✓ ALL TESTS PASSED")
        print("=" * 60)
        
    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()

# Made with Bob
