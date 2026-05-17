"""LLM integration supporting both Claude and Gemini with EasyOCR for grounded vision.

Complete rewrite with new architecture:
- Supports both Anthropic Claude and Google Gemini
- EasyOCR for text anchor extraction (grounded vision)
- Structured outputs with robust error handling
- Easy model switching via environment variables
"""

import json
import os
import tempfile
import time
import re
from typing import Dict, Any, List, Optional, Union
from PIL import Image
import io
import base64
import easyocr
import requests
from openai import OpenAI

# Import configuration
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import (
    LLM_PROVIDER,
    GEMINI_API_KEY,
    CLAUDE_API_KEY,
    CLAUDE_MODEL,
    OPENROUTER_API_KEY,
    OPENROUTER_MODEL,
    NVIDIA_API_KEY,
    NVIDIA_MODEL,
    OLLAMA_BASE_URL,
    OLLAMA_MODEL,
    FRAME_WIDTH,
    FRAME_HEIGHT,
    USE_GPU,
    OCR_CACHE_DURATION
)

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


# Initialize LLM clients based on provider
_genai_client = None
_claude_client = None
_openrouter_client = None
_nvidia_client = None

if LLM_PROVIDER == "gemini":
    from google import genai
    from google.genai import types
    print("[LLM] Initializing Google GenAI client...")
    _genai_client = genai.Client(api_key=GEMINI_API_KEY)
    print("[LLM] Google GenAI client initialized")
elif LLM_PROVIDER == "claude":
    try:
        import anthropic
        print("[LLM] Initializing Anthropic Claude client...")
        _claude_client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)
        print(f"[LLM] Claude client initialized (model: {CLAUDE_MODEL})")
    except ImportError:
        print("[LLM] ERROR: anthropic package not installed. Run: pip install anthropic")
        raise
elif LLM_PROVIDER == "openrouter":
    try:
        from openai import OpenAI
        print("[LLM] Initializing OpenRouter client...")
        _openrouter_client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=OPENROUTER_API_KEY
        )
        print(f"[LLM] OpenRouter client initialized (model: {OPENROUTER_MODEL})")
    except ImportError:
        print("[LLM] ERROR: openai package not installed. Run: pip install openai")
        raise
elif LLM_PROVIDER == "nvidia":
    try:
        print("[LLM] Initializing NVIDIA API client with OpenAI SDK...")
        _nvidia_client = OpenAI(
            base_url="https://integrate.api.nvidia.com/v1",
            api_key=NVIDIA_API_KEY
        )
        print(f"[LLM] NVIDIA client initialized (model: {NVIDIA_MODEL})")
    except ImportError:
        print("[LLM] ERROR: openai package not installed. Run: pip install openai")
        raise


def get_screen_elements(image_path: str, native_width: int = None, native_height: int = None, confidence_threshold: float = 0.4) -> List[Dict[str, Any]]:
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
            
            # Filter low-confidence detections
            if confidence < confidence_threshold:
                continue
            
            # Calculate center coordinate from bounding box (in downscaled space)
            # bbox format: [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
            # (top_left, top_right, bottom_right, bottom_left)
            x_coords = [point[0] for point in bbox]
            y_coords = [point[1] for point in bbox]
            
            center_x = sum(x_coords) / len(x_coords)
            center_y = sum(y_coords) / len(y_coords)
            
            # Scale coordinates to native resolution
            native_x = int(center_x * scale_x)
            native_y = int(center_y * scale_y)
            
            text_anchors.append({
                "text": text,
                "center_coordinate": [native_x, native_y],
                "coordinate_space": "native"  # Already in screen coordinates - do NOT scale again
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
    """Build tight system instruction optimized for small vision LLMs."""
    screen_w, screen_h = get_screen_resolution()

    # Format text anchors — already in native screen coords, ready to use directly
    if text_anchors:
        anchors_lines = "\n".join(
            f'  "{a["text"]}" -> [{a["center_coordinate"][0]}, {a["center_coordinate"][1]}]'
            for a in text_anchors[:50]
        )
        anchors_block = f"DETECTED TEXT ELEMENTS (native {screen_w}x{screen_h} coords — use EXACTLY as given):\n{anchors_lines}"
    else:
        anchors_block = "No text detected on screen. Use open_app to launch applications."

    return f"""You are an AI agent controlling a Windows {screen_w}x{screen_h} desktop. Return ONE JSON action per turn.

COORDINATE RULES (CRITICAL — read carefully):
- Text anchor coordinates below are ALREADY in native screen pixels ({screen_w}x{screen_h}).
- Copy them EXACTLY into your response. Do NOT multiply, scale, or modify them.
- If you invent coordinates (no text anchor found), stay within: x=0..{screen_w}, y=0..{screen_h}.

TASK RULES:
1. Check if app is already open before calling open_app. If you see its UI — skip open_app.
2. After open_app, wait — the next screenshot will show the new app state.
3. To interact with an element: use its text anchor coordinate.
4. To type a message: click the text INPUT FIELD first (bottom of chat), then use 'type'.
5. After typing: press Enter to SEND. Use: {{"action":"key","text":"enter","reasoning":"sending message","confidence":1.0}}
6. Return 'done' only AFTER the message is confirmed sent (Enter was pressed).
7. Never click the same spot more than twice. If stuck, try a different element.
8. Input fields are at the BOTTOM of chat windows, NOT in the message history area.
9. To print a document: use print_document action with the document name (e.g., "KheloParty_Full_Plan"). This will automatically open and print the document.

ACTIONS:
  open_app:      {{"action":"open_app","text":"discord","reasoning":"...","confidence":0.95}}
  left_click:    {{"action":"left_click","coordinate":[x,y],"reasoning":"...","confidence":0.9}}
  double_click:  {{"action":"double_click","coordinate":[x,y],"reasoning":"...","confidence":0.9}}
  right_click:   {{"action":"right_click","coordinate":[x,y],"reasoning":"...","confidence":0.8}}
  type:          {{"action":"type","text":"Hello","reasoning":"...","confidence":0.95}}
  key:           {{"action":"key","text":"enter","reasoning":"...","confidence":1.0}}
  mouse_move:    {{"action":"mouse_move","coordinate":[x,y],"reasoning":"...","confidence":0.8}}
  scroll:        {{"action":"scroll","coordinate":[x,y],"direction":"down","amount":3,"reasoning":"...","confidence":0.8}}
  print_document:{{"action":"print_document","text":"KheloParty_Full_Plan","reasoning":"printing document","confidence":0.95}}
  done:          {{"action":"done","reasoning":"task complete","confidence":1.0}}

{anchors_block}

IMPORTANT: Return ONLY valid JSON. No markdown. No extra text. Just the JSON object."""





def call_llm(
    screen_image: Union[bytes, str],
    task_description: str,
    conversation_history: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """Call LLM (Claude, Gemini, OpenRouter, or NVIDIA) to determine next action with structured outputs.
    
    This is the main function that:
    1. Extracts text anchors using EasyOCR
    2. Sends screenshot + context to LLM
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
    # Log which model is being used
    print(f"[LLM] Using provider: {LLM_PROVIDER.upper()}, model: {get_current_model()}")
    
    if LLM_PROVIDER == "claude":
        return _call_claude(screen_image, task_description, conversation_history)
    elif LLM_PROVIDER == "openrouter":
        return _call_openrouter(screen_image, task_description, conversation_history)
    elif LLM_PROVIDER == "nvidia":
        return _call_nvidia(screen_image, task_description, conversation_history)
    elif LLM_PROVIDER == "ollama":
        return _call_ollama(screen_image, task_description, conversation_history)
    else:
        return _call_gemini(screen_image, task_description, conversation_history)


def _call_claude(
    screen_image: Union[bytes, str],
    task_description: str,
    conversation_history: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """Call Claude API to determine next action."""
    temp_file = None
    try:
        # Handle both bytes and file path inputs
        if isinstance(screen_image, bytes):
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
            temp_file.write(screen_image)
            temp_file.close()
            frame_path = temp_file.name
            image_bytes = screen_image
        else:
            frame_path = screen_image
            with open(frame_path, 'rb') as f:
                image_bytes = f.read()
        
        # Extract text anchors
        print(f"[LLM] Extracting text anchors from screen...")
        text_anchors = get_screen_elements(frame_path)
        
        # Build system instruction
        system_instruction = _get_system_instruction(text_anchors)
        
        # Build user prompt
        user_prompt = f"**Goal:** {task_description}\n\n"
        
        if conversation_history and len(conversation_history) > 0:
            user_prompt += "**Previous Actions:**\n"
            for i, action in enumerate(conversation_history[-5:], 1):
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
        
        # Encode image to base64 for Claude
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        
        # Call Claude API
        print(f"[LLM] Calling Claude ({CLAUDE_MODEL})...")
        
        message = _claude_client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=1024,
            temperature=0.1,
            system=system_instruction,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/jpeg",
                                "data": image_base64
                            }
                        },
                        {
                            "type": "text",
                            "text": user_prompt
                        }
                    ]
                }
            ]
        )
        
        # Parse response
        response_text = message.content[0].text.strip()
        print(f"[LLM] Raw response: {response_text[:200]}")
        
        # Extract JSON from response (Claude might wrap it in markdown)
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()
        
        action_dict = json.loads(response_text)
        
        if "action" not in action_dict:
            print("[LLM] ERROR: Response missing 'action' field")
            return {"action": "mouse_move", "coordinate": [0, 0]}
        
        action_dict = normalize_and_scale_action(action_dict)
        
        print(f"[LLM] Action: {action_dict.get('action')}")
        if "coordinate" in action_dict:
            print(f"[LLM] Coordinate: {action_dict['coordinate']}")
        
        return action_dict
        
    except json.JSONDecodeError as e:
        print(f"[LLM] ERROR: Failed to parse JSON response: {e}")
        return {"action": "mouse_move", "coordinate": [0, 0]}
    except Exception as e:
        print(f"[LLM] ERROR in _call_claude: {e}")
        import traceback
        traceback.print_exc()
        return {"action": "mouse_move", "coordinate": [0, 0]}
    finally:
        if temp_file and os.path.exists(temp_file.name):
            try:
                os.unlink(temp_file.name)
            except:
                pass


def _call_openrouter(
    screen_image: Union[bytes, str],
    task_description: str,
    conversation_history: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """Call OpenRouter API to determine next action using OpenAI-compatible interface."""
    temp_file = None
    try:
        # Handle both bytes and file path inputs
        if isinstance(screen_image, bytes):
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
            temp_file.write(screen_image)
            temp_file.close()
            frame_path = temp_file.name
            image_bytes = screen_image
        else:
            frame_path = screen_image
            with open(frame_path, 'rb') as f:
                image_bytes = f.read()
        
        # Extract text anchors
        print(f"[LLM] Extracting text anchors from screen...")
        text_anchors = get_screen_elements(frame_path)
        
        # Build system instruction
        system_instruction = _get_system_instruction(text_anchors)
        
        # Build user prompt
        user_prompt = f"**Goal:** {task_description}\n\n"
        
        if conversation_history and len(conversation_history) > 0:
            user_prompt += "**Previous Actions:**\n"
            for i, action in enumerate(conversation_history[-5:], 1):
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
        
        # Encode image to base64 for OpenRouter
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        
        # Call OpenRouter API using OpenAI SDK
        print(f"[LLM] Calling OpenRouter ({OPENROUTER_MODEL})...")
        
        response = _openrouter_client.chat.completions.create(
            model=OPENROUTER_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": system_instruction
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": user_prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_base64}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=1024,
            temperature=0.1
        )
        
        # Parse response
        response_text = response.choices[0].message.content.strip()
        print(f"[LLM] Raw response: {response_text[:200]}")
        
        # Extract JSON from response (might be wrapped in markdown)
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()
        
        action_dict = json.loads(response_text)
        
        if "action" not in action_dict:
            print("[LLM] ERROR: Response missing 'action' field")
            return {"action": "mouse_move", "coordinate": [0, 0]}
        
        action_dict = normalize_and_scale_action(action_dict)
        
        print(f"[LLM] Action: {action_dict.get('action')}")
        if "coordinate" in action_dict:
            print(f"[LLM] Coordinate: {action_dict['coordinate']}")
        
        return action_dict
        
    except json.JSONDecodeError as e:
        print(f"[LLM] ERROR: Failed to parse JSON response: {e}")
        return {"action": "mouse_move", "coordinate": [0, 0]}
    except Exception as e:
        print(f"[LLM] ERROR in _call_openrouter: {e}")
        import traceback
        traceback.print_exc()
        return {"action": "mouse_move", "coordinate": [0, 0]}
    finally:
        if temp_file and os.path.exists(temp_file.name):
            try:
                os.unlink(temp_file.name)
            except:
                pass
        

def _call_nvidia(
    screen_image: Union[bytes, str],
    task_description: str,
    conversation_history: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """Call NVIDIA API using requests library for Meta Llama 3.2 90B Vision Instruct model."""
    
    temp_file = None
    try:
        # Handle both bytes and file path inputs
        if isinstance(screen_image, bytes):
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
            temp_file.write(screen_image)
            temp_file.close()
            frame_path = temp_file.name
            image_bytes = screen_image
        else:
            frame_path = screen_image
            with open(frame_path, 'rb') as f:
                image_bytes = f.read()
        
        # Extract text anchors
        print(f"[LLM] Extracting text anchors from screen...")
        text_anchors = get_screen_elements(frame_path)
        
        # Build system instruction
        system_instruction = _get_system_instruction(text_anchors)
        
        # Build user prompt
        user_prompt = f"**Goal:** {task_description}\n\n"
        
        if conversation_history and len(conversation_history) > 0:
            user_prompt += "**Previous Actions:**\n"
            for i, action in enumerate(conversation_history[-5:], 1):
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
        
        # Encode image to base64 for NVIDIA API
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        
        # Prepare messages with vision support
        # Combine system instruction and user prompt in a single user message with the image
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": system_instruction + "\n\n" + user_prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_base64}"
                        }
                    }
                ]
            }
        ]
        
        # Prepare request payload
        invoke_url = "https://integrate.api.nvidia.com/v1/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {NVIDIA_API_KEY}",
            "Accept": "text/event-stream",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": NVIDIA_MODEL,
            "messages": messages,
            "max_tokens": 512,
            "temperature": 1.00,
            "top_p": 1.00,
            "frequency_penalty": 0.00,
            "presence_penalty": 0.00,
            "stream": True
        }
        
        # Call NVIDIA API using requests library with streaming
        print(f"[LLM] Calling NVIDIA API ({NVIDIA_MODEL}) with requests library (streaming)...")
        
        response = requests.post(invoke_url, headers=headers, json=payload, stream=True)
        response.raise_for_status()
        
        # Collect streaming response (SSE format)
        response_text = ""
        for line in response.iter_lines():
            if line:
                line_str = line.decode('utf-8')
                # SSE format: lines starting with "data: " contain JSON chunks
                if line_str.startswith('data: '):
                    data_str = line_str[6:]  # Remove "data: " prefix
                    
                    # Check for end of stream
                    if data_str.strip() == '[DONE]':
                        break
                    
                    try:
                        # Parse JSON chunk
                        chunk_data = json.loads(data_str)
                        
                        # Extract content from chunk
                        if 'choices' in chunk_data and len(chunk_data['choices']) > 0:
                            delta = chunk_data['choices'][0].get('delta', {})
                            content = delta.get('content', '')
                            if content:
                                response_text += content
                    except json.JSONDecodeError:
                        # Skip malformed chunks
                        continue
        
        print(f"[LLM] Streaming complete. Total response length: {len(response_text)}")
        print(f"[LLM] Raw response: {response_text[:200]}")
        
        # Extract JSON from response (might be wrapped in markdown or have extra text)
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()
        else:
            # Try to find JSON object in the response
            json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', response_text)
            if json_match:
                response_text = json_match.group(0)
        
        action_dict = json.loads(response_text)
        
        if "action" not in action_dict:
            print("[LLM] ERROR: Response missing 'action' field")
            return {"action": "mouse_move", "coordinate": [0, 0]}
        
        action_dict = normalize_and_scale_action(action_dict)
        
        print(f"[LLM] Action: {action_dict.get('action')}")
        if "coordinate" in action_dict:
            print(f"[LLM] Coordinate: {action_dict['coordinate']}")
        
        return action_dict
        
    except json.JSONDecodeError as e:
        print(f"[LLM] ERROR: Failed to parse JSON response: {e}")
        print(f"[LLM] Response text: {response_text}")
        return {"action": "mouse_move", "coordinate": [0, 0]}
    except Exception as e:
        print(f"[LLM] ERROR in _call_nvidia: {e}")
        import traceback
        traceback.print_exc()
        return {"action": "mouse_move", "coordinate": [0, 0]}
    finally:
        if temp_file and os.path.exists(temp_file.name):
            try:
                os.unlink(temp_file.name)
            except:
                pass


def _call_ollama(
    screen_image: Union[bytes, str],
    task_description: str,
    conversation_history: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """Call Ollama local model API for vision-language tasks.
    
    Uses Ollama's /api/generate endpoint with vision support.
    Ollama runs locally, so no API key needed and data stays private.
    """
    
    temp_file = None
    try:
        # Handle both bytes and file path inputs
        if isinstance(screen_image, bytes):
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
            temp_file.write(screen_image)
            temp_file.close()
            frame_path = temp_file.name
            image_bytes = screen_image
        else:
            frame_path = screen_image
            with open(frame_path, 'rb') as f:
                image_bytes = f.read()
        
        # Extract text anchors
        print(f"[LLM] Extracting text anchors from screen...")
        text_anchors = get_screen_elements(frame_path)
        
        # Build system instruction
        system_instruction = _get_system_instruction(text_anchors)
        
        # Build user prompt with step-by-step guidance (same as Gemini)
        user_prompt = f"**Goal:** {task_description}\n\n"
        
        if conversation_history and len(conversation_history) > 0:
            user_prompt += "**Previous Actions (Last 5):**\n"
            for i, action in enumerate(conversation_history[-5:], 1):
                action_type = action.get('action', 'unknown')
                outcome = action.get('outcome', 'unknown')
                reasoning = action.get('reasoning', '')
                coord = action.get('coordinate', [])
                text = action.get('text', '')
                
                # Build detailed action description
                action_desc = action_type
                if coord:
                    action_desc += f" at {coord}"
                if text:
                    action_desc += f" '{text}'"
                if reasoning:
                    action_desc += f" ({reasoning[:50]}...)" if len(reasoning) > 50 else f" ({reasoning})"
                
                user_prompt += f"{i}. {action_desc} - Result: {outcome}\n"
            user_prompt += "\n"
            
            # Add smart analysis of history with step detection
            recent_actions = [a.get('action') for a in conversation_history[-3:]]
            
            # Detect if app was just opened
            if 'open_app' in recent_actions:
                app_name = next((a.get('text', 'app') for a in conversation_history[-3:] if a.get('action') == 'open_app'), 'app')
                user_prompt += f"✅ **STEP 1 COMPLETE:** {app_name} has been opened.\n"
                user_prompt += f"📋 **NEXT STEP:** Look for the target element (user, chat, input field) and interact with it.\n\n"
            
            # Detect if user was clicked
            if any(a.get('action') in ['left_click', 'click'] for a in conversation_history[-2:]):
                last_click = next((a for a in reversed(conversation_history[-2:]) if a.get('action') in ['left_click', 'click']), None)
                if last_click:
                    reasoning = last_click.get('reasoning', '').lower()
                    if 'input' in reasoning or 'field' in reasoning or 'type' in reasoning or 'message' in reasoning:
                        user_prompt += f"✅ **STEP 2 COMPLETE:** Input field has been clicked.\n"
                        user_prompt += f"📋 **NEXT STEP:** Now TYPE the message using 'type' action.\n\n"
            
            # Detect repeated same action
            if len(set(recent_actions)) == 1 and recent_actions[0] == 'open_app':
                app_name = conversation_history[-1].get('text', 'app')
                user_prompt += f"⚠️ **NOTICE:** You've opened '{app_name}' multiple times. Check if it's ALREADY OPEN before trying again!\n\n"
            elif len(recent_actions) >= 2 and recent_actions[-1] == recent_actions[-2] == 'left_click':
                user_prompt += f"⚠️ **NOTICE:** You've clicked twice in a row. If you clicked the input field, NEXT action should be 'type' to enter the message!\n\n"
        
        user_prompt += """**IMPORTANT - Step-by-Step Execution:**
- STEP 1: Find target (user, chat) → Click on it if needed
- STEP 2: Find TEXT INPUT FIELD → Click on it (look for "Type a message" or input box at BOTTOM)
- STEP 3: TYPE message → Use 'type' action with the message text
- STEP 4: Send message → Press Enter with 'key' action

**CRITICAL - After Clicking Input Field:**
- If you just clicked on an input field, your NEXT action MUST be 'type'
- Don't click again - the field is already focused
- Use: {"action": "type", "text": "your message here", "reasoning": "typing the message", "confidence": 0.95}

**Finding Text Input:**
- Text input fields are usually at the BOTTOM of the chat window
- Look for text anchors: "Type a message", "Message", "Send a message"
- Input fields often have a light background or border
- DON'T click on chat messages - click on the INPUT BOX
- After clicking input field once, immediately TYPE (don't click again)

"""
        
        user_prompt += "Analyze the screenshot and decide the next action. Respond with ONLY valid JSON."
        
        # Encode image to base64 for Ollama API
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        
        # Prepare Ollama API request
        # Ollama uses /api/generate endpoint with streaming support
        url = f"{OLLAMA_BASE_URL}/api/generate"
        
        payload = {
            "model": OLLAMA_MODEL,
            "prompt": system_instruction + "\n\n" + user_prompt,
            "images": [image_base64],
            "stream": True,
            "options": {
                "temperature": 0.7,
                "num_predict": 512
            }
        }
        
        # Call Ollama API
        print(f"[LLM] Calling Ollama API ({OLLAMA_MODEL}) at {OLLAMA_BASE_URL}...")
        
        response = requests.post(url, json=payload, stream=True, timeout=60)
        response.raise_for_status()
        
        # Collect streaming response
        response_text = ""
        for line in response.iter_lines():
            if line:
                try:
                    chunk_data = json.loads(line)
                    
                    # Ollama streams with "response" field containing text chunks
                    if "response" in chunk_data:
                        response_text += chunk_data["response"]
                    
                    # Check if generation is done
                    if chunk_data.get("done", False):
                        break
                        
                except json.JSONDecodeError:
                    # Skip malformed chunks
                    continue
        
        print(f"[LLM] Streaming complete. Total response length: {len(response_text)}")
        print(f"[LLM] Raw response: {response_text[:200]}")
        
        # Extract JSON from response (might be wrapped in markdown or have extra text)
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()
        else:
            # Try to find JSON object in the response
            json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', response_text)
            if json_match:
                response_text = json_match.group(0)
        
        action_dict = json.loads(response_text)
        
        if "action" not in action_dict:
            print("[LLM] ERROR: Response missing 'action' field")
            return {"action": "mouse_move", "coordinate": [0, 0]}
        
        action_dict = normalize_and_scale_action(action_dict)
        
        print(f"[LLM] Action: {action_dict.get('action')}")
        if "coordinate" in action_dict:
            print(f"[LLM] Coordinate: {action_dict['coordinate']}")
        
        return action_dict
        
    except json.JSONDecodeError as e:
        print(f"[LLM] ERROR: Failed to parse JSON response: {e}")
        print(f"[LLM] Response text: {response_text}")
        return {"action": "mouse_move", "coordinate": [0, 0]}
    except requests.exceptions.ConnectionError as e:
        print(f"[LLM] ERROR: Cannot connect to Ollama at {OLLAMA_BASE_URL}")
        print(f"[LLM] Make sure Ollama is running. Start it with: ollama serve")
        print(f"[LLM] Error details: {e}")
        return {"action": "mouse_move", "coordinate": [0, 0]}
    except Exception as e:
        print(f"[LLM] ERROR in _call_ollama: {e}")
        import traceback
        traceback.print_exc()
        return {"action": "mouse_move", "coordinate": [0, 0]}
    finally:
        if temp_file and os.path.exists(temp_file.name):
            try:
                os.unlink(temp_file.name)
            except:
                pass

            try:
                os.unlink(temp_file.name)
            except:
                pass


def _call_gemini(
    screen_image: Union[bytes, str],
    task_description: str,
    conversation_history: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """Call Gemini API to determine next action."""
    from google import genai
    from google.genai import types
    
    temp_file = None
    try:
        # Handle both bytes and file path inputs
        if isinstance(screen_image, bytes):
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
            temp_file.write(screen_image)
            temp_file.close()
            frame_path = temp_file.name
            image_bytes = screen_image
        else:
            frame_path = screen_image
            with open(frame_path, 'rb') as f:
                image_bytes = f.read()
        
        # Extract text anchors
        print(f"[LLM] Extracting text anchors from screen...")
        text_anchors = get_screen_elements(frame_path)
        
        # Build system instruction
        system_instruction = _get_system_instruction(text_anchors)
        
        # Build user prompt with step-by-step guidance
        user_prompt = f"**Goal:** {task_description}\n\n"
        
        if conversation_history and len(conversation_history) > 0:
            user_prompt += "**Previous Actions (Last 5):**\n"
            for i, action in enumerate(conversation_history[-5:], 1):
                action_type = action.get('action', 'unknown')
                outcome = action.get('outcome', 'unknown')
                reasoning = action.get('reasoning', '')
                coord = action.get('coordinate', [])
                text = action.get('text', '')
                
                # Build detailed action description
                action_desc = action_type
                if coord:
                    action_desc += f" at {coord}"
                if text:
                    action_desc += f" '{text}'"
                if reasoning:
                    action_desc += f" ({reasoning[:50]}...)" if len(reasoning) > 50 else f" ({reasoning})"
                
                user_prompt += f"{i}. {action_desc} - Result: {outcome}\n"
            user_prompt += "\n"
            
            # Add smart analysis of history with step detection
            recent_actions = [a.get('action') for a in conversation_history[-3:]]
            
            # Detect if app was just opened
            if 'open_app' in recent_actions:
                app_name = next((a.get('text', 'app') for a in conversation_history[-3:] if a.get('action') == 'open_app'), 'app')
                user_prompt += f"✅ **STEP 1 COMPLETE:** {app_name} has been opened.\n"
                user_prompt += f"📋 **NEXT STEP:** Look for the target element (user, chat, input field) and interact with it.\n\n"
            
            # Detect if user was clicked
            if any(a.get('action') in ['left_click', 'click'] for a in conversation_history[-2:]):
                last_click = next((a for a in reversed(conversation_history[-2:]) if a.get('action') in ['left_click', 'click']), None)
                if last_click:
                    reasoning = last_click.get('reasoning', '').lower()
                    if 'user' in reasoning or 'chat' in reasoning or 'pratham' in reasoning:
                        user_prompt += f"✅ **STEP 2 COMPLETE:** Target user/chat has been clicked.\n"
                        user_prompt += f"📋 **NEXT STEP:** Find and click the TEXT INPUT FIELD (look for 'Type a message', 'Message', or input box).\n\n"
            
            # Detect repeated same action
            if len(set(recent_actions)) == 1 and recent_actions[0] == 'open_app':
                app_name = conversation_history[-1].get('text', 'app')
                user_prompt += f"⚠️ **NOTICE:** You've opened '{app_name}' multiple times. Check if it's ALREADY OPEN before trying again!\n\n"
            elif len(recent_actions) >= 2 and recent_actions[-1] == recent_actions[-2] == 'left_click':
                user_prompt += f"⚠️ **NOTICE:** You've clicked twice in a row. Make sure you're clicking the RIGHT element (text input field, not chat history).\n\n"
        
        user_prompt += """**IMPORTANT - Step-by-Step Execution:**
- STEP 1: Open app (if needed) → Check if app UI is visible
- STEP 2: Find target (user, chat) → Click on it to open chat
- STEP 3: Find TEXT INPUT FIELD → Look for "Type a message" or input box at BOTTOM of chat
- STEP 4: Click on input field → Wait for cursor to appear
- STEP 5: Type message → Use 'type' action
- STEP 6: Send message → Press Enter with 'key' action

**CRITICAL - Finding Text Input:**
- Text input fields are usually at the BOTTOM of the chat window
- Look for text anchors: "Type a message", "Message @username", "Send a message"
- Input fields often have a light background or border
- DON'T click on chat messages or user names - click on the INPUT BOX
- If you can't find text anchor, look for the bottom-most clickable area in the chat

**Avoid Getting Stuck:**
- Each action should progress to the NEXT step
- Don't repeat the same click if it didn't work - try a different location
- If you clicked on a user, NEXT click should be on the text input field
- If you're stuck, use mouse_move to explore the screen first

"""
        
        user_prompt += "Analyze the screenshot and decide the next action. Respond with ONLY valid JSON."
        
        # Create image part
        image_part = types.Part.from_bytes(
            data=image_bytes,
            mime_type="image/jpeg"
        )
        
        # Call Gemini
        print("[LLM] Calling Gemini 2.5 Flash...")
        
        response = _genai_client.models.generate_content(
            model="gemini-2.5-flash",
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
                response_mime_type="application/json",
                max_output_tokens=1024
            )
        )
        
        # Parse response
        response_text = response.text.strip() if response.text else "{}"
        print(f"[LLM] Raw response: {response_text[:200]}")
        
        action_dict = json.loads(response_text)
        
        if "action" not in action_dict:
            print("[LLM] ERROR: Response missing 'action' field")
            return {"action": "mouse_move", "coordinate": [0, 0]}
        
        action_dict = normalize_and_scale_action(action_dict)
        
        print(f"[LLM] Action: {action_dict.get('action')}")
        if "coordinate" in action_dict:
            print(f"[LLM] Coordinate: {action_dict['coordinate']}")
        
        return action_dict
        
    except json.JSONDecodeError as e:
        print(f"[LLM] ERROR: Failed to parse JSON response: {e}")
        return {"action": "mouse_move", "coordinate": [0, 0]}
    except Exception as e:
        print(f"[LLM] ERROR in _call_gemini: {e}")
        import traceback
        traceback.print_exc()
        return {"action": "mouse_move", "coordinate": [0, 0]}
    finally:
        if temp_file and os.path.exists(temp_file.name):
            try:
                os.unlink(temp_file.name)
            except:
                pass


def get_screen_resolution() -> tuple:
    """Get the actual screen resolution for coordinate scaling.
    
    Returns:
        tuple: (width, height) of the primary monitor
    """
    try:
        from core.capture import get_screen_dimensions
        return get_screen_dimensions()
    except Exception:
        # Fallback: try pyautogui
        try:
            import pyautogui
            return pyautogui.size()
        except Exception:
            return (1920, 1080)  # Default fallback


def scale_coordinates(x: int, y: int, from_width: int = FRAME_WIDTH, from_height: int = FRAME_HEIGHT) -> tuple:
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
    
    Provider-aware coordinate handling:
    
    - Ollama / Claude / OpenRouter / NVIDIA:
        The system prompt explicitly tells these models that text anchor coords
        are already in native screen space and to output native-space coords.
        So we NEVER scale — just clamp to screen bounds.
    
    - Gemini:
        Gemini sees the resized image (FRAME_WIDTH x FRAME_HEIGHT) and naturally
        outputs image-space coordinates. We scale those to native.
    
    Args:
        action_dict: Raw parsed action from LLM
        
    Returns:
        dict: Action with normalized and clamped/scaled coordinates
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
    
    raw_x, raw_y = int(coord[0]), int(coord[1])
    screen_w, screen_h = get_screen_resolution()
    
    # Provider-aware: Gemini uses image-space coords; all others use native-space.
    if LLM_PROVIDER == "gemini":
        # Scale from image space (FRAME_WIDTH x FRAME_HEIGHT) to screen space
        scaled_x, scaled_y = scale_coordinates(raw_x, raw_y)
        print(f"[LLM] Gemini coords scaled: image({raw_x}, {raw_y}) -> screen({scaled_x}, {scaled_y})")
    else:
        # Ollama / Claude / OpenRouter / NVIDIA: model outputs native-space coords.
        # Just clamp to screen bounds (handles out-of-bounds values safely).
        scaled_x = max(0, min(raw_x, screen_w - 1))
        scaled_y = max(0, min(raw_y, screen_h - 1))
        print(f"[LLM] Native coords (clamped): ({raw_x}, {raw_y}) -> ({scaled_x}, {scaled_y})")
    
    # Update coordinate array
    action_dict['coordinate'] = [scaled_x, scaled_y]
    
    # Also set x/y for backward compatibility
    action_dict['x'] = scaled_x
    action_dict['y'] = scaled_y
    
    return action_dict


# Model switching and management functions
def switch_provider(provider: str) -> bool:
    """Switch between LLM providers (Claude, Gemini, OpenRouter, NVIDIA, or Ollama).
    
    Args:
        provider: "claude", "gemini", "openrouter", "nvidia", or "ollama"
    
    Returns:
        bool: True if switch successful, False otherwise
    """
    global LLM_PROVIDER, _genai_client, _claude_client, _openrouter_client, _nvidia_client
    
    provider = provider.lower()
    if provider not in ["claude", "gemini", "openrouter", "nvidia", "ollama"]:
        print(f"[LLM] ERROR: Invalid provider '{provider}'. Use 'claude', 'gemini', 'openrouter', 'nvidia', or 'ollama'")
        return False
    
    try:
        if provider == "claude" and not _claude_client:
            import anthropic
            _claude_client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)
            print(f"[LLM] Claude client initialized (model: {CLAUDE_MODEL})")
        elif provider == "gemini" and not _genai_client:
            from google import genai
            _genai_client = genai.Client(api_key=GEMINI_API_KEY)
            print("[LLM] Google GenAI client initialized")
        elif provider == "openrouter" and not _openrouter_client:
            from openai import OpenAI
            _openrouter_client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=OPENROUTER_API_KEY
            )
            print(f"[LLM] OpenRouter client initialized (model: {OPENROUTER_MODEL})")
        elif provider == "nvidia" and not _nvidia_client:
            import requests
            _nvidia_client = True
            print(f"[LLM] NVIDIA client initialized (model: {NVIDIA_MODEL})")
        elif provider == "ollama":
            # Ollama is local, no client initialization needed
            print(f"[LLM] Ollama local model initialized (model: {OLLAMA_MODEL} at {OLLAMA_BASE_URL})")
        
        # Update config
        import config
        config.LLM_PROVIDER = provider
        
        print(f"[LLM] ✓ Switched to {provider.upper()}")
        return True
        
    except Exception as e:
        print(f"[LLM] ERROR: Failed to switch to {provider}: {e}")
        return False


def get_current_provider() -> str:
    """Get the currently active LLM provider.
    
    Returns:
        str: "claude" or "gemini"
    """
    return LLM_PROVIDER


def get_current_model() -> str:
    """Get the currently active model name.
    
    Returns:
        str: Model identifier
    """
    if LLM_PROVIDER == "claude":
        return CLAUDE_MODEL
    elif LLM_PROVIDER == "openrouter":
        return OPENROUTER_MODEL
    elif LLM_PROVIDER == "nvidia":
        return NVIDIA_MODEL
    elif LLM_PROVIDER == "ollama":
        return OLLAMA_MODEL
    else:
        return "gemini-2.5-flash"


def get_model_display_name() -> str:
    """Get the display name of the current model.
    
    Returns:
        str: Human-readable model name
    """
    if LLM_PROVIDER == "claude":
        model_names = {
            "claude-3-5-sonnet-20241022": "Claude 3.5 Sonnet",
            "claude-3-5-haiku-20241022": "Claude 3.5 Haiku",
            "claude-3-opus-20240229": "Claude 3 Opus"
        }
        return model_names.get(CLAUDE_MODEL, CLAUDE_MODEL)
    elif LLM_PROVIDER == "openrouter":
        return f"OpenRouter: {OPENROUTER_MODEL}"
    elif LLM_PROVIDER == "nvidia":
        return f"NVIDIA: {NVIDIA_MODEL}"
    elif LLM_PROVIDER == "ollama":
        return f"Ollama Local: {OLLAMA_MODEL}"
    else:
        return "Gemini 2.5 Flash"


# Backward compatibility
def switch_model(model_name: str) -> bool:
    """Legacy function for switching models.
    
    Args:
        model_name: Model identifier
    
    Returns:
        bool: True if successful
    """
    print(f"[LLM] Legacy switch_model called with {model_name}")
    return True


# Made with Bob
