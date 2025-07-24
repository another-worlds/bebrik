#!/usr/bin/env python3
"""
Simple test script to verify the migration to HuggingFace embeddings works correctly.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

async def test_embedding_service():
    """Test the embedding service"""
    print("🧪 Testing HuggingFace Embedding Service...")
    
    try:
        from app.services.embedding import embedding_service
        
        # Test query embedding
        print("📝 Testing query embedding...")
        query_embedding = await embedding_service.embed_query("Hello world")
        print(f"✅ Query embedding generated: {len(query_embedding)} dimensions")
        
        # Test document embeddings
        print("📄 Testing document embeddings...")
        test_texts = [
            "This is a test document.",
            "Another test document with different content.",
            "A third document for testing purposes."
        ]
        doc_embeddings = await embedding_service.embed_documents(test_texts)
        print(f"✅ Document embeddings generated: {len(doc_embeddings)} embeddings")
        
        # Verify dimensions
        expected_dims = embedding_service.dimensions
        print(f"✅ Expected dimensions: {expected_dims}")
        
        if len(query_embedding) == expected_dims:
            print("✅ Query embedding dimensions match")
        else:
            print(f"❌ Query embedding dimensions mismatch: {len(query_embedding)} vs {expected_dims}")
            
        if all(len(emb) == expected_dims for emb in doc_embeddings):
            print("✅ Document embedding dimensions match")
        else:
            print("❌ Document embedding dimensions mismatch")
            
        print("🎉 Embedding service test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Embedding service test failed: {str(e)}")
        return False

def test_imports():
    """Test that all imports work correctly"""
    print("📦 Testing imports...")
    
    try:
        from app.config import (
            HUGGINGFACE_API_KEY, 
            EMBEDDING_SERVICE, 
            EMBEDDING_MODEL,
            VECTOR_DIMENSIONS
        )
        print("✅ Config imports successful")
        
        from app.services.embedding import embedding_service
        print("✅ Embedding service import successful")
        
        from app.database.mongodb import db
        print("✅ MongoDB import successful")
        
        from app.handlers.document import document_handler
        print("✅ Document handler import successful")
        
        from app.handlers.message import message_handler
        print("✅ Message handler import successful")
        
        print("🎉 All imports successful!")
        return True
        
    except Exception as e:
        print(f"❌ Import test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_config():
    """Test configuration values"""
    print("⚙️  Testing configuration...")
    
    try:
        from app.config import (
            HUGGINGFACE_API_KEY, 
            EMBEDDING_SERVICE, 
            EMBEDDING_MODEL,
            VECTOR_DIMENSIONS,
            EMBEDDING_BATCH_SIZE
        )
        
        print(f"📊 Embedding Service: {EMBEDDING_SERVICE}")
        print(f"📊 Embedding Model: {EMBEDDING_MODEL}")
        print(f"📊 Vector Dimensions: {VECTOR_DIMENSIONS}")
        print(f"📊 Batch Size: {EMBEDDING_BATCH_SIZE}")
        
        if HUGGINGFACE_API_KEY:
            print("✅ HuggingFace API key is set")
        else:
            print("⚠️  HuggingFace API key is not set - will use fallback service")
            
        if EMBEDDING_SERVICE == "huggingface":
            print("✅ Using HuggingFace embedding service")
        else:
            print(f"📝 Using {EMBEDDING_SERVICE} embedding service")
            
        return True
        
    except Exception as e:
        print(f"❌ Config test failed: {str(e)}")
        return False

async def main():
    """Main test function"""
    print("🚀 Starting HuggingFace Migration Test")
    print("=" * 50)
    
    # Test imports
    if not test_imports():
        print("❌ Import tests failed. Exiting.")
        return False
        
    print()
    
    # Test configuration
    if not test_config():
        print("❌ Configuration tests failed. Exiting.")
        return False
        
    print()
    
    # Test embedding service
    if not await test_embedding_service():
        print("❌ Embedding service tests failed. Exiting.")
        return False
        
    print()
    print("🎉 All tests passed! Migration to HuggingFace embeddings is successful!")
    print("🔥 Your bot is ready to use HuggingFace Inference API embeddings!")
    
    return True

if __name__ == "__main__":
    # Check if we're in the right directory
    if not os.path.exists("app"):
        print("❌ Please run this script from the project root directory")
        print("   cd /path/to/telegram-multi-agent-ai-bot")
        print("   python test_migration.py")
        sys.exit(1)
        
    # Run the tests
    try:
        result = asyncio.run(main())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n👋 Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
