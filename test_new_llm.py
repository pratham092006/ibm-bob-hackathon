"""Test script for the new LLM implementation with EasyOCR and Google GenAI SDK."""

import sys
import os

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all required modules can be imported."""
    print("=" * 60)
    print("TEST 1: Testing imports...")
    print("=" * 60)
    
    try:
        import easyocr
        print("✓ EasyOCR imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import EasyOCR: {e}")
        return False
    
    try:
        from google import genai
        print("✓ Google GenAI SDK imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import Google GenAI SDK: {e}")
        return False
    
    try:
        from dotenv import load_dotenv
        print("✓ python-dotenv imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import python-dotenv: {e}")
        return False
    
    try:
        from core.llm import get_screen_elements, call_llm
        print("✓ LLM module imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import LLM module: {e}")
        return False
    
    print("\n✓ All imports successful!\n")
    return True


def test_config():
    """Test that configuration loads correctly."""
    print("=" * 60)
    print("TEST 2: Testing configuration...")
    print("=" * 60)
    
    try:
        from config import GEMINI_API_KEY
        if GEMINI_API_KEY:
            print(f"✓ API key loaded: {GEMINI_API_KEY[:10]}...")
        else:
            print("✗ API key is empty")
            return False
    except Exception as e:
        print(f"✗ Failed to load config: {e}")
        return False
    
    print("\n✓ Configuration loaded successfully!\n")
    return True


def test_screen_capture():
    """Test screen capture and save to file."""
    print("=" * 60)
    print("TEST 3: Testing screen capture...")
    print("=" * 60)
    
    try:
        from core.capture import capture_screen
        
        print("Capturing screen...")
        screen_bytes = capture_screen()
        
        if screen_bytes:
            print(f"✓ Screen captured: {len(screen_bytes)} bytes")
            
            # Save to temporary file for testing
            test_path = "test_screen.jpg"
            with open(test_path, 'wb') as f:
                f.write(screen_bytes)
            print(f"✓ Saved to {test_path}")
            
            return test_path
        else:
            print("✗ Screen capture returned None")
            return None
            
    except Exception as e:
        print(f"✗ Screen capture failed: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_ocr(image_path):
    """Test EasyOCR text extraction."""
    print("=" * 60)
    print("TEST 4: Testing EasyOCR text extraction...")
    print("=" * 60)
    
    try:
        from core.llm import get_screen_elements
        
        print(f"Extracting text from {image_path}...")
        text_anchors = get_screen_elements(image_path)
        
        print(f"✓ Found {len(text_anchors)} text elements")
        
        if text_anchors:
            print("\nSample text elements:")
            for i, anchor in enumerate(text_anchors[:5], 1):
                text = anchor['text']
                coord = anchor['center_coordinate']
                print(f"  {i}. '{text}' at {coord}")
        
        print("\n✓ OCR test successful!\n")
        return True
        
    except Exception as e:
        print(f"✗ OCR test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_llm_call(image_path):
    """Test calling the LLM with a screen capture."""
    print("=" * 60)
    print("TEST 5: Testing LLM call...")
    print("=" * 60)
    
    try:
        from core.llm import call_llm
        
        # Read image bytes
        with open(image_path, 'rb') as f:
            image_bytes = f.read()
        
        print("Calling Gemini 2.5 Flash...")
        action = call_llm(
            screen_image=image_bytes,
            task_description="Test task: identify what's on screen",
            conversation_history=[]
        )
        
        print(f"\n✓ LLM responded successfully!")
        print(f"Action: {action.get('action')}")
        if 'coordinate' in action:
            print(f"Coordinate: {action['coordinate']}")
        if 'text' in action:
            print(f"Text: {action['text']}")
        
        print("\n✓ LLM call test successful!\n")
        return True
        
    except Exception as e:
        print(f"✗ LLM call failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("TESTING NEW LLM IMPLEMENTATION")
    print("=" * 60 + "\n")
    
    # Test 1: Imports
    if not test_imports():
        print("\n❌ Import test failed. Please install dependencies:")
        print("   pip install -r requirements.txt")
        return
    
    # Test 2: Configuration
    if not test_config():
        print("\n❌ Configuration test failed. Please check .env file.")
        return
    
    # Test 3: Screen capture
    image_path = test_screen_capture()
    if not image_path:
        print("\n❌ Screen capture test failed.")
        return
    
    # Test 4: OCR
    if not test_ocr(image_path):
        print("\n❌ OCR test failed.")
        return
    
    # Test 5: LLM call
    if not test_llm_call(image_path):
        print("\n❌ LLM call test failed.")
        return
    
    # Cleanup
    try:
        os.remove(image_path)
        print(f"Cleaned up {image_path}")
    except:
        pass
    
    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()

# Made with Bob
