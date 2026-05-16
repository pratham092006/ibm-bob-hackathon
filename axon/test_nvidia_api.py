"""Test script to verify NVIDIA API integration."""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.llm import call_llm, get_current_provider, get_model_display_name
from PIL import Image
import io

def test_nvidia_integration():
    """Test NVIDIA API integration with a simple screenshot."""
    
    print("=" * 60)
    print("NVIDIA API Integration Test")
    print("=" * 60)
    
    # Check current provider
    provider = get_current_provider()
    model = get_model_display_name()
    
    print(f"\n[OK] Current Provider: {provider.upper()}")
    print(f"[OK] Current Model: {model}")
    
    if provider != "nvidia":
        print("\n[WARNING] Current provider is not NVIDIA")
        print("  Run: python switch_llm.py nvidia")
        return False
    
    # Create a simple test image (blank white image)
    print("\n[OK] Creating test image...")
    img = Image.new('RGB', (800, 600), color='white')
    
    # Convert to bytes
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='JPEG', quality=85)
    img_bytes = img_bytes.getvalue()
    
    print("[OK] Test image created (800x600)")
    
    # Test API call
    print("\n[OK] Testing NVIDIA API call...")
    print("  (This may take 10-30 seconds...)")
    
    try:
        result = call_llm(
            screen_image=img_bytes,
            task_description="What do you see in this image?",
            conversation_history=[]
        )
        
        print("\n[OK] API call successful!")
        print(f"  Response action: {result.get('action', 'N/A')}")
        print(f"  Response reasoning: {result.get('reasoning', 'N/A')[:100]}...")
        
        print("\n" + "=" * 60)
        print("[SUCCESS] NVIDIA API Integration Test PASSED")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\n[ERROR] API call failed: {e}")
        print("\n" + "=" * 60)
        print("[FAILED] NVIDIA API Integration Test FAILED")
        print("=" * 60)
        print("\nTroubleshooting:")
        print("1. Check your NVIDIA_API_KEY in .env")
        print("2. Verify the model name is correct")
        print("3. Check your internet connection")
        print("4. Visit https://build.nvidia.com/ to verify your API key")
        return False

if __name__ == "__main__":
    success = test_nvidia_integration()
    sys.exit(0 if success else 1)

# Made with Bob
