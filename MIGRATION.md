# Migration Guide: OpenAI to xAI + Sentence Transformers

This guide documents the migration from OpenAI embeddings and chat to xAI chat and Sentence Transformers embeddings.

## Changes Made

### 1. Dependencies Updated
- **Removed**: `langchain-openai`, `openai`
- **Added**: `langchain-xai`, `sentence-transformers`, `torch`, `transformers`

### 2. Configuration Changes
- **Removed**: `OPENAI_API_KEY`
- **Added**: `XAI_API_KEY`
- **Updated**: `VECTOR_DIMENSIONS` from 1536 (OpenAI) to 384 (Sentence Transformers)
- **Updated**: `LLM_MODEL` from "gpt-4o-mini" to "grok-beta"
- **Added**: `EMBEDDING_MODEL` configuration

### 3. Code Changes

#### Document Handler (`app/handlers/document.py`)
- Replaced `OpenAIEmbeddings` with `SentenceTransformer`
- Updated embedding methods to use local Sentence Transformers
- Replaced `ChatOpenAI` with `ChatXAI`

#### Message Handler (`app/handlers/message.py`)
- Replaced `ChatOpenAI` with `ChatXAI`
- Updated import statements

#### Configuration (`app/config.py`)
- Added `XAI_API_KEY` and `EMBEDDING_MODEL` settings
- Updated vector dimensions

### 4. Environment Variables

#### Old Environment Variables
```env
OPENAI_API_KEY=your_openai_api_key
```

#### New Environment Variables
```env
XAI_API_KEY=your_xai_api_key
```

### 5. Docker Changes
- Updated Dockerfile to pre-download Sentence Transformers model
- Updated docker-compose files with new environment variable

## Migration Steps

1. **Update your `.env` file**:
   ```bash
   # Remove
   OPENAI_API_KEY=your_openai_api_key
   
   # Add
   XAI_API_KEY=your_xai_api_key
   ```

2. **Get xAI API Key**:
   - Visit [x.ai](https://x.ai/) to get your API key
   - Add it to your `.env` file

3. **Rebuild Docker image**:
   ```bash
   make docker-clean
   make docker-build
   make docker-run
   ```

## Benefits of Migration

### Sentence Transformers (Embeddings)
- ✅ **Cost**: Free, no API costs
- ✅ **Privacy**: Runs locally, no data sent to external APIs
- ✅ **Speed**: Fast inference after initial model download
- ✅ **Offline**: Works without internet connection
- ✅ **Consistency**: Deterministic results

### xAI (Chat/LLM)
- ✅ **Performance**: Access to Grok model
- ✅ **Cost**: Competitive pricing
- ✅ **Integration**: Native LangChain support

## Performance Considerations

### Embedding Model Comparison
| Model | Dimensions | Size | Performance | Use Case |
|-------|------------|------|-------------|----------|
| `all-MiniLM-L6-v2` | 384 | 90MB | Fast | General purpose |
| `all-mpnet-base-v2` | 768 | 420MB | Best | High quality needed |
| `paraphrase-multilingual-MiniLM-L12-v2` | 384 | 420MB | Good | Multilingual |

### Current Configuration
- **Model**: `all-MiniLM-L6-v2`
- **Dimensions**: 384
- **Trade-off**: Speed vs. Quality (optimized for speed)

## Troubleshooting

### Common Issues

1. **Model Download Fails**:
   ```bash
   # Pre-download manually
   docker run --rm -it your_image_name python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"
   ```

2. **xAI API Key Issues**:
   ```bash
   # Check if key is set
   echo $XAI_API_KEY
   ```

3. **Vector Dimension Mismatch**:
   - Clear MongoDB vector indexes if they exist
   - Ensure `VECTOR_DIMENSIONS=384` in config

### Rollback Process

If you need to rollback:

1. **Restore requirements.txt**:
   ```txt
   langchain-openai>=0.0.8
   openai==1.12.0
   ```

2. **Restore environment**:
   ```env
   OPENAI_API_KEY=your_openai_api_key
   ```

3. **Restore code imports and models in handlers**

## Performance Monitoring

### Memory Usage
- Sentence Transformers model: ~200MB RAM
- Expect initial startup delay for model loading

### Disk Space
- Model cache: ~100MB for `all-MiniLM-L6-v2`
- Located in: `/root/.cache/torch/sentence_transformers/`

### Network
- Initial download: ~100MB (one-time)
- Runtime: Only xAI API calls (no embedding API calls)

## Future Considerations

### Model Updates
To change embedding model:
1. Update `EMBEDDING_MODEL` in config
2. Update `VECTOR_DIMENSIONS` accordingly
3. Rebuild and restart services
4. Reprocess existing documents (if needed)

### Alternative Models
- **For better quality**: Use `all-mpnet-base-v2` (768 dims)
- **For multilingual**: Use `paraphrase-multilingual-MiniLM-L12-v2`
- **For domain-specific**: Consider fine-tuned models
