#!/usr/bin/env python3
"""
Docker health check script - verifies the bot and embedding service are working
"""

import os
import sys
import httpx
import asyncio
from datetime import datetime

async def health_check():
    """Simple health check for the embedding service"""
    try:
        # Check if required environment variables are present
        required_vars = ['HUGGINGFACE_API_KEY', 'TELEGRAM_BOT_TOKEN']
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        if missing_vars:
            print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
            return False
        
        # Simple connectivity test to HuggingFace
        api_key = os.getenv("HUGGINGFACE_API_KEY")
        model = os.getenv("EMBEDDING_MODEL", "intfloat/multilingual-e5-large")
        
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(
                f"https://api-inference.huggingface.co/models/{model}",
                headers={"Authorization": f"Bearer {api_key}"},
                json={"inputs": ["health check"]},
            )
            
            if response.status_code in [200, 503]:  # 503 means model is loading, which is OK
                print(f"✅ Health check passed at {datetime.now()}")
                return True
            else:
                print(f"❌ HuggingFace API error: {response.status_code}")
                return False
                
    except Exception as e:
        print(f"❌ Health check failed: {str(e)}")
        return False

if __name__ == "__main__":
    result = asyncio.run(health_check())
    sys.exit(0 if result else 1)
