"""Shared configuration and state for AXON."""
import queue
import threading

# Shared state between all modules
status_queue = queue.Queue()  # Dev 1 puts status updates, Dev 3 gets for UI
kill_event = threading.Event()  # Dev 2 sets to halt, Dev 1 checks in loop

# API Configuration
ANTHROPIC_API_KEY = ""  # TODO: Add your Anthropic API key here

# Frame capture settings
FRAME_WIDTH = 1280
FRAME_HEIGHT = 720
JPEG_QUALITY = 85

# Timing
MAX_LOOP_DELAY = 0.1  # seconds between loop iterations
API_TIMEOUT = 10  # seconds

# Made with Bob
