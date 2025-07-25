#!/usr/bin/env python3
"""
Test script to verify the simplified console-only logging system
"""

import asyncio
import sys
import os
import time

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(__file__))

from app.utils.logging import setup_logging
from app.utils.logging import document_logger, message_logger, embedding_logger, db_logger
from app.utils.logging import log_performance, log_async_performance  # Import both decoratorsython3
"""
Test script to verify the si    print("📺 Console logging is active - Docker will capture all output!")plified console-only logging system
"""

import asyncio
import sys
import os
import time

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '.'))

from app.utils.logging import setup_logging
from app.utils.logging import document_logger, message_logger, embedding_logger, db_logger
from app.utils.logging import log_performance, log_async_performance  # Import both decorators

def test_logging_system():
    """Test the console-only logging system functionality"""
    print("🧪 Testing Console-Only Logging System")
    print("=" * 50)
    
    # Setup logging
    setup_logging()
    print("✅ Console logging system initialized")
    
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
    print("� Console logging is active - Docker will capture all output!")
    print("💡 Use 'docker-compose logs -f telegram-bot' to view logs")

def test_performance_logger():
    """Test the performance logging decorator"""
    print("\n⏱️  Testing Performance Logger:")
    
    @log_performance("test_module")
    def sync_test_function(name: str) -> str:
        """Test synchronous function with performance logging"""
        time.sleep(0.1)  # Simulate work
        return f"Processed {name}"
    
    @log_async_performance("test_module")
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
    
    print("\n� Console-only logging is active - no log files are created!")
    print("� All output is captured by Docker for centralized log management")
