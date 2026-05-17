# Model Switching Guide

## Quick Reference

The `switch_llm.py` script provides a simple command-line interface to switch between different LLM providers and models.

## Basic Usage

### Check Current Model
```bash
python switch_llm.py
# or
python switch_llm.py status
```

This displays:
- Current provider (Claude, Gemini, OpenRouter, NVIDIA, or Ollama)
- Current model name
- API key status
- Additional configuration details

### Switch Providers

#### Switch to Claude
```bash
python switch_llm.py claude
```
- Uses: `claude-3-5-sonnet-20241022` (default)
- Requires: `CLAUDE_API_KEY` in `.env`

#### Switch to Gemini
```bash
python switch_llm.py gemini
```
- Uses: `gemini-2.5-flash` (default)
- Requires: `GEMINI_API_KEY` in `.env`

#### Switch to OpenRouter
```bash
python switch_llm.py openrouter
```
- Uses: `anthropic/claude-3.5-haiku` (default)
- Requires: `OPENROUTER_API_KEY` in `.env`

#### Switch to NVIDIA
```bash
python switch_llm.py nvidia
```
- Uses: `meta/llama-3.2-90b-vision-instruct` (default)
- Requires: `NVIDIA_API_KEY` in `.env`

#### Switch to Ollama (Local)
```bash
python switch_llm.py ollama
```
- Uses: Current `OLLAMA_MODEL` from `.env`
- **No API key required** - runs locally
- **Free, private, and offline**

### Switch Ollama Models

You can specify a different Ollama model when switching:

```bash
python switch_llm.py ollama llama3.2-vision:11b
```

This will:
1. Switch provider to Ollama
2. Update the `OLLAMA_MODEL` in `.env` to `llama3.2-vision:11b`
3. Persist the change for future sessions

#### Popular Ollama Vision Models

```bash
# Llama 3.2 Vision (11B) - Recommended for computer control
python switch_llm.py ollama llama3.2-vision:11b

# Llama 3.2 Vision (90B) - Most capable, requires more resources
python switch_llm.py ollama llama3.2-vision:90b

# Qwen 2.5 VL (7B) - Fast and efficient
python switch_llm.py ollama qwen2.5vl:7b

# Qwen 2.5 VL (32B) - More capable
python switch_llm.py ollama qwen2.5vl:32b
```

## Available Providers

| Provider | Cost | API Key Required | Best For |
|----------|------|------------------|----------|
| **Ollama** | FREE | ❌ No | Local, private, offline use |
| **Gemini** | Low | ✅ Yes | Fast responses, good quality |
| **OpenRouter** | Variable | ✅ Yes | Access to multiple models |
| **Claude** | Medium | ✅ Yes | High quality, complex tasks |
| **NVIDIA** | Free (limited) | ✅ Yes | Vision tasks, GPU acceleration |

## How It Works

1. **Reads** current configuration from `.env` file
2. **Updates** the `LLM_PROVIDER` variable (and optionally model-specific variables)
3. **Persists** changes to `.env` file
4. **Shows** before/after configuration

## Important Notes

### After Switching
- **Restart the application** for changes to take effect
- The script updates `.env` but doesn't reload running processes

### API Keys
- Make sure the required API key is set in `.env` before switching
- Ollama doesn't require an API key (local model)

### Model Availability
- For Ollama: Make sure the model is downloaded first
  ```bash
  ollama pull llama3.2-vision:11b
  ```
- For other providers: Check their documentation for available models

## Troubleshooting

### "API Key not set" Error
Add the required API key to your `.env` file:
```bash
# For Claude
CLAUDE_API_KEY=sk-ant-...

# For Gemini
GEMINI_API_KEY=AIza...

# For OpenRouter
OPENROUTER_API_KEY=sk-or-v1-...

# For NVIDIA
NVIDIA_API_KEY=nvapi-...
```

### Ollama Connection Error
1. Make sure Ollama is running:
   ```bash
   ollama serve
   ```
2. Check if the model is downloaded:
   ```bash
   ollama list
   ```
3. Pull the model if needed:
   ```bash
   ollama pull llama3.2-vision:11b
   ```

### Changes Not Taking Effect
- Restart the application after switching
- Check that `.env` file was updated correctly
- Verify no syntax errors in `.env` file

## Examples

### Example 1: Switch to Local Ollama Model
```bash
# Check current status
python switch_llm.py status

# Switch to Ollama with llama3.2-vision:11b
python switch_llm.py ollama llama3.2-vision:11b

# Verify the change
python switch_llm.py status

# Restart your application
python main.py
```

### Example 2: Switch Between Cloud Providers
```bash
# Try Gemini (fast and cheap)
python switch_llm.py gemini

# If you need better quality, switch to Claude
python switch_llm.py claude

# For free tier, use OpenRouter
python switch_llm.py openrouter
```

### Example 3: Test Different Ollama Models
```bash
# Try the 7B model (faster)
python switch_llm.py ollama qwen2.5vl:7b

# If you need better quality, try 11B
python switch_llm.py ollama llama3.2-vision:11b

# For best quality (if you have resources), try 32B
python switch_llm.py ollama qwen2.5vl:32b
```

## Advanced Configuration

### Manually Edit .env
You can also manually edit the `.env` file:

```bash
# Set the provider
LLM_PROVIDER=ollama

# Set the Ollama model
OLLAMA_MODEL=llama3.2-vision:11b

# Set the Ollama base URL (if different)
OLLAMA_BASE_URL=http://localhost:11434
```

### Provider-Specific Models
Each provider has its own model configuration in `.env`:

```bash
# Claude models
CLAUDE_MODEL=claude-3-5-sonnet-20241022

# Gemini models (configured in config.py)
# Use "flash" or "pro"

# OpenRouter models
OPENROUTER_MODEL=anthropic/claude-3.5-haiku

# NVIDIA models
NVIDIA_MODEL=meta/llama-3.2-90b-vision-instruct

# Ollama models
OLLAMA_MODEL=llama3.2-vision:11b
```

## Summary

The `switch_llm.py` script makes it easy to:
- ✅ Check current model configuration
- ✅ Switch between providers with one command
- ✅ Change Ollama models on the fly
- ✅ Persist changes to `.env` file
- ✅ Get clear feedback on configuration status

For more information on setting up specific providers, see:
- `LLM_SETUP_GUIDE.md` - General LLM setup
- `OLLAMA_QUICK_START.md` - Ollama-specific setup
- `FREE_LLM_OPTIONS.md` - Free provider options