"""Test script for action execution functions.

Tests all implemented functions in actions.py to ensure they work correctly.
"""

import time
from executor.actions import (
    validate_coordinates,
    mouse_move,
    click,
    type_text,
    scroll,
    press_key,
    execute_action
)

def test_validate_coordinates():
    """Test coordinate validation."""
    print("\n=== Testing validate_coordinates ===")
    
    # Valid coordinates
    assert validate_coordinates(100, 100) == True, "Valid coordinates should return True"
    print("✓ Valid coordinates (100, 100) passed")
    
    # Invalid coordinates (negative)
    assert validate_coordinates(-10, 100) == False, "Negative x should return False"
    print("✓ Invalid coordinates (-10, 100) correctly rejected")
    
    # Invalid coordinates (too large)
    assert validate_coordinates(99999, 99999) == False, "Out of bounds should return False"
    print("✓ Invalid coordinates (99999, 99999) correctly rejected")
    
    print("✓ All coordinate validation tests passed!")


def test_mouse_move():
    """Test mouse movement."""
    print("\n=== Testing mouse_move ===")
    
    # Move to center of screen
    result = mouse_move(500, 500)
    assert result == True, "Mouse move should succeed"
    print("✓ Mouse moved to (500, 500)")
    time.sleep(0.5)
    
    # Try invalid coordinates
    result = mouse_move(-100, -100)
    assert result == False, "Invalid coordinates should fail"
    print("✓ Invalid mouse move correctly rejected")
    
    print("✓ All mouse movement tests passed!")


def test_click():
    """Test click actions."""
    print("\n=== Testing click ===")
    
    # Left click
    result = click(500, 500, button='left')
    assert result == True, "Left click should succeed"
    print("✓ Left click at (500, 500)")
    time.sleep(0.3)
    
    # Right click
    result = click(500, 500, button='right')
    assert result == True, "Right click should succeed"
    print("✓ Right click at (500, 500)")
    time.sleep(0.3)
    
    # Double click
    result = click(500, 500, clicks=2)
    assert result == True, "Double click should succeed"
    print("✓ Double click at (500, 500)")
    time.sleep(0.3)
    
    print("✓ All click tests passed!")


def test_type_text():
    """Test text typing."""
    print("\n=== Testing type_text ===")
    print("Note: This will type text wherever the cursor is focused!")
    print("Waiting 3 seconds - click on a text editor if needed...")
    time.sleep(3)
    
    result = type_text("Hello AXON!")
    assert result == True, "Type text should succeed"
    print("✓ Text typed successfully")
    time.sleep(0.5)
    
    print("✓ All text typing tests passed!")


def test_scroll():
    """Test scrolling."""
    print("\n=== Testing scroll ===")
    
    # Scroll down
    result = scroll(500, 500, direction='down', amount=3)
    assert result == True, "Scroll down should succeed"
    print("✓ Scrolled down at (500, 500)")
    time.sleep(0.5)
    
    # Scroll up
    result = scroll(500, 500, direction='up', amount=3)
    assert result == True, "Scroll up should succeed"
    print("✓ Scrolled up at (500, 500)")
    time.sleep(0.5)
    
    print("✓ All scroll tests passed!")


def test_press_key():
    """Test key presses."""
    print("\n=== Testing press_key ===")
    
    # Single key
    result = press_key('space')
    assert result == True, "Single key press should succeed"
    print("✓ Pressed space key")
    time.sleep(0.3)
    
    # Key combination
    result = press_key('ctrl+a')
    assert result == True, "Key combination should succeed"
    print("✓ Pressed ctrl+a")
    time.sleep(0.3)
    
    print("✓ All key press tests passed!")


def test_execute_action():
    """Test the main action dispatcher."""
    print("\n=== Testing execute_action ===")
    
    # Test mouse_move action
    action = {"action": "mouse_move", "coordinate": [600, 600]}
    result = execute_action(action)
    assert result == True, "Mouse move action should succeed"
    print("✓ execute_action: mouse_move")
    time.sleep(0.3)
    
    # Test left_click action
    action = {"action": "left_click", "coordinate": [600, 600]}
    result = execute_action(action)
    assert result == True, "Left click action should succeed"
    print("✓ execute_action: left_click")
    time.sleep(0.3)
    
    # Test type action
    action = {"action": "type", "text": " Test!"}
    result = execute_action(action)
    assert result == True, "Type action should succeed"
    print("✓ execute_action: type")
    time.sleep(0.3)
    
    # Test key action
    action = {"action": "key", "text": "enter"}
    result = execute_action(action)
    assert result == True, "Key action should succeed"
    print("✓ execute_action: key")
    time.sleep(0.3)
    
    # Test scroll action
    action = {"action": "scroll", "coordinate": [600, 600], "direction": "down", "amount": 2}
    result = execute_action(action)
    assert result == True, "Scroll action should succeed"
    print("✓ execute_action: scroll")
    time.sleep(0.3)
    
    # Test invalid action
    action = {"action": "invalid_action"}
    result = execute_action(action)
    assert result == False, "Invalid action should fail"
    print("✓ execute_action: invalid action correctly rejected")
    
    print("✓ All execute_action tests passed!")


def main():
    """Run all tests."""
    print("=" * 60)
    print("AXON Action Execution Tests")
    print("=" * 60)
    print("\nWARNING: These tests will move your mouse and type text!")
    print("Make sure you're ready and have a safe environment.")
    print("\nStarting tests in 3 seconds...")
    time.sleep(3)
    
    try:
        test_validate_coordinates()
        test_mouse_move()
        test_click()
        test_type_text()
        test_scroll()
        test_press_key()
        test_execute_action()
        
        print("\n" + "=" * 60)
        print("✓ ALL TESTS PASSED!")
        print("=" * 60)
        
    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
    except Exception as e:
        print(f"\n✗ ERROR: {e}")


if __name__ == "__main__":
    main()

# Made with Bob
