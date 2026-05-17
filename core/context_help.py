"""Context-aware help using LLM for selected text.

Provides AI-powered explanations and help for selected text.
"""

import sys
import os

# Add parent directory to path for imports
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
    OLLAMA_MODEL
)


def get_context_help(selected_text: str) -> str:
    """Get AI-powered context help for selected text.
    
    Args:
        selected_text: The text selected by the user
        
    Returns:
        str: AI-generated explanation/help text
    """
    print(f"[CONTEXT HELP] Getting help for: '{selected_text[:50]}...'")
    print(f"[CONTEXT HELP] Using provider: {LLM_PROVIDER}")
    
    try:
        if LLM_PROVIDER == "claude":
            return _get_help_claude(selected_text)
        elif LLM_PROVIDER == "openrouter":
            return _get_help_openrouter(selected_text)
        elif LLM_PROVIDER == "nvidia":
            return _get_help_nvidia(selected_text)
        elif LLM_PROVIDER == "ollama":
            return _get_help_ollama(selected_text)
        else:  # gemini
            return _get_help_gemini(selected_text)
    except Exception as e:
        print(f"[CONTEXT HELP] Error: {e}")
        import traceback
        traceback.print_exc()
        return f"Sorry, I encountered an error while processing your request:\n\n{str(e)}"


def _build_help_prompt(selected_text: str) -> str:
    """Build the prompt for context help.
    
    Args:
        selected_text: The selected text
        
    Returns:
        str: The formatted prompt
    """
    return f"""You are a helpful AI assistant. The user has selected the following text and pressed Alt+G for help:

"{selected_text}"

Please provide a clear, concise, and helpful explanation about this text. Consider:
- What it means or represents
- Its context or purpose
- Any relevant technical details if it's code or technical content
- Practical usage or examples if applicable
- Common issues or tips if relevant

Keep your response focused, informative, and easy to understand. Use bullet points or short paragraphs for clarity."""


def _get_help_gemini(selected_text: str) -> str:
    """Get context help using Gemini."""
    try:
        from google import genai
        from google.genai import types
        
        client = genai.Client(api_key=GEMINI_API_KEY)
        prompt = _build_help_prompt(selected_text)
        
        print("[CONTEXT HELP] Calling Gemini...")
        
        response = client.models.generate_content(
            model='gemini-2.0-flash-exp',
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.7,
                max_output_tokens=1000
            )
        )
        
        answer = response.text.strip()
        print(f"[CONTEXT HELP] Received response ({len(answer)} chars)")
        return answer
        
    except Exception as e:
        print(f"[CONTEXT HELP] Gemini error: {e}")
        raise


def _get_help_claude(selected_text: str) -> str:
    """Get context help using Claude."""
    try:
        import anthropic
        
        client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)
        prompt = _build_help_prompt(selected_text)
        
        print(f"[CONTEXT HELP] Calling Claude ({CLAUDE_MODEL})...")
        
        message = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=1000,
            temperature=0.7,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        
        answer = message.content[0].text.strip()
        print(f"[CONTEXT HELP] Received response ({len(answer)} chars)")
        return answer
        
    except Exception as e:
        print(f"[CONTEXT HELP] Claude error: {e}")
        raise


def _get_help_openrouter(selected_text: str) -> str:
    """Get context help using OpenRouter."""
    try:
        from openai import OpenAI
        
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=OPENROUTER_API_KEY
        )
        prompt = _build_help_prompt(selected_text)
        
        print(f"[CONTEXT HELP] Calling OpenRouter ({OPENROUTER_MODEL})...")
        
        response = client.chat.completions.create(
            model=OPENROUTER_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_tokens=1000,
            temperature=0.7
        )
        
        answer = response.choices[0].message.content.strip()
        print(f"[CONTEXT HELP] Received response ({len(answer)} chars)")
        return answer
        
    except Exception as e:
        print(f"[CONTEXT HELP] OpenRouter error: {e}")
        raise


def _get_help_nvidia(selected_text: str) -> str:
    """Get context help using NVIDIA API."""
    try:
        from openai import OpenAI
        
        client = OpenAI(
            base_url="https://integrate.api.nvidia.com/v1",
            api_key=NVIDIA_API_KEY
        )
        prompt = _build_help_prompt(selected_text)
        
        print(f"[CONTEXT HELP] Calling NVIDIA ({NVIDIA_MODEL})...")
        
        response = client.chat.completions.create(
            model=NVIDIA_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_tokens=1000,
            temperature=0.7
        )
        
        answer = response.choices[0].message.content.strip()
        print(f"[CONTEXT HELP] Received response ({len(answer)} chars)")
        return answer
        
    except Exception as e:
        print(f"[CONTEXT HELP] NVIDIA error: {e}")
        raise


def _get_help_ollama(selected_text: str) -> str:
    """Get context help using Ollama local model."""
    try:
        import requests
        
        prompt = _build_help_prompt(selected_text)
        
        print(f"[CONTEXT HELP] Calling Ollama ({OLLAMA_MODEL})...")
        
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "num_predict": 1000
                }
            },
            timeout=60
        )
        
        response.raise_for_status()
        result = response.json()
        answer = result.get("response", "").strip()
        
        print(f"[CONTEXT HELP] Received response ({len(answer)} chars)")
        return answer
        
    except Exception as e:
        print(f"[CONTEXT HELP] Ollama error: {e}")
        raise


# Made with Bob