"""Test script for Windows API integration.

This script tests the win_api.py module to ensure all functions work correctly.
Run this on Windows to verify window detection functionality.
"""

import sys
import time
from executor.win_api import (
    get_active_window,
    get_window_title,
    get_process_name,
    list_all_windows,
    bring_window_to_front,
    get_window_at_position,
    is_window_visible
)


def test_get_active_window():
    """Test getting the currently active window."""
    print("\n=== Testing get_active_window() ===")
    
    info = get_active_window()
    if info:
        print(f"✓ Active window detected:")
        print(f"  - Handle: {info['hwnd']}")
        print(f"  - Title: {info['title']}")
        print(f"  - Process: {info['process']}")
        print(f"  - PID: {info['pid']}")
        return True
    else:
        print("✗ Failed to get active window")
        return False


def test_get_window_title():
    """Test getting window title from handle."""
    print("\n=== Testing get_window_title() ===")
    
    info = get_active_window()
    if info:
        title = get_window_title(info['hwnd'])
        if title:
            print(f"✓ Window title: {title}")
            return True
        else:
            print("✗ Failed to get window title")
            return False
    else:
        print("✗ No active window to test with")
        return False


def test_get_process_name():
    """Test getting process name from PID."""
    print("\n=== Testing get_process_name() ===")
    
    info = get_active_window()
    if info:
        process = get_process_name(info['pid'])
        if process:
            print(f"✓ Process name: {process}")
            return True
        else:
            print("✗ Failed to get process name")
            return False
    else:
        print("✗ No active window to test with")
        return False


def test_list_all_windows():
    """Test listing all visible windows."""
    print("\n=== Testing list_all_windows() ===")
    
    windows = list_all_windows()
    if windows:
        print(f"✓ Found {len(windows)} visible windows:")
        # Show first 5 windows
        for i, win in enumerate(windows[:5]):
            print(f"  {i+1}. {win['process']}: {win['title'][:50]}")
        if len(windows) > 5:
            print(f"  ... and {len(windows) - 5} more")
        return True
    else:
        print("✗ No windows found")
        return False


def test_is_window_visible():
    """Test checking if a window is visible."""
    print("\n=== Testing is_window_visible() ===")
    
    info = get_active_window()
    if info:
        visible = is_window_visible(info['hwnd'])
        print(f"✓ Window {info['hwnd']} visible: {visible}")
        return True
    else:
        print("✗ No active window to test with")
        return False


def test_get_window_at_position():
    """Test getting window at specific position."""
    print("\n=== Testing get_window_at_position() ===")
    
    # Test at screen center (assuming 1920x1080)
    x, y = 960, 540
    hwnd = get_window_at_position(x, y)
    if hwnd:
        title = get_window_title(hwnd)
        print(f"✓ Window at ({x}, {y}): {title}")
        return True
    else:
        print(f"✗ No window found at ({x}, {y})")
        return False


def test_bring_window_to_front():
    """Test bringing a window to front."""
    print("\n=== Testing bring_window_to_front() ===")
    
    info = get_active_window()
    if info:
        # Try to bring the current window to front (should already be there)
        success = bring_window_to_front(info['hwnd'])
        if success:
            print(f"✓ Successfully brought window to front")
            return True
        else:
            print("✗ Failed to bring window to front")
            return False
    else:
        print("✗ No active window to test with")
        return False


def interactive_test():
    """Interactive test - switch between apps."""
    print("\n=== Interactive Test ===")
    print("This test will monitor the active window for 10 seconds.")
    print("Switch between different applications to test detection.")
    print("Starting in 3 seconds...\n")
    
    time.sleep(3)
    
    last_process = None
    for i in range(10):
        info = get_active_window()
        if info:
            if info['process'] != last_process:
                print(f"[{i}s] Switched to: {info['process']} - {info['title'][:50]}")
                last_process = info['process']
        time.sleep(1)
    
    print("\n✓ Interactive test complete")


def main():
    """Run all tests."""
    print("=" * 60)
    print("Windows API Integration Test Suite")
    print("=" * 60)
    
    if sys.platform != 'win32':
        print("\n✗ ERROR: This test must be run on Windows")
        return
    
    results = []
    
    # Run all tests
    results.append(("get_active_window", test_get_active_window()))
    results.append(("get_window_title", test_get_window_title()))
    results.append(("get_process_name", test_get_process_name()))
    results.append(("list_all_windows", test_list_all_windows()))
    results.append(("is_window_visible", test_is_window_visible()))
    results.append(("get_window_at_position", test_get_window_at_position()))
    results.append(("bring_window_to_front", test_bring_window_to_front()))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    # Run interactive test if user wants
    print("\n" + "=" * 60)
    response = input("Run interactive test? (y/n): ")
    if response.lower() == 'y':
        interactive_test()
    
    print("\n" + "=" * 60)
    print("All tests complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()

# Made with Bob
