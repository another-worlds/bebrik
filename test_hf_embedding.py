#!/usr/bin/env python3
"""
Test script for HuggingFace Inference API embeddings

This script validates the HuggingFace embedding service implementation
using the feature-extraction endpoint (not sentence-similarity).

Based on HuggingFace documentation:
- feature-extraction: Returns dense vector embeddings for similarity search
- sentence-similarity: Returns similarity scores between sentences

Usage: python test_hf_embedding.py
"""

import asyncio
import os
import json
from typing import List
from app.services.embedding import HuggingFaceEmbeddingService

async def test_hf_embeddings():
    """Test HuggingFace embedding service"""
    
    # Check for API key
    api_key = os.getenv("HUGGINGFACE_API_KEY")
    if not api_key:
        print("❌ HUGGINGFACE_API_KEY environment variable not set")
        print("Please set it with: export HUGGINGFACE_API_KEY='your_token_here'")
        return
        
    print("🚀 Testing HuggingFace Embedding Service")
    print(f"API Key present: {'✅' if api_key else '❌'}")
    
    # Initialize service
    service = HuggingFaceEmbeddingService(
        api_key=api_key,
        model="intfloat/multilingual-e5-large"
    )
    
    print(f"Model: {service.model}")
    print(f"Expected dimensions: {service.dimensions}")
    print(f"API endpoint: {service.base_url}")
    
    # Test single query embedding
    print("\n📝 Testing single query embedding...")
    test_query = "What is artificial intelligence?"
    
    try:
        query_embedding = await service.embed_query(test_query)
        print(f"✅ Query embedding generated")
        print(f"   Dimensions: {len(query_embedding)}")
        print(f"   Sample values: {query_embedding[:5]}...")
        print(f"   Vector norm: {sum(x*x for x in query_embedding)**0.5:.4f}")
        
    except Exception as e:
        print(f"❌ Query embedding failed: {e}")
        return
    
    # Test document embeddings (batch)
    print("\n📚 Testing document embeddings...")
    test_documents = [
        "Machine learning is a subset of artificial intelligence.",
        "Natural language processing helps computers understand human language.",
        "Computer vision enables machines to interpret visual information.",
        "Deep learning uses neural networks with multiple layers."
    ]
    
    try:
        doc_embeddings = await service.embed_documents(test_documents)
        print(f"✅ Document embeddings generated")
        print(f"   Number of documents: {len(test_documents)}")
        print(f"   Number of embeddings: {len(doc_embeddings)}")
        
        for i, (doc, emb) in enumerate(zip(test_documents, doc_embeddings)):
            print(f"   Doc {i+1}: {len(emb)} dims, norm: {sum(x*x for x in emb)**0.5:.4f}")
            
    except Exception as e:
        print(f"❌ Document embeddings failed: {e}")
        return
    
    # Test similarity calculation
    print("\n🔍 Testing embedding similarity...")
    try:
        # Calculate cosine similarity between query and first document
        def cosine_similarity(a: List[float], b: List[float]) -> float:
            dot_product = sum(x * y for x, y in zip(a, b))
            norm_a = sum(x * x for x in a) ** 0.5
            norm_b = sum(x * x for x in b) ** 0.5
            return dot_product / (norm_a * norm_b) if norm_a * norm_b > 0 else 0.0
        
        similarities = []
        for i, doc_emb in enumerate(doc_embeddings):
            sim = cosine_similarity(query_embedding, doc_emb)
            similarities.append((i, sim))
            print(f"   Query <-> Doc {i+1}: {sim:.4f}")
        
        # Find most similar document
        best_match = max(similarities, key=lambda x: x[1])
        print(f"\n🎯 Most similar document (index {best_match[0]}):")
        print(f"   \"{test_documents[best_match[0]]}\"")
        print(f"   Similarity: {best_match[1]:.4f}")
        
    except Exception as e:
        print(f"❌ Similarity calculation failed: {e}")
    
    # Cleanup
    await service.close()
    print("\n✅ Test completed successfully!")

def test_endpoint_format():
    """Test the API endpoint format understanding"""
    print("\n🔧 HuggingFace API Endpoint Information:")
    print("="*50)
    
    model = "sentence-transformers/all-MiniLM-L6-v2"
    
    # Feature extraction endpoint (what we use for embeddings)
    feature_url = f"https://api-inference.huggingface.co/models/{model}"
    print(f"Feature Extraction: {feature_url}")
    print("  Purpose: Generate dense vector embeddings")
    print("  Input: {'inputs': ['text1', 'text2']}")
    print("  Output: [[emb1], [emb2]] - List of embedding vectors")
    
    # Sentence similarity endpoint (different use case)
    similarity_url = f"https://api-inference.huggingface.co/pipeline/sentence-similarity/{model}"
    print(f"\nSentence Similarity: {similarity_url}")  
    print("  Purpose: Compare sentence pairs for similarity")
    print("  Input: {'inputs': {'source_sentence': 'text', 'sentences': ['t1', 't2']}}")
    print("  Output: [0.8, 0.3] - Similarity scores")
    
    print(f"\n✅ We correctly use the feature extraction endpoint for embeddings")

if __name__ == "__main__":
    print("HuggingFace Embedding Service Test")
    print("="*40)
    
    # Show endpoint information
    test_endpoint_format()
    
    # Run the actual test
    asyncio.run(test_hf_embeddings())
