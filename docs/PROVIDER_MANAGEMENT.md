# Provider Management Guide

Cradle now supports multiple LLM providers with an easy-to-use management system.

## Supported Providers

| Provider | Type | Cost | Vision Support | Setup |
|----------|------|------|----------------|-------|
| **OpenAI** | API | Paid (~$0.015/1K tokens) | ✅ Yes | API Key |
| **Claude** | API | Paid (~$0.018/1K tokens) | ✅ Yes | API Key |
| **Ollama** | Local | FREE | ✅ Yes | Install + Pull Model |
| **LM Studio** | Local | FREE | ✅ Yes | Install + Load Model |
| **vLLM** | Local | FREE | ✅ Yes | Install + Start Server |

---

## Quick Start

### 1. Check Available Providers

```bash
# See all providers and their status
python providers.py

# Detailed status
python providers.py --status
```

### 2. Select a Provider

```bash
# Interactive selection (recommended)
python providers.py --select

# Or set directly
python providers.py --set-default ollama
```

### 3. Run Cradle

```bash
# Use default provider
python run.py skylines

# Or specify provider
python run.py skylines --llm ollama
python run.py rdr2-story --llm openai
```

---

## Provider Details

### OpenAI

**Setup:**
```bash
# 1. Get API key from https://platform.openai.com/api-keys
# 2. Add to .env
echo 'OA_OPENAI_KEY=sk-...' >> .env

# 3. Set as default
python providers.py --set-default openai
```

**Models:** gpt-4o-2024-05-13 (vision support)
**Cost:** ~$10-50/hour depending on usage
**Best for:** Highest quality, production use

---

### Claude (Anthropic)

**Setup:**
```bash
# 1. Get API key from https://console.anthropic.com/settings/keys
# 2. Add to .env
echo 'OA_CLAUDE_KEY=sk-ant-...' >> .env

# 3. Set as default
python providers.py --set-default claude
```

**Models:** claude-3-5-sonnet-20241022
**Cost:** ~$15-50/hour
**Best for:** High quality, good reasoning

---

### Ollama (Recommended for Testing)

**Setup:**
```bash
# 1. Install from https://ollama.com
curl -fsSL https://ollama.com/install.sh | sh

# 2. Pull a vision model
ollama pull llama3.2-vision  # 11GB
# OR
ollama pull llava  # 4.7GB (smaller)

# 3. Pull embedding model
ollama pull nomic-embed-text

# 4. Set as default
python providers.py --set-default ollama
```

**Models:** llama3.2-vision, llava, mistral, etc.
**Cost:** FREE
**Best for:** Development, testing, experimentation

**Check status:**
```bash
python providers.py --check ollama
ollama list  # See installed models
```

---

### LM Studio

**Setup:**
```bash
# 1. Download from https://lmstudio.ai
# 2. Install and open LM Studio
# 3. Search and download a model (e.g., "llava")
# 4. Go to Developer → Start Server
# 5. Set as default
python providers.py --set-default lmstudio
```

**Models:** Any model you load in the GUI
**Cost:** FREE
**Best for:** GUI users, easy model switching

---

### vLLM

**Setup:**
```bash
# 1. Install vLLM
pip install vllm

# 2. Start server with a model
vllm serve facebook/opt-125m --api-key token-abc123

# 3. Set as default
python providers.py --set-default vllm
```

**Models:** Any HuggingFace model
**Cost:** FREE
**Best for:** High-throughput, production local deployment

---

## Usage Examples

### Check Cost Estimates

```bash
# Estimate cost for 10,000 tokens
python providers.py --estimate-cost openai 10000
# Output: $0.1500 for 10,000 tokens

python providers.py --estimate-cost ollama 10000
# Output: Free (local)
```

### Provider Health Checks

```bash
# Check if Ollama is running
python providers.py --check ollama

# Check all providers
python providers.py --list
```

### During Runtime

When you run Cradle, you'll see provider info:

```bash
$ python run.py skylines --llm ollama

============================================================
💻 LLM Provider Information
============================================================
Provider:     Ollama
Type:         Local
Cost:         Free
Model:        llama3.2-vision
Endpoint:     http://localhost:11434/v1
============================================================
```

For API providers, you'll see a cost warning:

```bash
$ python run.py skylines --llm openai

============================================================
🌐 LLM Provider Information
============================================================
Provider:     OpenAI
Type:         API
Cost:         Paid
Model:        gpt-4o-2024-05-13

⚠️  WARNING: This provider incurs API costs!
   Estimated: $10-50/hour depending on usage
   Consider using a local provider (ollama, lmstudio) for testing
============================================================
```

---

## Configuration Files

Each provider has a config file in `conf/`:

**conf/ollama_config.json**
```json
{
    "base_url": "http://localhost:11434/v1",
    "comp_model": "llama3.2-vision",
    "emb_model": "nomic-embed-text"
}
```

**conf/openai_config.json**
```json
{
    "key_var": "OA_OPENAI_KEY",
    "emb_model": "text-embedding-ada-002",
    "comp_model": "gpt-4o-2024-05-13",
    "is_azure": false
}
```

You can customize these for different models or endpoints.

---

## Switching Providers

### Method 1: Set Default

```bash
# Set once, use always
python providers.py --set-default ollama
python run.py skylines  # Uses ollama
```

### Method 2: Specify Each Time

```bash
# Override default for specific runs
python run.py skylines --llm openai
python run.py skylines --llm ollama
python run.py skylines --llm lmstudio
```

### Method 3: Interactive

```bash
# Pick from menu
python providers.py --select
```

---

## Recommended Workflow

**For Development/Testing:**
1. Use Ollama or LM Studio (free)
2. Test your tasks and prompts
3. Iterate quickly without cost

**For Production/Final Runs:**
1. Switch to OpenAI or Claude
2. Get highest quality results
3. Record results and costs

**Hybrid Approach:**
```bash
# Development
python run.py skylines --llm ollama

# Testing specific scenarios
python run.py skylines --llm lmstudio

# Final validation
python run.py skylines --llm openai
```

---

## Troubleshooting

### "Provider not available"

**For API providers:**
- Check .env file has the correct key
- Verify key is valid (not expired)
- Run `python setup.py --keys-only` to reconfigure

**For local providers:**
- Check server is running
- Verify correct port (11434 for Ollama, 1234 for LM Studio, 8000 for vLLM)
- Check models are loaded

### "Model not found"

**Ollama:**
```bash
ollama list  # See what's installed
ollama pull llama3.2-vision  # Pull if missing
```

**LM Studio:**
- Open LM Studio GUI
- Load a model (must be loaded, not just downloaded)
- Server → Start Server

**vLLM:**
- Restart server with correct model name
- Check vLLM logs for errors

### Provider shows as configured but fails

1. **Check connectivity:**
   ```bash
   # Ollama
   curl http://localhost:11434/api/tags

   # LM Studio
   curl http://localhost:1234/v1/models

   # vLLM
   curl http://localhost:8000/v1/models
   ```

2. **Check logs:**
   - Ollama: `journalctl -u ollama` (Linux) or Console.app (Mac)
   - LM Studio: Check GUI console
   - vLLM: Terminal output

3. **Restart server:**
   - Ollama: `systemctl restart ollama` (Linux)
   - LM Studio: Stop and restart in GUI
   - vLLM: Kill and restart command

---

## FAQ

**Q: Which provider should I use?**
A: For testing and development, use Ollama (free, good quality). For production or best results, use OpenAI or Claude.

**Q: Can I use multiple providers at once?**
A: Yes! You can run different games with different providers simultaneously.

**Q: Do I need all providers?**
A: No. Pick one or two that fit your needs. Ollama + OpenAI is a good combination.

**Q: How much GPU memory do local providers need?**
A: Vision models typically need 8-16GB VRAM. Smaller models (4-7B) can run on 6-8GB.

**Q: Can I run providers on a different machine?**
A: Yes! Edit the config file to point to a remote server:
```json
{
    "base_url": "http://192.168.1.100:11434/v1",
    ...
}
```

**Q: What if I don't have a GPU?**
A: CPU inference works but is very slow. Consider using API providers (OpenAI/Claude) instead.

---

*Last updated: 2025-11-15*
