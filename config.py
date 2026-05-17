"""Shared configuration and state for AXON."""
import queue
import threading
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Shared state between all modules
status_queue = queue.Queue()  # Dev 1 puts status updates, tray icon consumes
ui_queue = queue.Queue()  # Dedicated queue for overlay/reticle UI updates
task_queue = queue.Queue()  # For submitting tasks to agent loop
kill_event = threading.Event()  # Dev 2 sets to halt, Dev 1 checks in loop

# LLM Provider Configuration
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openrouter").lower()  # "claude", "gemini", "openrouter", "nvidia", or "ollama"

# Gemini Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Claude Configuration
CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY", "")
CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-3-5-sonnet-20241022")

# OpenRouter Configuration
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "anthropic/claude-3.5-haiku")

# NVIDIA Configuration
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY", "")
NVIDIA_MODEL = os.getenv("NVIDIA_MODEL", "meta/llama-3.2-90b-vision-instruct")

# Ollama Configuration
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2-vision:11b")

# Validate API keys based on selected provider (skip validation for ollama - local model)
if LLM_PROVIDER == "claude" and not CLAUDE_API_KEY:
    raise ValueError("CLAUDE_API_KEY not found in environment. Please add it to your .env file.")
elif LLM_PROVIDER == "gemini" and not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in environment. Please add it to your .env file.")
elif LLM_PROVIDER == "openrouter" and not OPENROUTER_API_KEY:
    raise ValueError("OPENROUTER_API_KEY not found in environment. Please add it to your .env file.")
elif LLM_PROVIDER == "nvidia" and not NVIDIA_API_KEY:
    raise ValueError("NVIDIA_API_KEY not found in environment. Please add it to your .env file.")
elif LLM_PROVIDER == "ollama":
    # Ollama is local, no API key needed
    print(f"[Config] Using Ollama local model: {OLLAMA_MODEL} at {OLLAMA_BASE_URL}")

# Available models for each provider
GEMINI_MODELS = {
    "flash": "gemini-2.5-flash",  # Faster, cheaper (latest Flash model)
    "pro": "gemini-2.5-pro"        # More capable, slower (latest Pro model)
}

CLAUDE_MODELS = {
    "sonnet": "claude-3-5-sonnet-20241022",  # Best balance (recommended)
    "haiku": "claude-3-5-haiku-20241022",    # Fastest
    "opus": "claude-3-opus-20240229"         # Most capable
}

# Default model to use (for Gemini backward compatibility)
CURRENT_MODEL = "flash"  # Change to "pro" for Gemini 2.5 Pro

# Frame capture settings
# Capture at native screen resolution for best quality
# OCR will run on full resolution images for accurate text detection
FRAME_WIDTH = 1920
FRAME_HEIGHT = 1080
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
