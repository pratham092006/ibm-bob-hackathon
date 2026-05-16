# 🦙 Ollama Local Model Setup Guide

## What is Ollama?

Ollama is a tool that lets you run powerful AI models **locally on your computer**. This means:

- ✅ **100% FREE** - No API costs, ever
- ✅ **100% PRIVATE** - Your data never leaves your machine
- ✅ **FAST** - No network latency, instant responses
- ✅ **OFFLINE** - Works without internet connection
- ✅ **NO RATE LIMITS** - Use as much as you want

## Why Use Ollama with AXON?

AXON can use Ollama to run vision-capable AI models locally, giving you:

1. **Privacy**: Screenshots and tasks stay on your computer
2. **Cost Savings**: No API fees from cloud providers
3. **Speed**: Local inference is often faster than API calls
4. **Reliability**: No dependency on external services or internet

## Installation

### Windows

1. **Download Ollama**
   - Visit: https://ollama.com/download
   - Download the Windows installer
   - Run the installer and follow the prompts

2. **Verify Installation**
   ```powershell
   ollama --version
   ```

### macOS

```bash
# Using Homebrew
brew install ollama

# Or download from https://ollama.com/download
```

### Linux

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

## Installing Vision Models

AXON requires a **vision-capable model** to analyze screenshots. Here are the recommended models:

### Recommended: Llama 3.2 Vision (11B)

This is the model you currently have installed and is **highly recommended** for AXON:

```bash
ollama pull llama3.2-vision:11b
```

**Specs:**
- Size: ~7.8 GB
- RAM Required: ~12 GB
- Quality: Excellent for computer vision tasks
- Speed: Fast on modern hardware

### Alternative: Llama 3.2 Vision (90B)

For maximum quality (requires powerful hardware):

```bash
ollama pull llama3.2-vision:90b
```

**Specs:**
- Size: ~55 GB
- RAM Required: ~64 GB
- Quality: Best available
- Speed: Slower, but highest accuracy

### Alternative: LLaVA

A lighter alternative if you have limited resources:

```bash
ollama pull llava:13b
```

**Specs:**
- Size: ~8 GB
- RAM Required: ~10 GB
- Quality: Good for basic tasks
- Speed: Very fast

## Configuring AXON to Use Ollama

### 1. Check Your Installation

First, verify Ollama is running and your model is available:

```powershell
# Check if Ollama is running
ollama list

# You should see something like:
# NAME                   ID              SIZE      MODIFIED
# llama3.2-vision:11b    6f2f9757ae97    7.8 GB    About an hour ago
```

### 2. Update Your .env File

Your `.env` file should already have these settings (they were added automatically):

```env
# Ollama Local Model Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2-vision:11b

# LLM Provider Selection
LLM_PROVIDER='ollama'
```

### 3. Switch to Ollama

Use the switch script to activate Ollama:

```powershell
python switch_llm.py ollama
```

You should see:

```
[OK] Switched to OLLAMA
  Model: llama3.2-vision:11b
  Base URL: http://localhost:11434
  ✓ Local model - No API key needed!
  ✓ Free, private, and offline

[OK] Restart the application for changes to take effect
```

### 4. Verify Configuration

Check your current setup:

```powershell
python switch_llm.py status
```

## Running AXON with Ollama

1. **Start Ollama Service** (if not already running):
   ```powershell
   ollama serve
   ```

2. **Run AXON**:
   ```powershell
   python main.py
   ```

3. **Give it a task**:
   - AXON will now use your local Ollama model
   - No API calls to external services
   - All processing happens on your machine

## Troubleshooting

### "Cannot connect to Ollama"

**Problem**: AXON can't reach the Ollama service.

**Solution**:
```powershell
# Make sure Ollama is running
ollama serve

# In another terminal, test the connection
curl http://localhost:11434/api/tags
```

### "Model not found"

**Problem**: The specified model isn't installed.

**Solution**:
```powershell
# List installed models
ollama list

# Pull the required model
ollama pull llama3.2-vision:11b
```

### Slow Performance

**Problem**: Model is running slowly.

**Solutions**:
1. **Use a smaller model**:
   ```powershell
   ollama pull llava:7b
   ```
   Then update `.env`:
   ```env
   OLLAMA_MODEL=llava:7b
   ```

2. **Close other applications** to free up RAM

3. **Check GPU usage**:
   - Ollama automatically uses GPU if available
   - Ensure your GPU drivers are up to date

### Out of Memory

**Problem**: System runs out of RAM.

**Solutions**:
1. Use a smaller model (llava:7b instead of llama3.2-vision:11b)
2. Close other applications
3. Increase system swap/page file

## Model Comparison

| Model | Size | RAM Needed | Quality | Speed | Best For |
|-------|------|------------|---------|-------|----------|
| llama3.2-vision:11b | 7.8 GB | 12 GB | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | **Recommended** |
| llama3.2-vision:90b | 55 GB | 64 GB | ⭐⭐⭐⭐⭐ | ⭐⭐ | High-end systems |
| llava:13b | 8 GB | 10 GB | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Budget systems |
| llava:7b | 4.7 GB | 6 GB | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Low-end systems |

## Advanced Configuration

### Custom Ollama Port

If you're running Ollama on a different port:

```env
OLLAMA_BASE_URL=http://localhost:8080
```

### Remote Ollama Server

You can even run Ollama on another machine:

```env
OLLAMA_BASE_URL=http://192.168.1.100:11434
```

### Model Parameters

You can customize model behavior in `core/llm.py` in the `_call_ollama` function:

```python
"options": {
    "temperature": 0.7,  # Lower = more focused, Higher = more creative
    "num_predict": 512,  # Max tokens to generate
    "top_p": 0.9,        # Nucleus sampling
    "top_k": 40          # Top-k sampling
}
```

## Performance Tips

1. **First Run is Slower**: The model loads into memory on first use
2. **Keep Ollama Running**: Leave `ollama serve` running in the background
3. **Use SSD**: Store models on an SSD for faster loading
4. **GPU Acceleration**: Ollama automatically uses CUDA/Metal if available
5. **RAM**: More RAM = better performance, especially for larger models

## Switching Between Providers

You can easily switch between Ollama and cloud providers:

```powershell
# Use local Ollama (free, private)
python switch_llm.py ollama

# Use NVIDIA API (cloud, requires API key)
python switch_llm.py nvidia

# Use Claude (cloud, requires API key)
python switch_llm.py claude

# Check current provider
python switch_llm.py status
```

## Benefits Summary

### Ollama (Local)
- ✅ Free forever
- ✅ Complete privacy
- ✅ No internet needed
- ✅ No rate limits
- ✅ Fast (no network latency)
- ❌ Requires good hardware
- ❌ Uses local resources

### Cloud APIs (Claude, Gemini, etc.)
- ✅ No local resources needed
- ✅ Access to latest models
- ✅ Works on any hardware
- ❌ Costs money
- ❌ Requires internet
- ❌ Data sent to cloud
- ❌ Rate limits apply

## Getting Help

- **Ollama Documentation**: https://ollama.com/docs
- **Model Library**: https://ollama.com/library
- **GitHub Issues**: https://github.com/ollama/ollama/issues

## Next Steps

1. ✅ Install Ollama
2. ✅ Pull a vision model (`llama3.2-vision:11b`)
3. ✅ Configure AXON to use Ollama
4. ✅ Test with a simple task
5. 🎉 Enjoy free, private AI automation!

---

**Made with Bob** 🤖