"""Test script for NVIDIA Llama 3.1 Nemotron Nano VL 8B vision-language model."""

import os
import sys
import base64
from PIL import Image, ImageDraw, ImageFont
import io

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.llm import call_llm

def create_test_image():
    """Create a simple test image with text."""
    # Create a white image with some text
    img = Image.new('RGB', (800, 600), color='white')
    draw = ImageDraw.Draw(img)
    
    # Draw some text
    try:
        font = ImageFont.truetype("arial.ttf", 40)
    except:
        font = ImageFont.load_default()
    
    draw.text((50, 50), "Chrome Browser", fill='black', font=font)
    draw.text((50, 150), "File Explorer", fill='black', font=font)
    draw.text((50, 250), "Start Menu", fill='black', font=font)
    
    # Draw some rectangles to simulate UI elements
    draw.rectangle([40, 40, 300, 100], outline='blue', width=2)
    draw.rectangle([40, 140, 300, 200], outline='blue', width=2)
    draw.rectangle([40, 240, 300, 300], outline='blue', width=2)
    
    # Save to bytes
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='JPEG')
    img_bytes.seek(0)
    
    return img_bytes.getvalue()

def test_nvidia_vision():
    """Test the NVIDIA vision-language model."""
    print("=" * 60)
    print("Testing NVIDIA Llama 3.1 Nemotron Nano VL 8B")
    print("=" * 60)
    
    # Create test image
    print("\n[1] Creating test image...")
    image_bytes = create_test_image()
    print(f"    [OK] Test image created ({len(image_bytes)} bytes)")
    
    # Test with a simple task
    print("\n[2] Testing vision-language model...")
    task = "Click on Chrome Browser"
    print(f"    Task: {task}")
    
    try:
        result = call_llm(image_bytes, task)
        print(f"    [OK] Model response received")
        print(f"\n[3] Result:")
        print(f"    Action: {result.get('action')}")
        if 'coordinate' in result:
            print(f"    Coordinate: {result.get('coordinate')}")
        if 'reasoning' in result:
            print(f"    Reasoning: {result.get('reasoning')}")
        
        print("\n" + "=" * 60)
        print("[OK] Test completed successfully!")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_nvidia_vision()
    sys.exit(0 if success else 1)

# Made with Bob
