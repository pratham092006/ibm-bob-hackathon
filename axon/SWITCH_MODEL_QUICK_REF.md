# Model Switching - Quick Reference Card

## 🚀 One-Line Commands

```bash
# Check current model
python switch_llm.py

# Switch to Ollama with llama3.2-vision:11b (RECOMMENDED)
python switch_llm.py ollama llama3.2-vision:11b

# Switch to other Ollama models
python switch_llm.py ollama qwen2.5vl:7b
python switch_llm.py ollama llama3.2-vision:90b

# Switch to cloud providers
python switch_llm.py gemini
python switch_llm.py claude
python switch_llm.py openrouter
python switch_llm.py nvidia
```

## 📋 Current Configuration

**Provider:** Ollama (Local)  
**Model:** llama3.2-vision:11b  
**Status:** ✅ Active  
**Cost:** FREE  
**Privacy:** 100% Local  

## 🔄 Common Workflows

### Test Different Models
```bash
# Fast model (7B)
python switch_llm.py ollama qwen2.5vl:7b

# Balanced model (11B) - RECOMMENDED
python switch_llm.py ollama llama3.2-vision:11b

# Best quality (32B)
python switch_llm.py ollama qwen2.5vl:32b
```

### Switch to Cloud for Better Performance
```bash
# Fast and cheap
python switch_llm.py gemini

# Best quality
python switch_llm.py claude

# Free tier available
python switch_llm.py openrouter
```

## ⚠️ Important

- **Always restart the application** after switching models
- For Ollama: Make sure the model is downloaded first
  ```bash
  ollama pull llama3.2-vision:11b
  ```

## 📖 Full Documentation

See `MODEL_SWITCHING_GUIDE.md` for complete details.