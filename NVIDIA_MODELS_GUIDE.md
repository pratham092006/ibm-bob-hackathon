# NVIDIA Models Guide for AXON

## Recommended Models for Desktop Automation

Based on the task requirements (vision + reasoning + instruction following), here are the best NVIDIA models:

### 🏆 Top Recommendations

#### 1. **moonshotai/kimi-k2.6** (🌟 BEST - RECOMMENDED)
- **Model ID**: `moonshotai/kimi-k2.6`
- **Why**: Has **thinking mode** for better reasoning, excellent instruction following
- **Speed**: Medium (3-6s per request)
- **Cost**: Free tier available
- **Special Features**:
  - ✨ Thinking mode enabled (`chat_template_kwargs: {"thinking": True}`)
  - 🧠 Better reasoning and planning
  - 📝 16K max tokens (vs 512 for others)
- **Best for**: Complex multi-step tasks, desktop automation, accurate action planning

#### 2. **nvidia/llama-3.1-nemotron-70b-instruct** (EXCELLENT)
- **Model ID**: `nvidia/llama-3.1-nemotron-70b-instruct`
- **Why**: NVIDIA's optimized version, best reasoning capabilities
- **Speed**: Medium-Fast (2-4s per request)
- **Cost**: Free tier available
- **Best for**: Most accurate results, complex reasoning

#### 3. **meta/llama-3.1-70b-instruct** (VERY GOOD)
- **Model ID**: `meta/llama-3.1-70b-instruct`
- **Why**: Excellent instruction following, strong reasoning, good with complex tasks
- **Speed**: Medium (3-5s per request)
- **Cost**: Free tier available
- **Best for**: Complex multi-step tasks, accurate action planning

#### 4. **meta/llama-3.1-405b-instruct** (MOST POWERFUL)
- **Model ID**: `meta/llama-3.1-405b-instruct`
- **Why**: Largest and most capable, best understanding
- **Speed**: Slower (5-10s per request)
- **Cost**: May have limits
- **Best for**: When accuracy is critical

### ⚡ Fast Alternatives

#### 4. **meta/llama-3.1-8b-instruct** (FAST)
- **Model ID**: `meta/llama-3.1-8b-instruct`
- **Why**: Very fast, decent accuracy
- **Speed**: Very Fast (1-2s per request)
- **Cost**: Free
- **Best for**: Simple tasks, quick responses

#### 5. **mistralai/mistral-7b-instruct-v0.3** (BALANCED)
- **Model ID**: `mistralai/mistral-7b-instruct-v0.3`
- **Why**: Good balance of speed and accuracy
- **Speed**: Fast (1-3s per request)
- **Cost**: Free
- **Best for**: General purpose tasks

### ❌ NOT Recommended

- **google/gemma-3n-e2b-it** - Too small, poor instruction following (current issue)
- **google/gemma-2b-it** - Too small for complex tasks
- Small models (<7B parameters) - Not suitable for desktop automation

## How to Switch Models

### Option 1: Edit .env file
```env
NVIDIA_MODEL=meta/llama-3.1-70b-instruct
```

### Option 2: Use Python
```python
from dotenv import set_key
set_key('.env', 'NVIDIA_MODEL', 'meta/llama-3.1-70b-instruct')
```

### Option 3: Direct config change
Edit `config.py` and change the default:
```python
NVIDIA_MODEL = os.getenv("NVIDIA_MODEL", "meta/llama-3.1-70b-instruct")
```

## Testing Different Models

Run this command to test a model:
```bash
# Edit .env first, then:
python test_nvidia_api.py
```

## Model Comparison for Your Task

Your task: "Open chrome and search fitgirl"

| Model | Will it work? | Why |
|-------|---------------|-----|
| gemma-3n-e2b-it | ❌ NO | Gets stuck, poor reasoning |
| llama-3.1-8b | ✅ Maybe | Fast but may miss steps |
| llama-3.1-70b | ✅✅ YES | Best balance |
| nemotron-70b | ✅✅✅ BEST | Most accurate |
| llama-3.1-405b | ✅✅✅ BEST | Slowest but most capable |

## Recommended Setup

For best results with AXON (NOW ACTIVE):
```env
NVIDIA_MODEL=moonshotai/kimi-k2.6
```

This model will:
- ✅ Use **thinking mode** to reason through tasks
- ✅ Understand "open Chrome and search X" as two separate steps
- ✅ Wait for Chrome to open before typing
- ✅ Not get stuck in loops (has better loop detection)
- ✅ Follow multi-step instructions correctly
- ✅ Handle complex tasks with better planning

### Why Kimi K2.6 is Better:
1. **Thinking Mode**: The model "thinks" before acting, leading to better decisions
2. **Larger Context**: 16K tokens vs 512 tokens (can remember more)
3. **Better Reasoning**: Specifically designed for complex multi-step tasks
4. **Loop Prevention**: Better at detecting when it's repeating actions

## Available on NVIDIA API Catalog

Visit: https://build.nvidia.com/explore/discover

Search for:
- "llama-3.1-70b-instruct"
- "nemotron-70b-instruct"
- "llama-3.1-405b-instruct"

All are free to use with your API key!