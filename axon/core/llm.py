"""LLM integration using Google Gemini API with EasyOCR for grounded vision.

Complete rewrite with new architecture:
- Uses new Google GenAI SDK (google.genai)
- EasyOCR for text anchor extraction (grounded vision)
- Gemini 2.0 Flash / 1.5 Pro with structured outputs
- Robust error handling and type hints
"""

import json
import os
import tempfile
import time
from typing import Dict, Any, List, Optional, Union, Tuple
from PIL import Image
import io
import easyocr
from google import genai
from google.genai import types

# Import configuration - use relative imports
from ..config import GEMINI_API_KEY, FRAME_WIDTH, FRAME_HEIGHT, USE_GPU, OCR_CACHE_DURATION, GEMINI_MODELS, CURRENT_MODEL
from .capture import get_screen_dimensions

# Initialize EasyOCR reader globally (expensive operation, do once)
print("[LLM] Initializing EasyOCR reader...")
_easyocr_reader: Optional[easyocr.Reader] = None

# OCR caching to avoid re-running on every frame
_ocr_cache: List[Dict[str, Any]] = []
_last_ocr_time: float = 0

def _get_easyocr_reader() -> easyocr.Reader:
    """Get or initialize the global EasyOCR reader.
    
    Uses GPU setting from config.py
        
    Returns:
        easyocr.Reader: Initialized reader instance
    """
    global _easyocr_reader
    if _easyocr_reader is None:
        _easyocr_reader = easyocr.Reader(['en'], gpu=USE_GPU)
        print(f"[LLM] EasyOCR reader initialized (GPU: {USE_GPU})")
    return _easyocr_reader


# Initialize Google GenAI client
print("[LLM] Initializing Google GenAI client...")
_genai_client = genai.Client(api_key=GEMINI_API_KEY)
print("[LLM] Google GenAI client initialized")

def get_screen_resolution() -> Tuple[int, int]:
    """Get the actual screen resolution for coordinate scaling.
    
    Returns:
        Tuple[int, int]: (width, height) of the primary monitor
    """
    try:
        return get_screen_dimensions()
    except Exception:
        # Fallback: try pyautogui
        try:
            import pyautogui
            return pyautogui.size()
        except Exception:
            return (1920, 1080)  # Default fallback



def get_screen_elements(image_path: str, native_width: Optional[int] = None, native_height: Optional[int] = None, confidence_threshold: float = 0.4) -> List[Dict[str, Any]]:
    """Extract text anchors from screen capture using EasyOCR with caching.
    
    This provides grounded vision - the LLM gets actual text locations
    instead of guessing where UI elements are.
    
    CRITICAL: OCR runs on downscaled image, but coordinates are scaled
    to native screen resolution immediately for accurate clicking.
    
    Caching: OCR results are cached for OCR_CACHE_DURATION seconds to improve speed.
    
    Args:
        image_path: Path to screen capture image
        native_width: Native screen width (for coordinate scaling)
        native_height: Native screen height (for coordinate scaling)
        confidence_threshold: Minimum confidence for text detection (0.0-1.0)
        
    Returns:
        List of dictionaries with format:
        [
            {"text": "Chrome", "center_coordinate": [100, 920]},  # In native resolution
            {"text": "File", "center_coordinate": [50, 30]},
            ...
        ]
    """
    global _last_ocr_time, _ocr_cache
    
    try:
        # Check if we can use cached OCR results
        current_time = time.time()
        if current_time - _last_ocr_time < OCR_CACHE_DURATION and _ocr_cache:
            print(f"[LLM] Using cached OCR results ({len(_ocr_cache)} elements)")
            return _ocr_cache
        
        # Run fresh OCR
        reader = _get_easyocr_reader()
        
        # Get native screen resolution if not provided
        if native_width is None or native_height is None:
            native_width, native_height = get_screen_resolution()
        
        # Load image to get its dimensions (downscaled size)
        from PIL import Image
        img = Image.open(image_path)
        img_width, img_height = img.size
        
        # Calculate scale factors from downscaled to native
        scale_x = native_width / img_width
        scale_y = native_height / img_height
        
        print(f"[LLM] OCR scaling: image({img_width}x{img_height}) -> native({native_width}x{native_height})")
        print(f"[LLM] Scale factors: x={scale_x:.2f}, y={scale_y:.2f}")
        
        # Run OCR on the downscaled image
        results = reader.readtext(image_path)
        
        # Process results and extract text anchors with scaled coordinates
        text_anchors = []
        
        for detection in results:
            bbox, text, confidence = detection
            
            # Filter low-confidence detections (cast to float for type safety)
            if float(confidence) < confidence_threshold:
                continue
            
            # Calculate center coordinate from bounding box (in downscaled space)
            # bbox format: [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
            # (top_left, top_right, bottom_right, bottom_left)
            x_coords = [float(point[0]) for point in bbox]
            y_coords = [float(point[1]) for point in bbox]
            
            center_x = sum(x_coords) / len(x_coords)
            center_y = sum(y_coords) / len(y_coords)
            
            # Scale coordinates to native resolution
            native_x = int(center_x * scale_x)
            native_y = int(center_y * scale_y)
            
            text_anchors.append({
                "text": text,
                "center_coordinate": [native_x, native_y]
            })
        
        # Update cache
        _ocr_cache = text_anchors
        _last_ocr_time = current_time
        
        print(f"[LLM] Extracted {len(text_anchors)} text anchors (coordinates in native resolution)")
        return text_anchors
        
    except Exception as e:
        print(f"[LLM] ERROR in get_screen_elements: {e}")
        import traceback
        traceback.print_exc()
        return []


def _get_system_instruction(text_anchors: List[Dict[str, Any]]) -> str:
    """Build system instruction for Gemini with text anchor context.
    
    Args:
        text_anchors: List of detected text elements with coordinates
        
    Returns:
        str: System instruction for the LLM
    """
    # Get native screen resolution for accurate coordinates
    screen_w, screen_h = get_screen_resolution()
    
    # Format text anchors for the prompt
    anchors_text = ""
    if text_anchors:
        anchors_text = "\n\n**Detected Text Elements (MOST RELIABLE - use these coordinates):**\n"
        for anchor in text_anchors[:50]:  # Limit to first 50 to avoid token overflow
            text = anchor["text"]
            coord = anchor["center_coordinate"]
            anchors_text += f'- "{text}" at [{coord[0]}, {coord[1]}]\n'
    else:
        anchors_text = "\n\n**Note:** No text elements detected on screen. Use Windows Search (Win key + type) to open applications."
    
    return f"""You are an AI agent controlling a Windows desktop to accomplish user tasks.

**CRITICAL: How to Use Text Anchors**
Text anchors are the MOST RELIABLE way to interact with UI elements. ALWAYS prefer them over visual estimation.

**Examples of Correct Usage:**
- Task: "Open Chrome"
  - If you see text anchor: "Chrome" at [100, 920]
  - Response: {{"action": "left_click", "coordinate": [100, 920], "reasoning": "Clicking Chrome text anchor on taskbar", "confidence": 0.95}}
  
- Task: "Click Start Menu"
  - If you see text anchor: "Start" at [30, 1050]
  - Response: {{"action": "left_click", "coordinate": [30, 1050], "reasoning": "Clicking Start text anchor", "confidence": 0.95}}

- Task: "Open Notepad"
  - If NO text anchor found for "Notepad":
  - Step 1: {{"action": "key", "text": "win", "reasoning": "Opening Windows Search to find Notepad", "confidence": 0.9}}
  - Step 2: {{"action": "type", "text": "notepad", "reasoning": "Typing app name in search", "confidence": 0.95}}
  - Step 3: {{"action": "key", "text": "enter", "reasoning": "Launching Notepad from search results", "confidence": 0.95}}

**Strategy for Opening Applications:**
1. ALWAYS use open_app action for opening applications: {{"action": "open_app", "text": "chrome"}}
2. This is a single atomic operation that is FASTER and MORE RELIABLE than:
   - Clicking taskbar icons (which may not be visible)
   - Using separate key/type/enter actions (which is slow)
3. DO NOT break this into separate actions - open_app handles everything atomically
4. Examples:
   - Open Chrome: {{"action": "open_app", "text": "chrome"}}
   - Open Notepad: {{"action": "open_app", "text": "notepad"}}
   - Open Calculator: {{"action": "open_app", "text": "calculator"}}

**NEVER:**
- Click random coordinates without a text anchor
- Click IDE elements when task is about opening applications
- Guess coordinates based on visual appearance alone
- Repeat the same failed action more than twice

**Screen Dimensions:** {screen_w}x{screen_h} (native resolution)
**Available Text Anchors:** (see below)

{anchors_text}

**Available Actions (respond with exact JSON schema):**

1. open_app: Open application using Windows Search (FASTEST & MOST RELIABLE)
   {{"action": "open_app", "text": "chrome", "reasoning": "opening Chrome browser", "confidence": 0.95}}
   This is a single atomic operation that:
   - Presses Windows key
   - Types the app name
   - Presses Enter
   - Waits for app to launch
   Use this for: "chrome", "notepad", "firefox", "calculator", "paint", etc.

2. mouse_move: Move cursor to coordinates
   {{"action": "mouse_move", "coordinate": [x, y], "reasoning": "why moving here", "confidence": 0.0-1.0}}

3. left_click: Left click at coordinates
   {{"action": "left_click", "coordinate": [x, y], "reasoning": "why clicking here", "confidence": 0.0-1.0}}

4. right_click: Right click at coordinates
   {{"action": "right_click", "coordinate": [x, y], "reasoning": "why right-clicking", "confidence": 0.0-1.0}}

5. type: Type text character by character
   {{"action": "type", "text": "string to type", "reasoning": "what I'm typing and why", "confidence": 0.0-1.0}}

6. key: Press key or key combination
   {{"action": "key", "text": "enter", "reasoning": "why pressing this key", "confidence": 0.0-1.0}}
   Examples: "enter", "tab", "escape", "ctrl+c", "ctrl+v", "alt+tab", "win"

7. scroll: Scroll at coordinates
   {{"action": "scroll", "coordinate": [x, y], "direction": "up", "amount": 3, "reasoning": "why scrolling", "confidence": 0.0-1.0}}
   - direction: "up" or "down"
   - amount: integer (number of scroll clicks)

8. done: Task completed successfully
   {{"action": "done", "reasoning": "task completed because...", "confidence": 1.0}}

**Response Format:**
Return ONLY a JSON object with required fields: action, reasoning, confidence, and action-specific fields.
Example: {{"action": "left_click", "coordinate": [100, 200], "reasoning": "Clicking Chrome icon based on text anchor", "confidence": 0.95}}
"""


def call_llm(
    screen_image: Union[bytes, str],
    task_description: str,
    conversation_history: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """Call Gemini 2.5 Flash to determine next action with structured outputs.
    
    This is the main function that:
    1. Extracts text anchors using EasyOCR
    2. Sends screenshot + context to Gemini
    3. Gets structured JSON response
    4. Returns action for executor
    
    Args:
        screen_image: Either bytes (JPEG image data) or path to image file
        task_description: User's task/goal description
        conversation_history: List of previous actions to prevent loops
        
    Returns:
        Dict with action information:
        {
            "action": "left_click",
            "coordinate": [x, y],
            "text": "...",  # for type/key actions
            "direction": "up",  # for scroll
            "amount": 3  # for scroll
        }
        
        On error, returns safe fallback:
        {"action": "mouse_move", "coordinate": [0, 0]}
    """
    temp_file = None
    try:
        # Handle both bytes and file path inputs
        if isinstance(screen_image, bytes):
            # Save bytes to temporary file for EasyOCR
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
            temp_file.write(screen_image)
            temp_file.close()
            frame_path = temp_file.name
            image_bytes = screen_image
        else:
            # It's a file path
            frame_path = screen_image
            with open(frame_path, 'rb') as f:
                image_bytes = f.read()
        
        # Step 1: Extract text anchors from screen
        print(f"[LLM] Extracting text anchors from screen...")
        text_anchors = get_screen_elements(frame_path)
        
        # Step 2: Build system instruction with text anchors
        system_instruction = _get_system_instruction(text_anchors)
        
        # Step 3: Build user prompt with context
        user_prompt = f"**Goal:** {task_description}\n\n"
        
        # Add conversation history with outcome tracking to prevent infinite loops
        if conversation_history and len(conversation_history) > 0:
            user_prompt += "**Previous Actions:**\n"
            for i, action in enumerate(conversation_history[-5:], 1):  # Last 5 actions
                action_type = action.get('action', 'unknown')
                outcome = action.get('outcome', 'unknown')
                coord = action.get('coordinate', [])
                coord_str = f" at {coord}" if coord else ""
                user_prompt += f"{i}. {action_type}{coord_str} - Result: {outcome}\n"
            user_prompt += "\n"
        
        user_prompt += """**IMPORTANT - Avoid Getting Stuck:**
- If you've clicked the same area 3+ times without progress, try a different approach
- If the task is 'Open Chrome' but you're clicking IDE elements, STOP and click Start Menu instead
- To open applications: Click Start Menu (bottom-left corner), type app name, press Enter
- Each action should move you closer to the goal
- If unsure, use mouse_move to explore before clicking
- Don't repeat failed actions - analyze what went wrong and try something different

"""
        
        user_prompt += "Analyze the screenshot and decide the next action. Respond with ONLY valid JSON."
        
        # Step 4: Create image part for Gemini
        image_part = types.Part.from_bytes(
            data=image_bytes,
            mime_type="image/jpeg"
        )
        
        # Step 5: Call Gemini with structured outputs
        print("[LLM] Calling Gemini API...")
        
        response = _genai_client.models.generate_content(
            model=GEMINI_MODELS.get(CURRENT_MODEL, "gemini-2.0-flash-exp"),
            contents=[
                types.Content(
                    role="user",
                    parts=[
                        types.Part.from_text(text=system_instruction),
                        types.Part.from_text(text=user_prompt),
                        image_part
                    ]
                )
            ],
            config=types.GenerateContentConfig(
                temperature=0.1,
                response_mime_type="application/json",  # Force JSON output
                max_output_tokens=1024
            )
        )
        
        # Step 6: Parse response
        response_text = response.text.strip() if hasattr(response, 'text') and response.text else "{}"
        print(f"[LLM] Raw response: {response_text[:200]}")
        
        # Parse JSON response
        action_dict = json.loads(response_text)
        
        # Validate action field exists
        if "action" not in action_dict:
            print("[LLM] ERROR: Response missing 'action' field")
            return {"action": "mouse_move", "coordinate": [0, 0]}
        
        # Scale coordinates if present
        action_dict = normalize_and_scale_action(action_dict)
        
        print(f"[LLM] Action: {action_dict.get('action')}")
        if "coordinate" in action_dict:
            print(f"[LLM] Coordinate: {action_dict['coordinate']}")
        
        return action_dict
        
    except json.JSONDecodeError as e:
        print(f"[LLM] ERROR: Failed to parse JSON response: {e}")
        return {"action": "mouse_move", "coordinate": [0, 0]}
        
    except Exception as e:
        print(f"[LLM] ERROR in call_llm: {e}")
        import traceback
        traceback.print_exc()
        return {"action": "mouse_move", "coordinate": [0, 0]}
    
    finally:
        # Clean up temporary file if created
        if temp_file is not None and hasattr(temp_file, 'name') and os.path.exists(temp_file.name):
            try:
                os.unlink(temp_file.name)
            except:
                pass


def scale_coordinates(x: int, y: int, from_width: int = FRAME_WIDTH, from_height: int = FRAME_HEIGHT) -> Tuple[int, int]:
    """Scale coordinates from image space to real screen space.
    
    The LLM sees a resized image (FRAME_WIDTH x FRAME_HEIGHT) but we need 
    to click on the actual screen which may be a different resolution.
    
    Args:
        x: X coordinate in image space
        y: Y coordinate in image space
        from_width: Width of the image the LLM analyzed
        from_height: Height of the image the LLM analyzed
        
    Returns:
        tuple: (scaled_x, scaled_y) in real screen coordinates
    """
    screen_w, screen_h = get_screen_resolution()
    
    # Scale proportionally
    scaled_x = int(x * screen_w / from_width)
    scaled_y = int(y * screen_h / from_height)
    
    # Clamp to screen bounds
    scaled_x = max(0, min(scaled_x, screen_w - 1))
    scaled_y = max(0, min(scaled_y, screen_h - 1))
    
    return scaled_x, scaled_y


def normalize_and_scale_action(action_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize coordinate format and scale to screen resolution.
    
    Handles coordinate scaling from image space to screen space for actions
    that require coordinates.
    
    Args:
        action_dict: Raw parsed action from LLM
        
    Returns:
        dict: Action with normalized and scaled coordinates
    """
    action_type = action_dict.get('action', '')
    
    # Actions that need coordinates
    coordinate_actions = ['click', 'left_click', 'right_click', 'double_click', 
                          'mouse_move', 'scroll', 'middle_click']
    
    if action_type not in coordinate_actions:
        return action_dict
    
    # Extract coordinates
    coord = action_dict.get('coordinate', [])
    
    if not coord or len(coord) != 2:
        print(f"[LLM] WARNING: No valid coordinates found for {action_type}")
        return action_dict
    
    # Scale coordinates from image space to screen space
    raw_x, raw_y = int(coord[0]), int(coord[1])
    scaled_x, scaled_y = scale_coordinates(raw_x, raw_y)
    
    print(f"[LLM] Coordinates: image({raw_x}, {raw_y}) -> screen({scaled_x}, {scaled_y})")
    
    # Update coordinate array
    action_dict['coordinate'] = [scaled_x, scaled_y]
    
    # Also set x/y for backward compatibility
    action_dict['x'] = scaled_x
    action_dict['y'] = scaled_y
    
    return action_dict


# Backward compatibility functions for existing code
def switch_model(model_name: str) -> bool:
    """Switch between Gemini models (for backward compatibility).
    
    Note: New architecture uses gemini-2.5-flash only.
    This function is kept for compatibility but doesn't change behavior.
    
    Args:
        model_name: "flash" or "pro"
    
    Returns:
        True (always succeeds)
    """
    _ = model_name  # Keep parameter for API compatibility
    print(f"[LLM] Model switch requested to {model_name} (using gemini-2.5-flash)")
    return True


def get_current_model() -> str:
    """Get the currently active model name (for backward compatibility).
    
    Returns:
        str: Always returns "flash"
    """
    return "flash"


def get_model_display_name() -> str:
    """Get the display name of the current model (for backward compatibility).
    
    Returns:
        str: Display name
    """
    return "Gemini 2.5 Flash"


# Made with Bob
