"""Test script for Gemini API integration.

This script tests:
1. Gemini API connection
2. Basic image analysis
3. Model switching
4. Response parsing
"""

import sys
import os
import io as io_module

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io_module.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io_module.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
from PIL import Image, ImageDraw, ImageFont
import io

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.llm import call_llm, switch_model, get_current_model, get_model_display_name


def create_test_image():
    """Create a simple test image with a button."""
    # Create a simple image with a button
    img = Image.new('RGB', (800, 600), color='white')
    draw = ImageDraw.Draw(img)
    
    # Draw a button
    button_rect = [300, 250, 500, 350]
    draw.rectangle(button_rect, fill='blue', outline='black', width=2)
    
    # Add text
    try:
        font = ImageFont.truetype("arial.ttf", 24)
    except:
        font = ImageFont.load_default()
    
    draw.text((350, 290), "Click Me", fill='white', font=font)
    
    # Convert to JPEG bytes
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='JPEG', quality=85)
    return img_bytes.getvalue()


def test_api_connection():
    """Test basic API connection."""
    print("=" * 60)
    print("TEST 1: API Connection")
    print("=" * 60)
    
    try:
        # Create test image
        print("Creating test image...")
        test_image = create_test_image()
        print(f"✓ Test image created ({len(test_image)} bytes)")
        
        # Test API call
        print(f"\nCalling Gemini API with model: {get_model_display_name()}")
        task = "Click the blue button"
        
        result = call_llm(test_image, task)
        
        print("\n✓ API call successful!")
        print(f"\nResponse:")
        print(f"  Action: {result.get('action', 'N/A')}")
        print(f"  Reasoning: {result.get('reasoning', 'N/A')}")
        
        if 'x' in result and 'y' in result:
            print(f"  Coordinates: ({result['x']}, {result['y']})")
        
        return True
        
    except Exception as e:
        print(f"\n✗ API call failed: {str(e)}")
        return False


def test_model_switching():
    """Test switching between models."""
    print("\n" + "=" * 60)
    print("TEST 2: Model Switching")
    print("=" * 60)
    
    try:
        # Test Flash model
        print("\nSwitching to Flash model...")
        if switch_model("flash"):
            print(f"✓ Switched to: {get_model_display_name()}")
            print(f"  Current model key: {get_current_model()}")
        else:
            print("✗ Failed to switch to Flash")
            return False
        
        # Test Pro model
        print("\nSwitching to Pro model...")
        if switch_model("pro"):
            print(f"✓ Switched to: {get_model_display_name()}")
            print(f"  Current model key: {get_current_model()}")
        else:
            print("✗ Failed to switch to Pro")
            return False
        
        # Switch back to Flash
        print("\nSwitching back to Flash...")
        if switch_model("flash"):
            print(f"✓ Switched to: {get_model_display_name()}")
        else:
            print("✗ Failed to switch back to Flash")
            return False
        
        return True
        
    except Exception as e:
        print(f"\n✗ Model switching failed: {str(e)}")
        return False


def test_response_parsing():
    """Test response parsing with different scenarios."""
    print("\n" + "=" * 60)
    print("TEST 3: Response Parsing")
    print("=" * 60)
    
    try:
        test_image = create_test_image()
        
        # Test different task types
        tasks = [
            "Click the blue button",
            "What do you see in this image?",
            "Type 'Hello World'",
        ]
        
        for i, task in enumerate(tasks, 1):
            print(f"\nTest {i}: {task}")
            result = call_llm(test_image, task)
            
            if result.get('action') == 'error':
                print(f"  ⚠ Error response: {result.get('reasoning', 'Unknown error')}")
            else:
                print(f"  ✓ Action: {result.get('action', 'N/A')}")
                print(f"  ✓ Reasoning: {result.get('reasoning', 'N/A')[:80]}...")
        
        return True
        
    except Exception as e:
        print(f"\n✗ Response parsing test failed: {str(e)}")
        return False


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("AXON GEMINI API INTEGRATION TEST")
    print("=" * 60)
    print(f"\nCurrent Model: {get_model_display_name()}")
    print(f"Model Key: {get_current_model()}")
    
    results = []
    
    # Run tests
    results.append(("API Connection", test_api_connection()))
    results.append(("Model Switching", test_model_switching()))
    results.append(("Response Parsing", test_response_parsing()))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{test_name:.<40} {status}")
    
    total_passed = sum(1 for _, passed in results if passed)
    total_tests = len(results)
    
    print(f"\nTotal: {total_passed}/{total_tests} tests passed")
    
    if total_passed == total_tests:
        print("\n🎉 All tests passed! Gemini integration is working correctly.")
        return 0
    else:
        print("\n⚠ Some tests failed. Please review the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

# Made with Bob
