"""Test script for the highlight/context help feature.

This script demonstrates how to use the Alt+G context help feature:
1. Run this script
2. Select some text in any application (Notepad, browser, etc.)
3. Press Alt+G
4. See the AI response in a transparent overlay

The script will also create a test text file you can use for testing.
"""

import os
import sys

def create_test_file():
    """Create a test text file with sample content for testing."""
    test_content = """
AXON Context Help Test File
===========================

Select any of the text below and press Alt+G to test the context help feature:

1. PYTHON CODE EXAMPLE:
   def fibonacci(n):
       if n <= 1:
           return n
       return fibonacci(n-1) + fibonacci(n-2)

2. TECHNICAL QUESTION:
   What is the difference between machine learning and deep learning?

3. MATH PROBLEM:
   If a train travels at 60 mph for 2.5 hours, how far does it travel?

4. DEFINITION REQUEST:
   What is quantum computing?

5. CODE DEBUGGING:
   Why does this code throw an error?
   x = [1, 2, 3]
   print(x[5])

6. EXPLANATION REQUEST:
   Explain how HTTP cookies work in web browsers.

7. TRANSLATION:
   Translate "Hello, how are you?" to Spanish.

8. SUMMARY REQUEST:
   Summarize the key features of Python programming language.

INSTRUCTIONS:
=============
1. Open this file in Notepad or any text editor
2. Select any text above (e.g., the Python code, a question, etc.)
3. Press Alt+G
4. Wait for the AI response to appear in a transparent overlay
5. The overlay will show the AI's answer to your selected text

TIPS:
=====
- Select complete sentences or code blocks for best results
- The AI will provide context-aware help based on what you select
- You can select text from ANY application, not just this file
- Try selecting text from web pages, PDFs, or other documents
"""
    
    # Create the test file on the desktop
    desktop = os.path.join(os.path.expanduser("~"), "Desktop")
    test_file_path = os.path.join(desktop, "AXON_Context_Help_Test.txt")
    
    try:
        with open(test_file_path, 'w', encoding='utf-8') as f:
            f.write(test_content)
        print(f"✅ Test file created: {test_file_path}")
        return test_file_path
    except Exception as e:
        print(f"❌ Failed to create test file: {e}")
        return None

def open_test_file(file_path):
    """Open the test file in Notepad."""
    try:
        os.startfile(file_path)
        print(f"✅ Opened test file in default text editor")
    except Exception as e:
        print(f"❌ Failed to open test file: {e}")

def main():
    """Main test function."""
    print("\n" + "="*60)
    print("AXON Context Help Feature Test")
    print("="*60 + "\n")
    
    print("This test will help you verify the Alt+G context help feature.\n")
    
    # Create test file
    print("Step 1: Creating test file...")
    test_file = create_test_file()
    
    if test_file:
        print("\nStep 2: Opening test file...")
        open_test_file(test_file)
        
        print("\n" + "="*60)
        print("HOW TO TEST:")
        print("="*60)
        print("1. Make sure AXON is running (python main.py)")
        print("2. In the opened text file, select any text")
        print("   (e.g., the Python code or a question)")
        print("3. Press Alt+G")
        print("4. Wait for the AI response overlay to appear")
        print("\nEXPECTED BEHAVIOR:")
        print("- A transparent overlay should appear with the AI's answer")
        print("- The overlay should be positioned near your cursor")
        print("- You can close the overlay by clicking the X button")
        print("\nCONSOLE MESSAGES TO LOOK FOR:")
        print("- [HOTKEY] Alt+G pressed - TEXT SELECTED")
        print("- [MODE] Context Help Mode")
        print("- [TEXT] Selected: '...'")
        print("- [CONTEXT] Requesting AI help for selected text...")
        print("- [CONTEXT] Received answer (XXX chars)")
        print("\nIf you see these messages, the feature is working correctly!")
        print("="*60 + "\n")
    else:
        print("\n❌ Failed to create test file. Please create a text file manually.")
        print("   Then select text and press Alt+G to test the feature.\n")

if __name__ == "__main__":
    main()

# Made with Bob
