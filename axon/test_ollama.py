"""Test script for Ollama integration with AXON.

This script tests the Ollama local model integration by:
1. Checking if Ollama is running
2. Testing the API connection
3. Making a simple vision request
"""

import os
import sys
import requests
import json
from PIL import Image, ImageDraw, ImageFont
import io
import base64

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import OLLAMA_BASE_URL, OLLAMA_MODEL

def test_ollama_connection():
    """Test if Ollama is running and accessible."""
    print("[TEST] Checking Ollama connection...")
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
        if response.status_code == 200:
            print(f"[OK] Ollama is running at {OLLAMA_BASE_URL}")
            return True
        else:
            print(f"[ERROR] Ollama returned status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"[ERROR] Cannot connect to Ollama at {OLLAMA_BASE_URL}")
        print("[INFO] Make sure Ollama is running: ollama serve")
        return False
    except Exception as e:
        print(f"[ERROR] {e}")
        return False


def test_model_availability():
    """Test if the configured model is available."""
    print(f"\n[TEST] Checking if model '{OLLAMA_MODEL}' is available...")
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
        if response.status_code == 200:
            data = response.json()
            models = [model['name'] for model in data.get('models', [])]
            
            if OLLAMA_MODEL in models:
                print(f"[OK] Model '{OLLAMA_MODEL}' is available")
                return True
            else:
                print(f"[ERROR] Model '{OLLAMA_MODEL}' not found")
                print(f"[INFO] Available models: {', '.join(models)}")
                print(f"[INFO] Pull the model with: ollama pull {OLLAMA_MODEL}")
                return False
    except Exception as e:
        print(f"[ERROR] {e}")
        return False


def create_test_image():
    """Create a simple test image with text."""
    print("\n[TEST] Creating test image...")
    
    # Create a simple image with text
    img = Image.new('RGB', (800, 600), color='white')
    draw = ImageDraw.Draw(img)
    
    # Draw some text
    try:
        font = ImageFont.truetype("arial.ttf", 40)
    except:
        font = ImageFont.load_default()
    
    draw.text((50, 50), "AXON Test Image", fill='black', font=font)
    draw.text((50, 150), "Click the button below:", fill='black', font=font)
    
    # Draw a button
    draw.rectangle([50, 250, 250, 350], outline='blue', width=3)
    draw.text((80, 280), "Submit", fill='blue', font=font)
    
    print("[OK] Test image created")
    return img


def test_ollama_vision():
    """Test Ollama with a vision request."""
    print("\n[TEST] Testing Ollama vision capabilities...")
    
    # Create test image
    img = create_test_image()
    
    # Convert to bytes
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='JPEG')
    img_bytes = img_byte_arr.getvalue()
    
    # Encode to base64
    image_base64 = base64.b64encode(img_bytes).decode('utf-8')
    
    # Prepare request
    url = f"{OLLAMA_BASE_URL}/api/generate"
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": "Describe what you see in this image. What text is visible?",
        "images": [image_base64],
        "stream": False
    }
    
    try:
        print(f"[INFO] Sending request to Ollama...")
        response = requests.post(url, json=payload, timeout=60)
        response.raise_for_status()
        
        data = response.json()
        response_text = data.get("response", "")
        
        print(f"[OK] Ollama responded successfully!")
        print(f"\n[RESPONSE]")
        print(f"{response_text}")
        print(f"\n[INFO] Response length: {len(response_text)} characters")
        
        return True
        
    except requests.exceptions.Timeout:
        print("[ERROR] Request timed out (model might be loading)")
        print("[INFO] First request can be slow as model loads into memory")
        return False
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False


def test_ollama_with_llm_module():
    """Test Ollama through the AXON LLM module."""
    print("\n[TEST] Testing Ollama through AXON LLM module...")
    
    try:
        from core.llm import call_llm
        
        # Create test image
        img = create_test_image()
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='JPEG')
        img_bytes = img_byte_arr.getvalue()
        
        print("[INFO] Calling LLM module...")
        result = call_llm(
            screen_image=img_bytes,
            task_description="Click the Submit button",
            conversation_history=[]
        )
        
        print(f"[OK] LLM module returned successfully!")
        print(f"\n[RESULT]")
        print(json.dumps(result, indent=2))
        
        if "action" in result:
            print(f"\n[OK] Valid action returned: {result['action']}")
            return True
        else:
            print(f"\n[ERROR] No action in result")
            return False
            
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("AXON Ollama Integration Test")
    print("=" * 60)
    
    # Test 1: Connection
    if not test_ollama_connection():
        print("\n[FAILED] Ollama is not running or not accessible")
        print("[INFO] Start Ollama with: ollama serve")
        return False
    
    # Test 2: Model availability
    if not test_model_availability():
        print("\n[FAILED] Required model is not available")
        return False
    
    # Test 3: Vision capabilities
    if not test_ollama_vision():
        print("\n[FAILED] Vision test failed")
        return False
    
    # Test 4: LLM module integration
    if not test_ollama_with_llm_module():
        print("\n[FAILED] LLM module integration test failed")
        return False
    
    print("\n" + "=" * 60)
    print("[SUCCESS] All tests passed!")
    print("=" * 60)
    print("\n[INFO] Ollama is ready to use with AXON")
    print("[INFO] Run 'python main.py' to start AXON with Ollama")
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

# Made with Bob
