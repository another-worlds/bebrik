from typing import List, Dict, Any, Optional
import asyncio
import logging
import time
from abc import ABC, abstractmethod
import httpx
import json
import hashlib
from datetime import datetime

from ..config import (
    EMBEDDING_SERVICE,
    EMBEDDING_MODEL,
    HUGGINGFACE_API_KEY,
    EMBEDDING_BATCH_SIZE,
    EMBEDDING_MAX_RETRIES,
    EMBEDDING_TIMEOUT
)
from ..utils.logging import get_logger, log_async_performance

logger = get_logger('embedding_service')

class EmbeddingServiceBase(ABC):
    """Base class for embedding services"""
    
    @abstractmethod
    async def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for documents"""
        pass
    
    @abstractmethod
    async def embed_query(self, query: str) -> List[float]:
        """Generate embedding for query"""
        pass
    
    @property
    @abstractmethod
    def dimensions(self) -> int:
        """Get embedding dimensions"""
        pass

class HuggingFaceEmbeddingService(EmbeddingServiceBase):
    """
    HuggingFace Inference API embedding service
    
    Uses the feature-extraction pipeline to generate dense vector embeddings
    for similarity search and retrieval. This is different from the 
    sentence-similarity pipeline which returns similarity scores.
    
    API Endpoint: https://api-inference.huggingface.co/models/{model}
    Task: feature-extraction (generates embeddings)
    
    Input format: {"inputs": ["text1", "text2"], "options": {...}}
    Output format: [[emb1], [emb2]] - List of embedding vectors
    """
    
    def __init__(self, api_key: str, model: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.api_key = api_key
        self.model = model
        # Use the correct HuggingFace Inference API endpoint for feature extraction
        self.base_url = f"https://api-inference.huggingface.co/models/{self.model}"
        self._dimensions = self._get_model_dimensions(model)
        self.rate_limit_delay = 0.2  # 200ms between requests for stability
        self._client = None  # Lazy initialization
        
    def _get_model_dimensions(self, model: str) -> int:
        """Get embedding dimensions based on model name"""
        model_lower = model.lower()
        
        # Common model dimensions
        if "multilingual-e5-large" in model_lower:
            return 1024
        elif "multilingual-e5-base" in model_lower:
            return 768
        elif "multilingual-e5-small" in model_lower:
            return 384
        elif "all-minilm-l6-v2" in model_lower:
            return 384
        elif "all-minilm-l12-v2" in model_lower:
            return 384
        elif "all-mpnet-base-v2" in model_lower:
            return 768
        elif "large" in model_lower:
            return 1024
        elif "base" in model_lower:
            return 768
        else:
            return 1024  # Default for multilingual-e5-large
    
    @property
    def client(self) -> httpx.AsyncClient:
        """Get or create HTTP client with proper timeout settings"""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                timeout=httpx.Timeout(
                    connect=10.0,
                    read=EMBEDDING_TIMEOUT,
                    write=10.0,
                    pool=30.0
                ),
                limits=httpx.Limits(
                    max_keepalive_connections=5,
                    max_connections=10
                )
            )
        return self._client
        
    async def _make_request(self, payload: Dict[str, Any], retries: int = EMBEDDING_MAX_RETRIES) -> List[List[float]]:
        """
        Make API request with retry logic
        
        Uses HuggingFace Inference API feature-extraction endpoint:
        - Endpoint: https://api-inference.huggingface.co/models/{model}
        - Task: feature-extraction (not pipeline/sentence-similarity)
        - Returns: Dense vector embeddings for similarity search
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        for attempt in range(retries):
            try:
                response = await self.client.post(
                    self.base_url,  # Use direct model endpoint, not pipeline
                    headers=headers,
                    json=payload
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if isinstance(result, list) and len(result) > 0:
                        # Validate embeddings have correct dimensions
                        valid_embeddings = []
                        for i, embedding in enumerate(result):
                            if isinstance(embedding, list) and len(embedding) > 0:
                                # Ensure correct dimensions
                                if len(embedding) != self.dimensions:
                                    logger.warning(f"Unexpected embedding size: {len(embedding)}, expected {self.dimensions}")
                                    # Pad or truncate to expected size
                                    if len(embedding) < self.dimensions:
                                        embedding.extend([0.0] * (self.dimensions - len(embedding)))
                                    else:
                                        embedding = embedding[:self.dimensions]
                                valid_embeddings.append(embedding)
                            else:
                                logger.warning(f"Invalid embedding at index {i}")
                                valid_embeddings.append([0.0] * self.dimensions)
                        
                        logger.info(f"Successfully generated {len(valid_embeddings)} embeddings")
                        return valid_embeddings
                    else:
                        logger.error(f"Unexpected response format: {type(result)} - {result}")
                        return []
                        
                elif response.status_code == 503:
                    # Model loading, wait and retry
                    wait_time = 2 ** attempt
                    logger.warning(f"Model loading, waiting {wait_time}s before retry {attempt + 1}")
                    await asyncio.sleep(wait_time)
                    continue
                    
                elif response.status_code == 429:
                    # Rate limited, wait and retry
                    wait_time = 2 ** attempt
                    logger.warning(f"Rate limited, waiting {wait_time}s before retry {attempt + 1}")
                    await asyncio.sleep(wait_time)
                    continue
                    
                else:
                    logger.error(f"API request failed with status {response.status_code}: {response.text}")
                    if attempt == retries - 1:
                        return []
                    
            except Exception as e:
                logger.error(f"Request failed (attempt {attempt + 1}): {str(e)}")
                if attempt == retries - 1:
                    return []
                await asyncio.sleep(1)
        
        return []
    
    @log_async_performance("embedding_service")
    async def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for documents with batching and rate limiting"""
        if not texts:
            return []
        
        all_embeddings = []
        
        # Process in batches to respect rate limits
        for i in range(0, len(texts), EMBEDDING_BATCH_SIZE):
            batch = texts[i:i + EMBEDDING_BATCH_SIZE]
            
            try:
                # Add rate limiting delay
                if i > 0:
                    await asyncio.sleep(self.rate_limit_delay)
                
                # Prepare payload
                payload = {
                    "inputs": batch,
                    "options": {
                        "wait_for_model": True,
                        "use_cache": True
                    }
                }
                
                batch_embeddings = await self._make_request(payload)
                
                if batch_embeddings:
                    all_embeddings.extend(batch_embeddings)
                    logger.info(f"Generated embeddings for batch {i//EMBEDDING_BATCH_SIZE + 1}, {len(batch)} texts")
                else:
                    # Add zero embeddings for failed batch
                    zero_embedding = [0.0] * self.dimensions
                    all_embeddings.extend([zero_embedding] * len(batch))
                    logger.error(f"Failed to generate embeddings for batch {i//EMBEDDING_BATCH_SIZE + 1}")
                
            except Exception as e:
                logger.error(f"Error generating embeddings for batch {i//EMBEDDING_BATCH_SIZE + 1}: {str(e)}")
                # Add zero embeddings for failed batch
                zero_embedding = [0.0] * self.dimensions
                all_embeddings.extend([zero_embedding] * len(batch))
        
        return all_embeddings
    
    @log_async_performance("embedding_service")
    async def embed_query(self, query: str) -> List[float]:
        """Generate embedding for query"""
        try:
            payload = {
                "inputs": [query],
                "options": {
                    "wait_for_model": True,
                    "use_cache": True
                }
            }
            
            result = await self._make_request(payload)
            
            if result and len(result) > 0:
                return result[0]
            else:
                logger.error("Failed to generate query embedding")
                return [0.0] * self.dimensions
                
        except Exception as e:
            logger.error(f"Error generating query embedding: {str(e)}")
            return [0.0] * self.dimensions
    
    @property
    def dimensions(self) -> int:
        return self._dimensions
    
    async def close(self):
        """Close the HTTP client"""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            logger.info("HuggingFace embedding service client closed")

class LocalFallbackEmbeddingService(EmbeddingServiceBase):
    """Local fallback using simple text features (for emergencies)"""
    
    def __init__(self):
        self._dimensions = 300  # Simple feature vector size
    
    async def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Generate simple text-based embeddings"""
        embeddings = []
        for text in texts:
            embedding = self._simple_text_embedding(text)
            embeddings.append(embedding)
        return embeddings
    
    async def embed_query(self, query: str) -> List[float]:
        """Generate simple text-based embedding for query"""
        return self._simple_text_embedding(query)
    
    def _simple_text_embedding(self, text: str) -> List[float]:
        """Create a simple text embedding based on character and word features"""
        import hashlib
        
        # Normalize text
        text = text.lower().strip()
        
        # Create features based on text characteristics
        features = [0.0] * self._dimensions
        
        # Text length features
        features[0] = min(len(text) / 1000.0, 1.0)
        features[1] = len(text.split()) / 100.0
        
        # Character frequency features
        for i, char in enumerate(text[:50]):  # First 50 chars
            if i < 50:
                features[i + 2] = ord(char) / 255.0
        
        # Hash-based features for the remaining dimensions
        text_hash = hashlib.md5(text.encode()).digest()
        for i, byte in enumerate(text_hash):
            if i + 52 < self._dimensions:
                features[i + 52] = byte / 255.0
        
        # Word count features
        words = text.split()
        for i, word in enumerate(words[:100]):
            if i + 68 < self._dimensions:
                word_hash = hash(word) % 1000
                features[i + 68] = word_hash / 1000.0
        
        return features
    
    @property
    def dimensions(self) -> int:
        return self._dimensions

class EmbeddingServiceFactory:
    """Factory for creating embedding services"""
    
    @staticmethod
    def create_service(service_type: Optional[str] = None) -> EmbeddingServiceBase:
        """Create embedding service based on configuration"""
        service_type = service_type or EMBEDDING_SERVICE
        
        if service_type == "huggingface":
            if not HUGGINGFACE_API_KEY:
                logger.warning("HuggingFace API key not found, falling back to local service")
                return EmbeddingServiceFactory.create_service("local")
            return HuggingFaceEmbeddingService(HUGGINGFACE_API_KEY, EMBEDDING_MODEL)
        
        elif service_type == "local":
            return LocalFallbackEmbeddingService()
        
        else:
            logger.warning(f"Unknown embedding service: {service_type}, using HuggingFace")
            return EmbeddingServiceFactory.create_service("huggingface")

# Create singleton instance
embedding_service = EmbeddingServiceFactory.create_service()
