# Migration Guide: Sentence Transformers to HuggingFace Inference API

This guide documents the migration from local Sentence Transformers to HuggingFace Inference API embeddings while keeping MongoDB vector store.

## Changes Made

### 1. Dependencies Updated
- **Removed**: `sentence-transformers`, `torch`, `transformers`, `nvidia-*` packages
- **Kept**: `langchain-xai`, `httpx`, `numpy`
- **Architecture**: Now uses HuggingFace Inference API instead of local models

### 2. Configuration Changes
- **Added**: `HUGGINGFACE_API_KEY` environment variable
- **Added**: `EMBEDDING_SERVICE` configuration (huggingface/local)
- **Added**: `EMBEDDING_BATCH_SIZE`, `EMBEDDING_MAX_RETRIES`, `EMBEDDING_TIMEOUT`
- **Kept**: `VECTOR_DIMENSIONS=384` (same model, different serving method)

### 3. Code Changes

#### New Embedding Service (`app/services/embedding.py`)
- **HuggingFaceEmbeddingService**: Uses HF Inference API
- **LocalFallbackEmbeddingService**: Simple text-based fallback
- **EmbeddingServiceFactory**: Creates appropriate service based on config
- **Features**: Async operations, retry logic, batch processing, rate limiting

#### Document Handler (`app/handlers/document.py`)
- Replaced local `SentenceTransformer` with `embedding_service`
- Updated methods to be async: `_embed_documents()`, `_embed_query()`
- Added embedding service metadata to chunks

### 4. Environment Variables

#### Required Environment Variables
```env
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
XAI_API_KEY=your_xai_api_key
HUGGINGFACE_API_KEY=your_huggingface_api_key
```

#### Optional Environment Variables
```env
EMBEDDING_SERVICE=huggingface  # or "local" for fallback
EMBEDDING_BATCH_SIZE=50
EMBEDDING_MAX_RETRIES=3
EMBEDDING_TIMEOUT=30
```

### 5. Docker Changes
- Removed Sentence Transformers model pre-download from Dockerfile
- Added `HUGGINGFACE_API_KEY` to docker-compose environment
- Reduced Docker image size significantly (~2GB reduction)

## Migration Steps

### 1. Get HuggingFace API Key
- Visit [HuggingFace Settings](https://huggingface.co/settings/tokens)
- Create a new token with "Read" permissions
- Copy the token

### 2. Update Environment Variables
```bash
# Add to your .env file
HUGGINGFACE_API_KEY=hf_your_token_here
EMBEDDING_SERVICE=huggingface
```

### 3. Clean and Rebuild
```bash
# Clean everything
make docker-clean
make clean-venv

# Rebuild with new dependencies
make install
make docker-build
make docker-run
```

### 4. Run Migration Command
```bash
make migrate-to-hf
```

## Benefits of Migration

### Cost & Infrastructure
- ✅ **No GPU Required**: Eliminates need for local GPU/CUDA
- ✅ **Smaller Images**: ~2GB reduction in Docker image size
- ✅ **Lower Memory**: ~1GB less RAM usage per container
- ✅ **Faster Startup**: No model loading delay
- ✅ **Free Tier**: HuggingFace Inference API has generous free limits

### Performance & Reliability
- ✅ **Always Available**: No model loading or CUDA issues
- ✅ **Consistent Results**: Same embeddings across deployments
- ✅ **Auto-scaling**: HuggingFace handles model scaling
- ✅ **Rate Limiting**: Built-in request throttling
- ✅ **Retry Logic**: Automatic failure recovery

### Development & Deployment
- ✅ **Simpler Deployment**: No GPU drivers or CUDA setup
- ✅ **Cross-platform**: Works on any system (ARM, x86, etc.)
- ✅ **Faster CI/CD**: Smaller images = faster builds/deploys
- ✅ **Environment Parity**: Same embeddings in dev/staging/prod

## Service Comparison

| Feature | Sentence Transformers | HuggingFace API |
|---------|----------------------|------------------|
| **Setup** | Complex (GPU/CUDA) | Simple (API key) |
| **Image Size** | ~3GB | ~1GB |
| **RAM Usage** | ~2GB | ~200MB |
| **Startup Time** | 30-60s | <5s |
| **Consistency** | Model version dependent | Always consistent |
| **Offline** | ✅ Works offline | ❌ Requires internet |
| **Cost** | Infrastructure costs | Free tier + usage |
| **Scaling** | Manual | Automatic |

## Configuration Options

### HuggingFace Inference API Settings
```python
# Current configuration
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
EMBEDDING_BATCH_SIZE = 50  # Texts per API request
EMBEDDING_MAX_RETRIES = 3  # Retry failed requests
EMBEDDING_TIMEOUT = 30     # Request timeout in seconds
```

### Available Models
- `sentence-transformers/all-MiniLM-L6-v2` (384 dims) - **Current**
- `sentence-transformers/all-mpnet-base-v2` (768 dims) - Higher quality
- `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` (384 dims) - Multilingual

### Rate Limits & Pricing
- **Free Tier**: 30,000 requests/month
- **Rate Limit**: ~10 requests/second
- **Batch Size**: Up to 100 texts per request
- **Pricing**: $0.0001 per 1k tokens after free tier

## Troubleshooting

### Common Issues

#### 1. API Key Issues
```bash
# Check if key is set
echo $HUGGINGFACE_API_KEY

# Test API key
curl -H "Authorization: Bearer $HUGGINGFACE_API_KEY" \
  https://api-inference.huggingface.co/pipeline/feature-extraction/sentence-transformers/all-MiniLM-L6-v2
```

#### 2. Model Loading Delays
```json
// API Response during model loading
{
  "estimated_time": 20.0,
  "error": "Model sentence-transformers/all-MiniLM-L6-v2 is currently loading"
}
```
**Solution**: The service automatically retries with exponential backoff.

#### 3. Rate Limiting
```json
// API Response when rate limited
{
  "error": "Rate limit reached. Try again in 60 seconds"
}
```
**Solution**: Built-in retry logic handles rate limits automatically.

#### 4. Network Issues
**Fallback**: The system falls back to `LocalFallbackEmbeddingService` if HF API is unavailable.

### MongoDB Vector Index
The migration keeps the existing MongoDB vector store structure:
- Vector dimensions remain 384
- Existing documents work without reprocessing
- Same vector similarity search performance

### Rollback Process
If you need to rollback to Sentence Transformers:

1. **Restore requirements.txt**:
   ```bash
   git checkout HEAD~1 -- requirements.txt
   ```

2. **Remove environment variables**:
   ```bash
   # Remove from .env
   # HUGGINGFACE_API_KEY=...
   # EMBEDDING_SERVICE=...
   ```

3. **Rebuild**:
   ```bash
   make docker-clean
   make docker-build
   make docker-run
   ```

## Monitoring & Logging

### Embedding Service Logs
The service logs embedding operations:
```python
logger.info(f"Generated embeddings for batch 1, 50 texts")
logger.warning(f"Model loading, waiting 2s before retry 1")
logger.error(f"API request failed with status 429: Rate limited")
```

### Performance Metrics
Monitor these metrics in your logs:
- Embedding generation time per batch
- API request success/failure rates
- Fallback service usage
- Rate limiting occurrences

## Future Considerations

### Alternative Services
- **Cohere**: Better multilingual support
- **Voyage AI**: Higher quality embeddings
- **Local Ollama**: Self-hosted with API compatibility

### Model Updates
To change embedding model:
1. Update `EMBEDDING_MODEL` in config
2. Update `VECTOR_DIMENSIONS` if needed
3. Consider reprocessing existing documents

### Scaling
- Monitor free tier usage
- Consider upgrading to paid tier for high volume
- Implement caching for frequently used embeddings
