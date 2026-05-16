# 🚀 AXON with Ollama - Quick Start Guide

## ✅ You're Ready to Go!

Your Ollama setup is **complete and verified**. Everything is working perfectly!

### 📊 Current Status

- ✅ **Ollama Service**: Running at `http://localhost:11434`
- ✅ **Model Installed**: `llama3.2-vision:11b` (10.7B parameters, Q4_K_M quantization)
- ✅ **Model Location**: `F:\OllamaModels\blobs`
- ✅ **AXON Configuration**: Switched to Ollama
- ✅ **Integration Tests**: All passed successfully

---

## 🎯 How to Use AXON with Ollama

### Option 1: Run AXON Normally (Recommended)

```bash
cd ibm-bob-hackathon/axon
python main.py
```

That's it! AXON will automatically use your local Ollama model.

### Option 2: Test First (Optional)

If you want to verify everything is working before running AXON:

```bash
cd ibm-bob-hackathon/axon
python test_ollama.py
```

---

## 🔧 Key Features

### ✨ Benefits of Using Ollama

- **100% Free**: No API costs, no usage limits
- **Private**: All processing happens locally on your machine
- **Offline**: Works without internet connection
- **Fast**: Direct local inference, no network latency
- **GPU Accelerated**: Uses your GPU for faster processing

### 📝 Model Details

- **Name**: llama3.2-vision:11b
- **Size**: 7.8 GB
- **Parameters**: 10.7 billion
- **Capabilities**: Vision + Text understanding
- **Quantization**: Q4_K_M (optimized for speed/quality balance)

---

## 🎮 Usage Tips

### Starting AXON

1. **Make sure Ollama is running** (it should auto-start with Windows)
2. **Navigate to the AXON directory**:
   ```bash
   cd ibm-bob-hackathon/axon
   ```
3. **Run AXON**:
   ```bash
   python main.py
   ```

### Verifying Ollama Status

Check if Ollama is running and which models are available:

```bash
# Check Ollama status
python -c "import requests; print('✅ Ollama is running!' if requests.get('http://localhost:11434/api/tags').status_code == 200 else '❌ Ollama is not running')"

# Or check current LLM configuration
python switch_llm.py status
```

---

## 🔄 Switching Between LLM Providers

You can easily switch between different LLM providers:

```bash
# Switch to Ollama (local, free)
python switch_llm.py ollama

# Switch to other providers (requires API keys)
python switch_llm.py gemini
python switch_llm.py claude
python switch_llm.py openrouter
python switch_llm.py nvidia

# Check current provider
python switch_llm.py status
```

---

## 🐛 Troubleshooting

### Issue: "Ollama is not running"

**Solution**: Start the Ollama service

1. Check if Ollama is installed:
   - Look for Ollama in your system tray (bottom-right corner)
   - Or check if the service is running in Task Manager

2. If not running, start Ollama:
   - Open Ollama from Start Menu
   - Or run: `ollama serve` in a terminal

### Issue: "Model not found"

**Solution**: Your model is already downloaded at `F:\OllamaModels\`

If Ollama can't find it, you may need to set the environment variable:

```powershell
# In PowerShell
$env:OLLAMA_MODELS = "F:\OllamaModels"
```

Or add it permanently:
1. Open System Properties → Environment Variables
2. Add new system variable:
   - Name: `OLLAMA_MODELS`
   - Value: `F:\OllamaModels`

### Issue: "Connection refused to localhost:11434"

**Solution**: Ollama service is not running

1. Start Ollama from the Start Menu
2. Or run in terminal: `ollama serve`
3. Wait a few seconds for it to start
4. Try again

### Issue: Slow performance

**Possible causes**:
- GPU not being used (check with `nvidia-smi`)
- Other applications using GPU
- Model needs to load into memory (first request is slower)

**Solutions**:
- Close other GPU-intensive applications
- Wait for model to fully load (first request takes longer)
- Check GPU usage: `nvidia-smi`

---

## 📊 Performance Expectations

### First Request
- **Loading time**: 5-10 seconds (model loads into memory)
- **Response time**: 10-20 seconds

### Subsequent Requests
- **Response time**: 3-8 seconds (model already in memory)
- **Streaming**: Real-time token generation

### Memory Usage
- **GPU VRAM**: ~8 GB (for the 11B model)
- **System RAM**: ~2-4 GB

---

## 🎯 What AXON Can Do with Ollama

AXON uses the vision model to:

1. **Understand Screenshots**: Analyzes what's on your screen
2. **Identify UI Elements**: Finds buttons, text fields, menus, etc.
3. **Extract Text**: Reads text from images using OCR
4. **Plan Actions**: Decides what to click/type based on your goal
5. **Execute Tasks**: Performs the actions automatically

### Example Workflow

1. You say: "Open Notepad and type 'Hello World'"
2. AXON takes a screenshot
3. Ollama analyzes the screen
4. AXON clicks Start menu
5. AXON types "Notepad"
6. AXON opens Notepad
7. AXON types "Hello World"

All of this happens **locally** on your machine with **no internet required**!

---

## 🔐 Privacy & Security

### Your Data Stays Local

- ✅ Screenshots never leave your computer
- ✅ No data sent to external servers
- ✅ No telemetry or tracking
- ✅ Complete privacy

### Model Storage

- Models stored at: `F:\OllamaModels\`
- Total size: ~7.8 GB
- No cloud sync or backup

---

## 📚 Additional Resources

### Documentation
- [OLLAMA_SETUP.md](./OLLAMA_SETUP.md) - Detailed setup instructions
- [LLM_SETUP_GUIDE.md](./LLM_SETUP_GUIDE.md) - All LLM provider options
- [README.md](./README.md) - Main AXON documentation

### Testing
- `test_ollama.py` - Test Ollama integration
- `test_full_flow.py` - Test complete AXON workflow

### Configuration
- `.env` - Environment variables
- `config.py` - AXON configuration

---

## 🎉 You're All Set!

Your Ollama setup is complete and verified. Just run:

```bash
cd ibm-bob-hackathon/axon
python main.py
```

And start automating your tasks with AXON! 🚀

---

## 💡 Pro Tips

1. **Keep Ollama Running**: Let it run in the background for instant responses
2. **First Request is Slower**: Model needs to load into memory
3. **GPU Monitoring**: Use `nvidia-smi` to check GPU usage
4. **Model Stays Loaded**: Once loaded, model stays in memory for fast responses
5. **No Internet Needed**: Works completely offline

---

## 🆘 Need Help?

If you encounter any issues:

1. Check this guide's troubleshooting section
2. Run `python test_ollama.py` to diagnose issues
3. Check Ollama logs (if available)
4. Verify GPU is working: `nvidia-smi`

---

**Last Updated**: 2026-05-16  
**Status**: ✅ Verified Working  
**Model**: llama3.2-vision:11b  
**Location**: F:\OllamaModels\