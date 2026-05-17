"""Utility script to switch between Claude, Gemini, OpenRouter, NVIDIA, and Ollama LLM providers.

Usage:
    python switch_llm.py                              # Show current status
    python switch_llm.py status                       # Show current status
    python switch_llm.py claude                       # Switch to Claude
    python switch_llm.py gemini                       # Switch to Gemini
    python switch_llm.py openrouter                   # Switch to OpenRouter
    python switch_llm.py nvidia                       # Switch to NVIDIA
    python switch_llm.py ollama                       # Switch to Ollama (local)
    python switch_llm.py ollama llama3.2-vision:11b   # Switch to Ollama with specific model
"""

import sys
import os
from dotenv import load_dotenv, set_key

# Load environment variables
load_dotenv()

def switch_provider(provider: str, model: str | None = None) -> bool:
    """Switch the LLM provider in .env file.
    
    Args:
        provider: "claude", "gemini", "openrouter", "nvidia", or "ollama"
        model: Optional specific model name for the provider
    
    Returns:
        bool: True if successful
    """
    provider = provider.lower()
    
    if provider not in ["claude", "gemini", "openrouter", "nvidia", "ollama"]:
        print(f"[ERROR] Invalid provider: {provider}")
        print("   Use 'claude', 'gemini', 'openrouter', 'nvidia', or 'ollama'")
        return False
    
    env_file = ".env"
    if not os.path.exists(env_file):
        print(f"[ERROR] .env file not found")
        return False
    
    try:
        # Update the LLM_PROVIDER in .env
        set_key(env_file, "LLM_PROVIDER", provider)
        print(f"[OK] Switched to {provider.upper()}")
        
        if provider == "claude":
            model = os.getenv("CLAUDE_MODEL", "claude-3-5-sonnet-20241022")
            print(f"  Model: {model}")
            print(f"  Make sure CLAUDE_API_KEY is set in .env")
        elif provider == "openrouter":
            model = os.getenv("OPENROUTER_MODEL", "anthropic/claude-3.5-haiku")
            print(f"  Model: {model}")
            print(f"  Make sure OPENROUTER_API_KEY is set in .env")
        elif provider == "nvidia":
            model = os.getenv("NVIDIA_MODEL", "google/gemma-3n-e2b-it")
            print(f"  Model: {model}")
            print(f"  Make sure NVIDIA_API_KEY is set in .env")
        elif provider == "ollama":
            # If a specific model is provided, update it
            if model:
                set_key(env_file, "OLLAMA_MODEL", model)
                current_model = model
            else:
                current_model = os.getenv("OLLAMA_MODEL", "llama3.2-vision:11b")
            
            base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
            print(f"  Model: {current_model}")
            print(f"  Base URL: {base_url}")
            print(f"  [OK] Local model - No API key needed!")
            print(f"  [OK] Free, private, and offline")
        else:
            print(f"  Model: gemini-2.5-flash")
            print(f"  Make sure GEMINI_API_KEY is set in .env")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] {e}")
        return False


def show_status():
    """Show current LLM provider status."""
    provider = os.getenv("LLM_PROVIDER", "openrouter").lower()
    
    print(f"\n[STATUS] Current LLM Configuration:")
    print(f"   Provider: {provider.upper()}")
    
    if provider == "claude":
        model = os.getenv("CLAUDE_MODEL", "claude-3-5-sonnet-20241022")
        api_key = os.getenv("CLAUDE_API_KEY", "")
        print(f"   Model: {model}")
        print(f"   API Key: {'[OK] Set' if api_key else '[ERROR] Not set'}")
    elif provider == "openrouter":
        model = os.getenv("OPENROUTER_MODEL", "anthropic/claude-3.5-haiku")
        api_key = os.getenv("OPENROUTER_API_KEY", "")
        print(f"   Model: {model}")
        print(f"   API Key: {'[OK] Set' if api_key else '[ERROR] Not set'}")
    elif provider == "nvidia":
        model = os.getenv("NVIDIA_MODEL", "google/gemma-3n-e2b-it")
        api_key = os.getenv("NVIDIA_API_KEY", "")
        print(f"   Model: {model}")
        print(f"   API Key: {'[OK] Set' if api_key else '[ERROR] Not set'}")
    elif provider == "ollama":
        model = os.getenv("OLLAMA_MODEL", "llama3.2-vision:11b")
        base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        print(f"   Model: {model}")
        print(f"   Base URL: {base_url}")
        print(f"   API Key: [N/A] Local model - No API key needed")
        print(f"   Status: [OK] Free, private, and offline")
    else:
        api_key = os.getenv("GEMINI_API_KEY", "")
        print(f"   Model: gemini-2.5-flash")
        print(f"   API Key: {'[OK] Set' if api_key else '[ERROR] Not set'}")
    
    print(f"\n[INFO] To switch providers:")
    print(f"   python switch_llm.py claude")
    print(f"   python switch_llm.py gemini")
    print(f"   python switch_llm.py openrouter")
    print(f"   python switch_llm.py nvidia")
    print(f"   python switch_llm.py ollama      # Local model (FREE!)")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        show_status()
        sys.exit(0)
    
    command = sys.argv[1].lower()
    
    if command == "status":
        show_status()
    elif command in ["claude", "gemini", "openrouter", "nvidia", "ollama"]:
        # Check if a specific model is provided as second argument
        model = sys.argv[2] if len(sys.argv) > 2 else None
        
        if switch_provider(command, model):
            print(f"\n[OK] Restart the application for changes to take effect")
            sys.exit(0)
        else:
            sys.exit(1)
    else:
        print(f"[ERROR] Unknown command: {command}")
        print("   Use: claude, gemini, openrouter, nvidia, ollama, or status")
        sys.exit(1)

# Made with Bob
