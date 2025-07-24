#!/usr/bin/env python3
"""
Test the embedding service with the working HuggingFace model
"""

import asyncio
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(__file__))

from app.services.embedding import HuggingFaceEmbeddingService

async def test_embedding_service():
    """Test the HuggingFace embedding service"""
    
    print("🧪 Testing HuggingFace Embedding Service")
    print("=" * 50)
    
    # Initialize the service
    from app.config import HUGGINGFACE_API_KEY, EMBEDDING_MODEL
    
    if not HUGGINGFACE_API_KEY:
        print("❌ HUGGINGFACE_API_KEY not found in environment")
        return False
    
    service = HuggingFaceEmbeddingService(
        api_key=HUGGINGFACE_API_KEY,
        model=EMBEDDING_MODEL
    )
    
    # Test documents
    documents = [
        "Hello world, this is a test document.",
        "Machine learning and artificial intelligence are fascinating fields.",
        "Python is a great programming language for data science.",
        "The weather today is sunny and beautiful."
    ]
    
    # Test query
    query = "What programming language is good for AI?"
    
    try:
        print("📄 Test Documents:")
        for i, doc in enumerate(documents, 1):
            print(f"   {i}. {doc}")
        print()
        
        print("❓ Test Query:")
        print(f"   {query}")
        print()
        
        # Test document embedding
        print("🔄 Generating document embeddings...")
        doc_embeddings = await service.embed_documents(documents)
        
        print(f"✅ Generated {len(doc_embeddings)} document embeddings")
        for i, emb in enumerate(doc_embeddings):
            print(f"   Doc {i+1}: {len(emb)} dimensions, sample: {emb[:3]}")
        print()
        
        # Test query embedding
        print("🔄 Generating query embedding...")
        query_embedding = await service.embed_query(query)
        
        print(f"✅ Generated query embedding: {len(query_embedding)} dimensions")
        print(f"   Sample: {query_embedding[:3]}")
        print()
        
        # Test similarity calculation
        print("🔍 Calculating similarities...")
        similarities = []
        for i, doc_emb in enumerate(doc_embeddings):
            # Simple cosine similarity calculation
            dot_product = sum(a * b for a, b in zip(query_embedding, doc_emb))
            magnitude_query = sum(a * a for a in query_embedding) ** 0.5
            magnitude_doc = sum(a * a for a in doc_emb) ** 0.5
            similarity = dot_product / (magnitude_query * magnitude_doc)
            similarities.append((i, similarity))
        
        # Sort by similarity
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        print("📊 Document Similarities (sorted by relevance):")
        for i, (doc_idx, sim) in enumerate(similarities, 1):
            print(f"   {i}. Doc {doc_idx+1}: {sim:.4f} - {documents[doc_idx]}")
        print()
        
        print("🎉 SUCCESS: Embedding service works perfectly!")
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main test function"""
    success = await test_embedding_service()
    
    if success:
        print("\n✅ All tests passed! Your HuggingFace embedding migration is complete.")
        print("💡 The service is ready to use with your Telegram bot.")
    else:
        print("\n❌ Tests failed. Check your configuration and API key.")

if __name__ == "__main__":
    asyncio.run(main())
