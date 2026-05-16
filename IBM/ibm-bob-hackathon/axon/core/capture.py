"""Screen capture module using mss.

Dev 1 (Joshua) - Vision & Brain
TODO: Implement screen capture functionality
- Use mss library to grab frames from the screen
- Resize frames to FRAME_WIDTH x FRAME_HEIGHT from config.py
- Compress frames to JPEG with JPEG_QUALITY from config.py
- Return compressed frame data for LLM processing
- Handle multi-monitor setups (capture primary monitor)
- Optimize for performance (target ~10 FPS capture rate)
"""

import mss
from PIL import Image
import io
from config import FRAME_WIDTH, FRAME_HEIGHT, JPEG_QUALITY


def capture_screen():
    """Capture and compress the current screen.
    
    Returns:
        bytes: JPEG-compressed screen capture
    """
    try:
        # Create screen capture object
        with mss.mss() as sct:
            # Grab the primary monitor (monitor 1)
            monitor = sct.monitors[1]
            screenshot = sct.grab(monitor)
            
            # Convert to PIL Image
            img = Image.frombytes('RGB', screenshot.size, screenshot.rgb)
            
            # Resize to configured dimensions
            img = img.resize((FRAME_WIDTH, FRAME_HEIGHT), Image.Resampling.LANCZOS)
            
            # Compress to JPEG
            buffer = io.BytesIO()
            img.save(buffer, format='JPEG', quality=JPEG_QUALITY)
            
            # Return bytes
            return buffer.getvalue()
    except Exception as e:
        print(f"Error capturing screen: {e}")
        return None


def get_screen_dimensions():
    """Get the dimensions of the primary monitor.
    
    Returns:
        tuple: (width, height) of primary monitor
    """
    try:
        with mss.mss() as sct:
            monitor = sct.monitors[1]  # Primary monitor
            return (monitor['width'], monitor['height'])
    except Exception as e:
        print(f"Error getting screen dimensions: {e}")
        return (1920, 1080)  # Default fallback

# Made with Bob
