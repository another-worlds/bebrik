#!/usr/bin/env python3
"""
Simple test of the embedding service
"""

import asyncio
import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from app.config import HUGGINGFACE_API_KEY, EMBEDDING_MODEL
from app.services.embedding import HuggingFaceEmbeddingService

async def simple_test():
    print(f"🔧 API Key present: {'✅' if HUGGINGFACE_API_KEY else '❌'}")
    print(f"🤖 Model: {EMBEDDING_MODEL}")
    
    service = HuggingFaceEmbeddingService(
        api_key=HUGGINGFACE_API_KEY,
        model=EMBEDDING_MODEL
    )
    
    print("🧪 Testing single document...")
    try:
        result = await service.embed_documents(["Hello world"])
        print(f"✅ Success! Got embedding with {len(result[0])} dimensions")
        print(f"Sample: {result[0][:5]}")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(simple_test())
