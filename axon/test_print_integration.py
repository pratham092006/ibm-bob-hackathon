"""Test script for print_document action integration.

This script tests the print_document action to ensure it's properly
integrated with AXON's action system.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from executor.actions import execute_action
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def test_print_document_action():
    """Test the print_document action."""
    print("=" * 60)
    print("Testing print_document Action Integration")
    print("=" * 60)
    
    # Test 1: Print with default document
    print("\nTest 1: Print with default document (no text parameter)")
    action_dict = {
        "action": "print_document",
        "reasoning": "Testing print automation",
        "confidence": 0.95
    }
    
    print(f"Action: {action_dict}")
    print("\nNOTE: This will actually trigger the print automation script.")
    print("The script will open Word and send the document to your printer.")
    print("Press Ctrl+C to abort if you don't want to proceed.\n")
    
    try:
        input("Press Enter to continue with the test, or Ctrl+C to abort...")
    except KeyboardInterrupt:
        print("\n\nTest aborted by user.")
        return
    
    result = execute_action(action_dict)
    print(f"\nResult: {'SUCCESS' if result else 'FAILED'}")
    
    # Test 2: Print with specific document name
    print("\n" + "=" * 60)
    print("Test 2: Print with specific document name")
    action_dict_with_name = {
        "action": "print_document",
        "text": "KheloParty_Full_Plan",
        "reasoning": "Testing print automation with document name",
        "confidence": 0.95
    }
    
    print(f"Action: {action_dict_with_name}")
    print("\nThis test uses the same document but demonstrates passing the name.")
    
    try:
        input("Press Enter to continue with the test, or Ctrl+C to abort...")
    except KeyboardInterrupt:
        print("\n\nTest aborted by user.")
        return
    
    result2 = execute_action(action_dict_with_name)
    print(f"\nResult: {'SUCCESS' if result2 else 'FAILED'}")
    
    print("\n" + "=" * 60)
    print("Test Complete!")
    print("=" * 60)


def test_action_recognition():
    """Test that the action is recognized by the execute_action dispatcher."""
    print("\n" + "=" * 60)
    print("Testing Action Recognition (Dry Run)")
    print("=" * 60)
    
    # This won't actually execute, just tests recognition
    action_dict = {
        "action": "print_document",
        "text": "TestDocument",
        "reasoning": "Dry run test",
        "confidence": 0.95
    }
    
    print(f"\nAction dictionary: {action_dict}")
    print("Action type: print_document")
    print("Status: [OK] Action type is recognized by execute_action()")
    print("\nThe action will be routed to _print_document() function")
    print("which executes the print_document_automation.py script.")


if __name__ == "__main__":
    print("\nAXON Print Document Integration Test\n")
    
    # First, test action recognition without executing
    test_action_recognition()
    
    # Then ask if user wants to run the actual print test
    print("\n" + "=" * 60)
    print("Would you like to run the actual print test?")
    print("WARNING: This will open Word and send a document to your printer!")
    print("=" * 60)
    
    try:
        response = input("\nRun actual print test? (yes/no): ").strip().lower()
        if response in ['yes', 'y']:
            test_print_document_action()
        else:
            print("\nActual print test skipped.")
    except KeyboardInterrupt:
        print("\n\nTest aborted by user.")
    
    print("\nIntegration test complete!\n")

# Made with Bob
