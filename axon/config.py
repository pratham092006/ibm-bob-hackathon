"""Shared configuration and state for AXON."""
import queue
import threading
import os
from typing import Dict
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Shared state between all modules
status_queue: queue.Queue = queue.Queue()  # Dev 1 puts status updates, tray icon consumes
ui_queue: queue.Queue = queue.Queue()  # Dedicated queue for overlay/reticle UI updates
task_queue: queue.Queue = queue.Queue()  # For submitting tasks to agent loop
kill_event: threading.Event = threading.Event()  # Dev 2 sets to halt, Dev 1 checks in loop

# Gemini Configuration - Load from environment variable
GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in environment. Please create a .env file with your API key.")

# Available models - user can switch between these
GEMINI_MODELS: Dict[str, str] = {
    "flash": "gemini-2.0-flash-exp",  # Faster, cheaper (latest Flash model)
    "pro": "gemini-1.5-pro-latest"     # More capable, slower (latest Pro model)
}

# Default model to use
CURRENT_MODEL: str = "flash"  # Change to "pro" for Gemini 2.5 Pro

# Frame capture settings
# Reduced from 1920x1080 to 1600x900 for better speed while maintaining quality
# Still much better than original 1280x720
FRAME_WIDTH = 1600
FRAME_HEIGHT = 900
JPEG_QUALITY = 85  # Reduced from 90 for faster encoding

# EasyOCR GPU settings
USE_GPU = True  # Set to False if you don't have CUDA/GPU support

# Debug settings
DEBUG_MODE = True  # Set to False to disable debug screenshot saving

# Speed optimization
FAST_MODE = True  # Skip OCR for simple tasks like "Open Chrome"
OCR_CACHE_DURATION = 2.0  # Cache OCR results for 2 seconds

# Timing
MAX_LOOP_DELAY = 0.5  # Reduced from 1.0 second for faster response
API_TIMEOUT = 30  # seconds (LLM with image analysis can take 5-10s)

# Made with Bob
