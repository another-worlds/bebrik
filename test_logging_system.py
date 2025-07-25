#!/usr/bin/env python3
"""
Test script to verify the elaborate logging system implementation
"""

import asyncio
import sys
import os

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '.'))

from app.utils.logging import setup_logging
from app.utils.logging import document_logger, message_logger, embedding_logger, db_logger
from app.utils.logging import performance_logger  # Import the decorator separately

def test_logging_system():
    """Test the logging system setup and functionality"""
    print("🧪 Testing Elaborate Logging System")
    print("=" * 50)
    
    # Setup logging
    setup_logging()
    print("✅ Logging system initialized")
    
    # Test document pipeline logger
    print("\n📄 Testing Document Pipeline Logger:")
    document_logger.info("🚀 Starting document processing test")
    document_logger.debug("📋 Processing document: test.pdf")
    document_logger.warning("⚠️  Large file detected: 10MB")
    document_logger.error("❌ Failed to extract text from page 5")
    
    # Test message pipeline logger
    print("\n💬 Testing Message Pipeline Logger:")
    message_logger.info("🚀 Starting message processing test")
    message_logger.debug("👤 Processing messages for user: test_user_123")
    message_logger.info("🎯 Language detected: English")
    message_logger.debug("📝 Generated response: Hello, how can I help?")
    
    # Test embedding service logger
    print("\n🔢 Testing Embedding Service Logger:")
    embedding_logger.info("🚀 Starting embedding generation test")
    embedding_logger.debug("📊 Text length: 500 characters")
    embedding_logger.info("✅ Embedding generated: 1024 dimensions")
    embedding_logger.warning("⚠️  API rate limit approaching")
    
    # Test database logger
    print("\n🗃️  Testing Database Logger:")
    db_logger.info("🔗 Testing database connection")
    db_logger.debug("💾 Inserting document: test_doc_123")
    db_logger.info("🔍 Searching for similar chunks")
    db_logger.debug("📊 Found 5 similar documents")
    
    print("\n🎉 All logging tests completed!")
    print("📁 Check the 'logs/' directory for log files:")
    print("   - telegram_bot.log (main application log)")
    print("   - document_pipeline.log (document processing)")
    print("   - message_pipeline.log (message processing)")
    print("   - embedding_service.log (embedding operations)")
    print("   - database.log (database operations)")

def test_performance_logger():
    """Test the performance logging decorator"""
    print("\n⏱️  Testing Performance Logger:")
    
    @performance_logger
    def sync_test_function(name: str) -> str:
        """Test synchronous function with performance logging"""
        import time
        time.sleep(0.1)  # Simulate work
        return f"Processed {name}"
    
    @performance_logger
    async def async_test_function(name: str) -> str:
        """Test asynchronous function with performance logging"""
        await asyncio.sleep(0.1)  # Simulate async work
        return f"Async processed {name}"
    
    # Test synchronous function
    result = sync_test_function("sync_test")
    print(f"Sync result: {result}")
    
    # Test asynchronous function
    async def run_async_test():
        result = await async_test_function("async_test")
        print(f"Async result: {result}")
    
    asyncio.run(run_async_test())

if __name__ == "__main__":
    test_logging_system()
    test_performance_logger()
    
    print("\n🔍 Log Directory Structure:")
    logs_dir = "logs"
    if os.path.exists(logs_dir):
        for file in os.listdir(logs_dir):
            file_path = os.path.join(logs_dir, file)
            if os.path.isfile(file_path):
                size = os.path.getsize(file_path)
                print(f"   📄 {file} ({size} bytes)")
    else:
        print("   📁 Logs directory will be created when the system runs")
