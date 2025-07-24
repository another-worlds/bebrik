#!/usr/bin/env python3
"""
Direct HuggingFace API Test - Feature Extraction vs Sentence Similarity
"""

import asyncio
import os
import httpx
import json
from dotenv import load_dotenv

load_dotenv()

async def test_feature_extraction_direct():
    """Test the feature extraction endpoint directly"""
    
    api_key = os.getenv("HUGGINGFACE_API_KEY")
    if not api_key:
        print("❌ HUGGINGFACE_API_KEY not found")
        return
    
    print("🧪 Testing Direct Feature Extraction API")
    print("=" * 50)
    
    # Test different models that support feature extraction
    models_to_test = [
        "thenlper/gte-large",  # Recommended by HF docs
        "intfloat/multilingual-e5-large",  # Used in HF examples
        "intfloat/e5-large-v2",  # Popular alternative
        "sentence-transformers/all-MiniLM-L6-v2"  # Our target model
    ]
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Simple texts to embed
    texts = ["Hello world", "This is a test", "Machine learning rocks"]
    
    for model in models_to_test:
        print(f"\n🔬 Testing model: {model}")
        print("-" * 60)
        
        url = f"https://api-inference.huggingface.co/models/{model}"
        
        # Try the simplest format first
        payload = {
            "inputs": texts
        }
        
        try:
            async with httpx.AsyncClient(timeout=60) as client:
                print(f"🔗 URL: {url}")
                print(f"📤 Sending: {json.dumps(payload, indent=2)}")
                
                response = await client.post(url, headers=headers, json=payload)
                
                print(f"\n📥 Status: {response.status_code}")
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"✅ Success! Response type: {type(result)}")
                    
                    if isinstance(result, list):
                        if len(result) > 0 and isinstance(result[0], list):
                            # This is embeddings format [[emb1], [emb2]]
                            print(f"📊 Got {len(result)} embeddings")
                            
                            for i, emb in enumerate(result):
                                if isinstance(emb, list):
                                    print(f"   Text {i}: '{texts[i]}'")
                                    print(f"   Embedding: {len(emb)} dimensions")
                                    print(f"   Sample: {emb[:5]}")
                                    print()
                                else:
                                    print(f"   ❌ Invalid embedding {i}: {type(emb)}")
                            
                            print(f"🎉 SUCCESS: {model} works for feature extraction!")
                            return True, model
                        elif len(result) > 0 and isinstance(result[0], (int, float)):
                            # This might be similarity scores
                            print(f"⚠️  Got similarity scores instead of embeddings: {result}")
                        else:
                            print(f"❌ Unexpected response format: {result}")
                    else:
                        print(f"❌ Unexpected response type: {type(result)}")
                        print(f"Response: {result}")
                
                elif response.status_code == 503:
                    print("⏳ Model is loading... This might take a moment")
                    print("Response:", response.text)
                
                else:
                    print(f"❌ Failed with status {response.status_code}")
                    print("Response:", response.text)
                    
        except Exception as e:
            print(f"❌ Exception: {str(e)}")
    
    print("\n❌ No working models found for feature extraction")
    return False, None

async def test_sentence_similarity_comparison():
    """Test sentence similarity endpoint for comparison"""
    
    api_key = os.getenv("HUGGINGFACE_API_KEY")
    if not api_key:
        return
    
    print("\n🔍 Testing Sentence Similarity (for comparison)")
    print("=" * 50)
    
    # Your example URL structure
    url = "https://api-inference.huggingface.co/models/sentence-transformers/all-MiniLM-L6-v2"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Sentence similarity payload format
    payload = {
        "inputs": {
            "source_sentence": "That is a happy person",
            "sentences": [
                "That is a happy dog",
                "That is a very happy person",
                "Today is a sunny day"
            ]
        }
    }
    
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            print(f"🔗 URL: {url}")
            print(f"📤 Sending: {json.dumps(payload, indent=2)}")
            
            response = await client.post(url, headers=headers, json=payload)
            
            print(f"\n📥 Status: {response.status_code}")
            print(f"Response: {response.text}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Similarity scores: {result}")
                return True
            else:
                return False
                
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False

async def main():
    """Run tests"""
    
    print("🚀 HuggingFace API Endpoint Test")
    print("=" * 60)
    
    if not os.getenv("HUGGINGFACE_API_KEY"):
        print("❌ Missing HUGGINGFACE_API_KEY")
        print("Get it from: https://huggingface.co/settings/tokens")
        return
    
    # Test feature extraction (what we need for embeddings)
    feature_result = await test_feature_extraction_direct()
    
    # Test sentence similarity (for comparison)
    similarity_result = await test_sentence_similarity_comparison()
    
    print("\n" + "=" * 60)
    print("📊 RESULTS")
    print("=" * 60)
    
    if isinstance(feature_result, tuple) and feature_result[0]:
        working_model = feature_result[1]
        print(f"Feature Extraction (embeddings): ✅ WORKS with {working_model}")
    else:
        print("Feature Extraction (embeddings): ❌ FAILED")
        
    print(f"Sentence Similarity (scores): {'✅ WORKS' if similarity_result else '❌ FAILED'}")
    print()
    
    if isinstance(feature_result, tuple) and feature_result[0]:
        working_model = feature_result[1]
        print("🎉 Feature extraction works! This is what we need for document retrieval.")
        print(f"💡 Recommendation: Update your config to use: {working_model}")
    else:
        print("⚠️  Feature extraction failed. Check your API key and try again.")

if __name__ == "__main__":
    asyncio.run(main())
