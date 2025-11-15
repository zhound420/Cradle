# Local LLM Setup Guide

This guide explains how to use **Ollama** or **LM Studio** as free, local alternatives to OpenAI/Claude APIs.

## Why Use Local LLMs?

✅ **Free**: No API costs
✅ **Privacy**: Data stays on your machine
✅ **Speed**: No network latency (with good GPU)
✅ **Experimentation**: Try multiple models easily

⚠️ **Requirements**:
- GPU with 8GB+ VRAM recommended (for vision models)
- 10-50GB disk space per model
- Models may not perform as well as GPT-4o/Claude

---

## Option 1: Ollama (Recommended)

### Installation

1. **Download Ollama**
   - Visit: https://ollama.com
   - Download for your OS (Windows, Mac, Linux)
   - Install (server starts automatically)

2. **Pull a Vision Model**
   ```bash
   # Recommended for games (needs vision)
   ollama pull llama3.2-vision  # 11GB

   # Alternative (smaller)
   ollama pull llava  # 4.7GB

   # For embeddings
   ollama pull nomic-embed-text  # 274MB
   ```

3. **Verify Installation**
   ```bash
   ollama list  # See installed models
   curl http://localhost:11434/api/tags  # Check server
   ```

### Using with Cradle

```bash
# Run any game/app with Ollama
python run.py skylines --llm ollama
python run.py rdr2-story --llm ollama
python run.py outlook --llm ollama
```

### Configuration

Edit `conf/ollama_config.json` if needed:
```json
{
    "base_url": "http://localhost:11434/v1",
    "comp_model": "llama3.2-vision",
    "emb_model": "nomic-embed-text"
}
```

---

## Option 2: LM Studio

### Installation

1. **Download LM Studio**
   - Visit: https://lmstudio.ai
   - Download for your OS
   - Install and open

2. **Download a Model**
   - Click "Search" in LM Studio
   - Search for "llava" or "vision"
   - Download a model (e.g., `llava-v1.6-mistral-7b`)

3. **Start Server**
   - Go to "Developer" tab
   - Click "Start Server"
   - Server runs on http://localhost:1234

### Using with Cradle

```bash
# Run any game/app with LM Studio
python run.py skylines --llm lmstudio
python run.py rdr2-story --llm lmstudio
```

### Configuration

Edit `conf/lmstudio_config.json` if needed:
```json
{
    "base_url": "http://localhost:1234/v1",
    "comp_model": "local-model",
    "emb_model": "nomic-embed-text"
}
```

---

## Recommended Models

### For Games (Need Vision)

| Model | Size | Speed | Quality | Notes |
|-------|------|-------|---------|-------|
| **llama3.2-vision** | 11GB | Medium | Best | Recommended |
| **llava-1.6** | 7GB | Fast | Good | Good balance |
| **bakllava** | 5GB | Fast | OK | Faster, less accurate |

### For Software (Text-Only)

| Model | Size | Speed | Quality |
|-------|------|-------|---------|
| **mistral** | 4GB | Very Fast | Good |
| **llama3** | 7GB | Fast | Better |
| **mixtral** | 26GB | Slow | Best |

### For Embeddings

| Model | Size | Notes |
|-------|------|-------|
| **nomic-embed-text** | 274MB | Recommended |
| **mxbai-embed-large** | 669MB | Better quality |

---

## Testing Your Setup

### 1. Check Server Status
```bash
# Ollama
curl http://localhost:11434/api/tags

# LM Studio
curl http://localhost:1234/v1/models
```

### 2. Test with Cradle
```bash
# Validate setup
python validate.py

# Dry run to see config
python run.py skylines --llm ollama --dry-run

# Actually run
python run.py skylines --llm ollama
```

### 3. Use Detection Script
```bash
python scripts/common/local_llm.py
```

---

## Performance Comparison

Based on community testing:

| Provider | Cost/Hour | Speed | Quality | Setup |
|----------|-----------|-------|---------|-------|
| GPT-4o | $10-40 | Fast | ⭐⭐⭐⭐⭐ | Easy |
| Claude 3.5 | $15-50 | Fast | ⭐⭐⭐⭐⭐ | Easy |
| Ollama (llama3.2-vision) | $0 | Medium | ⭐⭐⭐⭐ | Medium |
| LM Studio (llava) | $0 | Medium | ⭐⭐⭐ | Medium |

---

## Troubleshooting

### Ollama Issues

**Problem**: "Ollama not running"
**Solution**:
```bash
# Start Ollama manually
ollama serve

# Or restart service
# Linux: systemctl restart ollama
# Mac: Check Activity Monitor
# Windows: Check Services
```

**Problem**: "Model not found"
**Solution**:
```bash
ollama list  # Check installed models
ollama pull llama3.2-vision  # Pull if missing
```

### LM Studio Issues

**Problem**: "Server not running"
**Solution**:
- Open LM Studio GUI
- Go to Developer → Start Server
- Keep LM Studio open while using Cradle

**Problem**: "No models loaded"
**Solution**:
- Load a model in LM Studio GUI first
- Models must be loaded (green indicator)

### Performance Issues

**Problem**: Very slow responses
**Solutions**:
- Use smaller model (llava instead of llama3.2-vision)
- Check GPU is being used (not CPU)
- Close other GPU-intensive applications
- Increase GPU allocation in LM Studio settings

**Problem**: Out of memory
**Solutions**:
- Use smaller model
- Reduce context length in config
- Close other applications

---

## Advanced Usage

### Custom Endpoints

If running on different ports:

**Ollama on custom port:**
```json
{
    "base_url": "http://localhost:8080/v1",
    "comp_model": "llama3.2-vision"
}
```

**Remote server:**
```json
{
    "base_url": "http://192.168.1.100:11434/v1",
    "comp_model": "llama3.2-vision"
}
```

### Multiple Models

Create custom configs for different models:

`conf/ollama_fast_config.json`:
```json
{
    "base_url": "http://localhost:11434/v1",
    "comp_model": "llava",  // Faster model
    "emb_model": "nomic-embed-text"
}
```

Then add to `run.py` LLM_CONFIGS.

### Hybrid Setup

Use local LLM for cheap tasks, API for important ones:

```bash
# Development/testing with Ollama
python run.py skylines --llm ollama

# Final runs with GPT-4o
python run.py skylines --llm openai
```

---

## FAQ

**Q: Can I use CPU instead of GPU?**
A: Yes, but it will be much slower. Not recommended for real-time games.

**Q: Which is better, Ollama or LM Studio?**
A:
- Ollama: Better for CLI users, simpler, more automated
- LM Studio: Better GUI, easier to try different models, more control

**Q: Can I use both at the same time?**
A: Yes! They run on different ports (11434 vs 1234).

**Q: Do I need internet?**
A: Only to download models initially. After that, fully offline.

**Q: Can I use other models?**
A: Yes! Any model compatible with OpenAI API format works.

---

## Resources

- **Ollama**: https://ollama.com
- **LM Studio**: https://lmstudio.ai
- **Model Library**: https://ollama.com/library
- **Hugging Face**: https://huggingface.co/models (for LM Studio)

---

*Last updated: 2025-11-15*
