#!/usr/bin/env python3
"""Quick test of HuggingFace embedding API"""

import asyncio
import os
import httpx
import json
from dotenv import load_dotenv

load_dotenv()

async def quick_test():
    api_key = os.getenv("HUGGINGFACE_API_KEY")
    if not api_key:
        print("❌ No API key")
        return
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    url = "https://api-inference.huggingface.co/models/intfloat/e5-large-v2"
    payload = {"inputs": ["Hello world"]}
    
    print("🧪 Quick test...")
    print(f"URL: {url}")
    print(f"Payload: {payload}")
    
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(url, headers=headers, json=payload)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Success! Got {len(result)} embeddings")
                if len(result) > 0:
                    print(f"First embedding: {len(result[0])} dimensions")
                    print(f"Sample: {result[0][:5]}")
            else:
                print(f"❌ Error: {response.text}")
                
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    asyncio.run(quick_test())
