# LLM Setup Guide - Multi-Provider Support

This guide explains how to use Claude, Gemini, OpenRouter, and NVIDIA models with AXON and switch between them.

## 🚀 Quick Start

### 1. Get Your API Keys

**Claude (Anthropic):**
- Visit: https://console.anthropic.com/
- Sign up and get your API key
- Add to `.env`: `CLAUDE_API_KEY=your_key_here`

**Gemini (Google):**
- Visit: https://aistudio.google.com/app/apikey
- Get your API key
- Add to `.env`: `GEMINI_API_KEY=your_key_here`

**OpenRouter:**
- Visit: https://openrouter.ai/
- Sign up and get your API key
- Add to `.env`: `OPENROUTER_API_KEY=your_key_here`

**NVIDIA:**
- Visit: https://build.nvidia.com/
- Sign up and get your API key
- Add to `.env`: `NVIDIA_API_KEY=your_key_here`

### 2. Configure Your Provider

Edit `.env` file:

```env
# Choose your provider: "claude", "gemini", "openrouter", or "nvidia"
LLM_PROVIDER=nvidia

# Claude Configuration
CLAUDE_API_KEY=your_claude_api_key_here
CLAUDE_MODEL=claude-3-5-sonnet-20241022

# Gemini Configuration
GEMINI_API_KEY=your_gemini_api_key_here

# OpenRouter Configuration
OPENROUTER_API_KEY=your_openrouter_api_key_here
OPENROUTER_MODEL=anthropic/claude-3.5-haiku

# NVIDIA Configuration
NVIDIA_API_KEY=your_nvidia_api_key_here
NVIDIA_MODEL=google/gemma-3n-e2b-it
```

### 3. Install Required Packages

```bash
# For Claude support
pip install anthropic

# For Gemini support (already installed)
pip install google-genai

# For switching utility
pip install python-dotenv
```

## 🔄 Switching Between Models

### Method 1: Using the Switch Script (Recommended)

```bash
# Switch to Claude
python switch_llm.py claude

# Switch to Gemini
python switch_llm.py gemini

# Switch to OpenRouter
python switch_llm.py openrouter

# Switch to NVIDIA
python switch_llm.py nvidia

# Check current status
python switch_llm.py status
```

### Method 2: Edit .env Manually

Change the `LLM_PROVIDER` value in `.env`:

```env
LLM_PROVIDER=nvidia   # or "claude", "gemini", "openrouter"
```

Then restart the application.

### Method 3: Programmatically (Advanced)

```python
from core.llm import switch_provider, get_current_provider

# Switch to Claude
switch_provider("claude")

# Switch to Gemini
switch_provider("gemini")

# Switch to OpenRouter
switch_provider("openrouter")

# Switch to NVIDIA
switch_provider("nvidia")

# Check current provider
current = get_current_provider()
print(f"Using: {current}")
```

## 📊 Available Models

### Claude Models

| Model | Speed | Capability | Best For |
|-------|-------|------------|----------|
| **claude-3-5-sonnet-20241022** | ⚡⚡⚡ | ⭐⭐⭐⭐⭐ | **Recommended** - Best balance |
| claude-3-5-haiku-20241022 | ⚡⚡⚡⚡ | ⭐⭐⭐⭐ | Fast tasks |
| claude-3-opus-20240229 | ⚡⚡ | ⭐⭐⭐⭐⭐ | Complex tasks |

### Gemini Models

| Model | Speed | Capability | Best For |
|-------|-------|------------|----------|
| **gemini-2.5-flash** | ⚡⚡⚡⚡ | ⭐⭐⭐⭐ | **Default** - Fast & capable |
| gemini-2.5-pro | ⚡⚡⚡ | ⭐⭐⭐⭐⭐ | Complex reasoning |

### OpenRouter Models

| Model | Speed | Capability | Best For |
|-------|-------|------------|----------|
| **anthropic/claude-3.5-haiku** | ⚡⚡⚡⚡ | ⭐⭐⭐⭐ | **Default** - Fast & affordable |
| anthropic/claude-3.5-sonnet | ⚡⚡⚡ | ⭐⭐⭐⭐⭐ | Best performance |
| google/gemini-2.0-flash-exp:free | ⚡⚡⚡⚡ | ⭐⭐⭐⭐ | Free tier option |

### NVIDIA Models

| Model | Speed | Capability | Best For |
|-------|-------|------------|----------|
| **google/gemma-3n-e2b-it** | ⚡⚡⚡⚡ | ⭐⭐⭐⭐ | **Default** - Fast & efficient |
| meta/llama-3.1-8b-instruct | ⚡⚡⚡⚡ | ⭐⭐⭐⭐ | Open source option |
| nvidia/llama-3.1-nemotron-70b-instruct | ⚡⚡⚡ | ⭐⭐⭐⭐⭐ | Most capable |

## 🎯 When to Use Which Provider

### Use Claude When:
- ✅ You need the best instruction following
- ✅ You want most reliable structured outputs
- ✅ You have budget for premium API

### Use Gemini When:
- ✅ You want to save on API costs
- ✅ You need fast vision capabilities
- ✅ You're already familiar with Google AI

### Use OpenRouter When:
- ✅ You want access to multiple models
- ✅ You need flexible pricing options
- ✅ You want to try different models easily

### Use NVIDIA When:
- ✅ You want free or low-cost API access
- ✅ You need fast inference speeds
- ✅ You want to use open-source models
- ✅ You're experimenting with different models

## 💡 Tips & Best Practices

1. **Start with NVIDIA** - Free tier is great for testing and development
2. **Keep all API keys configured** - Easy to switch when needed
3. **Monitor your usage** - Check API dashboards for costs
4. **Test different providers** - See which works best for your specific tasks
5. **Use OpenRouter for flexibility** - Access multiple models with one API key

## 🔧 Troubleshooting

### "API_KEY not found"
- Make sure you've added your API key to `.env`
- Check that `.env` file is in the `axon` directory
- Restart the application after adding the key

### "Package not installed"
```bash
# For Claude
pip install anthropic

# For OpenRouter
pip install openai

# For NVIDIA (requests is usually pre-installed)
pip install requests
```

### Model not switching
- Make sure you restart the application after changing `.env`
- Use `python switch_llm.py status` to verify current configuration

### API Rate Limits
- Claude: Check https://console.anthropic.com/
- Gemini: Check https://aistudio.google.com/
- OpenRouter: Check https://openrouter.ai/
- NVIDIA: Check https://build.nvidia.com/

### NVIDIA API Errors
- Verify your API key is correct
- Check if the model name is valid
- Some models may require approval or have usage limits

## 📝 Example .env Configuration

```env
# LLM Provider Selection
LLM_PROVIDER=nvidia

# Claude Configuration
CLAUDE_API_KEY=sk-ant-api03-xxxxxxxxxxxxx
CLAUDE_MODEL=claude-3-5-sonnet-20241022

# Gemini Configuration
GEMINI_API_KEY=AIzaSyBHnBEhv45doirhPJ9j7-6GMJmSY2ffw7o

# OpenRouter Configuration
OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxxx
OPENROUTER_MODEL=anthropic/claude-3.5-haiku

# NVIDIA Configuration
NVIDIA_API_KEY=nvapi-xxxxxxxxxxxxx
NVIDIA_MODEL=google/gemma-3n-e2b-it

# Other settings...
```

## 🚨 Important Notes

- **Restart Required**: Always restart the application after changing providers
- **API Costs**: Monitor your usage on respective dashboards
- **Rate Limits**: Be aware of rate limits for each provider
- **Model Availability**: Some models may not be available in all regions

## 📞 Support

If you encounter issues:
1. Check this guide first
2. Verify your API keys are correct
3. Check the console for error messages
4. Try switching to the other provider

---

Made with ❤️ for better AI agent performance