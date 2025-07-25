from typing import Dict, Any, List
from datetime import datetime
import logging
from pymongo import MongoClient, ASCENDING
from pymongo.operations import IndexModel

from ..config import (
    MONGODB_URI, 
    MONGODB_DB_NAME, 
    MONGODB_COLLECTIONS,
    VECTOR_DIMENSIONS,
    VECTOR_SIMILARITY,
    VECTOR_INDEX_NAME
)

from ..models.document import Document
from ..models.message import MessageModel
from ..utils.logging import db_logger, log_async_performance, log_performance

class MongoDB:
    def __init__(self):
        db_logger.info("🔗 Initializing MongoDB connection")
        db_logger.debug(f"📍 Connection URI: {MONGODB_URI[:30]}...")
        db_logger.debug(f"🗃️  Database: {MONGODB_DB_NAME}")
        
        self.client = MongoClient(
            MONGODB_URI,
            tls=True,
            tlsAllowInvalidCertificates=True,  # Disable certificate verification for development
            serverSelectionTimeoutMS=10000  # 5 second timeout
        )
        self.db = self.client[MONGODB_DB_NAME]
        self.message_queue = self.db[MONGODB_COLLECTIONS["messages"]]
        self.documents = self.db[MONGODB_COLLECTIONS["documents"]]
        
        db_logger.info("✅ MongoDB client initialized")
        db_logger.debug(f"📋 Collections: {list(MONGODB_COLLECTIONS.values())}")
        
        self._setup_indexes()
    
    def _setup_indexes(self):
        """Setup database indexes for optimal query performance"""
        db_logger.info("🔧 Setting up database indexes")
        
        try:
            # Vector index for similarity search
            try:
                vector_index_result = self.documents.create_index([
                    ("embedding", "2dsphere")
                ], name="vector_index")
                db_logger.debug(f"📊 Vector index: {vector_index_result}")
            except Exception as e:
                if "already exists" in str(e):
                    db_logger.debug("📊 Vector index already exists, skipping")
                else:
                    raise
            
            # Text index for content search - check if it exists first
            try:
                # Check existing indexes to avoid conflicts
                existing_indexes = list(self.documents.list_indexes())
                text_index_exists = any("text" in idx.get("key", {}).values() for idx in existing_indexes)
                
                if not text_index_exists:
                    text_index_result = self.documents.create_index([
                        ("content", "text"),
                        ("file_name", "text")
                    ], name="content_text_index")
                    db_logger.debug(f"🔍 Text index: {text_index_result}")
                else:
                    db_logger.debug("🔍 Text index already exists, skipping creation")
            except Exception as e:
                if "already exists" in str(e) or "IndexOptionsConflict" in str(e):
                    db_logger.debug("🔍 Text index conflict detected, using existing index")
                else:
                    raise
            
            # Compound index for user-specific queries
            try:
                user_index_result = self.documents.create_index([
                    ("user_id", 1),
                    ("timestamp", -1)
                ], name="user_timestamp_index")
                db_logger.debug(f"👤 User index: {user_index_result}")
            except Exception as e:
                if "already exists" in str(e):
                    db_logger.debug("👤 User index already exists, skipping")
                else:
                    raise
            
            # Message queue index
            try:
                message_index_result = self.message_queue.create_index([
                    ("user_id", 1),
                    ("timestamp", -1)
                ], name="message_user_timestamp_index")
                db_logger.debug(f"💬 Message index: {message_index_result}")
            except Exception as e:
                if "already exists" in str(e):
                    db_logger.debug("💬 Message index already exists, skipping")
                else:
                    raise
            
            db_logger.info("✅ All database indexes created successfully")
            
        except Exception as e:
            db_logger.error(f"❌ Failed to create indexes: {str(e)}")
            # Don't raise the exception - let the app continue even if indexes fail
            db_logger.info("🔄 Continuing without index creation, app should still work")
    
    @log_async_performance("database")
    async def insert_message(self, message: MessageModel) -> str:
        """Insert a message into the database"""
        db_logger.info(f"💾 Inserting message for user {message.user_id}")
        
        # Handle both custom Message class and potential other message types
        message_text = getattr(message, 'message', '') or getattr(message, 'text', '') or getattr(message, 'content', '')
        db_logger.debug(f"📝 Message preview: {message_text[:100]}...")
        
        try:
            # Use to_dict() method if available, otherwise try model_dump()
            if hasattr(message, 'to_dict'):
                message_dict = message.to_dict()
            elif hasattr(message, 'model_dump'):
                message_dict = message.model_dump()
            else:
                # Fallback: manually create dict from known attributes
                message_dict = {
                    'user_id': message.user_id,
                    'message': message_text,
                    'timestamp': getattr(message, 'timestamp', datetime.utcnow()),
                    'is_processed': getattr(message, 'is_processed', False),
                    'is_file': getattr(message, 'is_file', False)
                }
            
            message_dict['timestamp'] = datetime.utcnow()
            
            result = self.message_queue.insert_one(message_dict)
            message_id = str(result.inserted_id)
            
            db_logger.info(f"✅ Message inserted successfully: {message_id}")
            db_logger.debug(f"📊 Document ID: {message_id}")
            
            return message_id
            
        except Exception as e:
            db_logger.error(f"❌ Failed to insert message: {str(e)}")
            # Safe debug logging that won't fail
            try:
                if hasattr(message, 'to_dict'):
                    debug_data = message.to_dict()
                elif hasattr(message, 'model_dump'):
                    debug_data = message.model_dump()
                else:
                    debug_data = f"Message type: {type(message)}, user_id: {getattr(message, 'user_id', 'unknown')}"
                db_logger.debug(f"🔍 Message data: {debug_data}")
            except:
                db_logger.debug(f"🔍 Could not serialize message data for debugging")
            raise
    
    @log_performance("database")
    def get_pending_messages(self, user_id: str, cutoff_time: datetime, limit: int) -> List[Dict[str, Any]]:
        """Get pending messages for processing"""
        db_logger.info(f"🔍 Getting pending messages for user {user_id}")
        db_logger.debug(f"⏰ Cutoff time: {cutoff_time}")
        db_logger.debug(f"📊 Limit: {limit}")
        
        try:
            messages = list(self.message_queue.find({
                "user_id": user_id,
                "is_processed": False,
                "timestamp": {"$gte": cutoff_time}
            }).sort("timestamp", ASCENDING).limit(limit))
            
            db_logger.info(f"✅ Found {len(messages)} pending messages")
            db_logger.debug(f"📝 Message IDs: {[str(msg['_id']) for msg in messages]}")
            
            return messages
            
        except Exception as e:
            db_logger.error(f"❌ Failed to get pending messages: {str(e)}")
            raise
    
    @log_performance("database")
    def mark_messages_as_processed(self, message_ids: List[str], batch_id: str):
        """Mark messages as processed"""
        db_logger.info(f"✅ Marking {len(message_ids)} messages as processed")
        db_logger.debug(f"🏷️  Batch ID: {batch_id}")
        db_logger.debug(f"📝 Message IDs: {message_ids}")
        
        try:
            result = self.message_queue.update_many(
                {"_id": {"$in": message_ids}},
                {
                    "$set": {
                        "is_processed": True,
                        "batch_id": batch_id,
                        "processing_started": datetime.utcnow()
                    }
                }
            )
            
            db_logger.info(f"✅ Updated {result.modified_count} messages")
            db_logger.debug(f"🔍 Matched: {result.matched_count}, Modified: {result.modified_count}")
            
        except Exception as e:
            db_logger.error(f"❌ Failed to mark messages as processed: {str(e)}")
            raise
    
    @log_performance("database")
    def update_message_response(self, batch_id: str, response: str):
        """Update messages with response"""
        db_logger.info(f"📝 Updating message response for batch {batch_id}")
        db_logger.debug(f"💬 Response preview: {response[:100]}...")
        
        try:
            result = self.message_queue.update_many(
                {"batch_id": batch_id},
                {
                    "$set": {
                        "processing_completed": datetime.utcnow(),
                        "response": response
                    }
                }
            )
            
            db_logger.info(f"✅ Updated {result.modified_count} messages with response")
            db_logger.debug(f"🔍 Matched: {result.matched_count}, Modified: {result.modified_count}")
            
        except Exception as e:
            db_logger.error(f"❌ Failed to update message response: {str(e)}")
            raise
    
    @log_performance("database")
    def add_document(self, doc_info: Dict[str, Any]) -> str:
        """Add a document to the database"""
        db_logger.info(f"💾 Adding document to database")
        db_logger.debug(f"📋 Document keys: {list(doc_info.keys())}")
        db_logger.debug(f"📊 Chunks count: {len(doc_info.get('chunks', []))}")
        
        try:
            # Convert numpy arrays to lists for MongoDB storage
            if "chunks" in doc_info:
                db_logger.debug(f"🔄 Converting embeddings for {len(doc_info['chunks'])} chunks")
                for i, chunk in enumerate(doc_info["chunks"]):
                    if "embedding" in chunk and hasattr(chunk["embedding"], 'tolist'):
                        chunk["embedding"] = chunk["embedding"].tolist()
                        db_logger.debug(f"✅ Converted embedding for chunk {i+1}")
            
            result = self.documents.insert_one(doc_info)
            document_id = str(result.inserted_id)
            
            db_logger.info(f"✅ Document added successfully: {document_id}")
            db_logger.debug(f"📊 Final document size: {len(str(doc_info))} chars")
            
            return document_id
            
        except Exception as e:
            db_logger.error(f"❌ Failed to add document: {str(e)}")
            db_logger.debug(f"🔍 Document info: {doc_info.keys()}")
            raise
    
    @log_performance("database")
    def get_document_by_hash(self, file_hash: str) -> Dict[str, Any]:
        """Get document by file hash"""
        db_logger.info(f"🔍 Looking up document by hash: {file_hash[:16]}...")
        
        try:
            document = self.documents.find_one({"file_hash": file_hash})
            
            if document:
                db_logger.info(f"✅ Document found: {document.get('file_name', 'Unknown')}")
                db_logger.debug(f"📊 Document ID: {document['_id']}")
            else:
                db_logger.info(f"❌ No document found with hash: {file_hash[:16]}...")
            
            return document
            
        except Exception as e:
            db_logger.error(f"❌ Failed to get document by hash: {str(e)}")
            raise
    
    @log_performance("database")
    def get_user_documents(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all documents for a user"""
        db_logger.info(f"📚 Getting all documents for user {user_id}")
        
        try:
            documents = list(self.documents.find({"user_id": user_id}))
            
            db_logger.info(f"✅ Found {len(documents)} documents for user")
            db_logger.debug(f"📋 Document names: {[doc.get('file_name', 'Unknown') for doc in documents]}")
            
            return documents
            
        except Exception as e:
            db_logger.error(f"❌ Failed to get user documents: {str(e)}")
            raise
    
    @log_performance("database")
    def search_similar_chunks(self, query_vector: List[float], user_id: str, k: int = 3) -> List[Dict[str, Any]]:
        """Search for similar chunks using vector similarity"""
        db_logger.info(f"🔍 Searching for similar chunks for user {user_id}")
        db_logger.debug(f"🎯 Query vector dimensions: {len(query_vector)}")
        db_logger.debug(f"📊 Requested results: {k}")
        
        try:
            # Handle numpy array conversion if needed
            if hasattr(query_vector, 'tolist'):
                query_vector = query_vector.tolist()
                db_logger.debug("🔄 Converted numpy array to list")
            
            # MongoDB aggregation pipeline for vector similarity search
            pipeline = [
                {
                    "$match": {
                        "user_id": user_id,
                        "chunks.embedding": {"$exists": True}
                    }
                },
                {"$unwind": "$chunks"},
                {
                    "$addFields": {
                        "similarity": {
                            "$divide": [
                                {
                                    "$reduce": {
                                        "input": {"$range": [0, {"$size": "$chunks.embedding"}]},
                                        "initialValue": 0,
                                        "in": {
                                            "$add": [
                                                "$$value",
                                                {
                                                    "$multiply": [
                                                        {"$arrayElemAt": ["$chunks.embedding", "$$this"]},
                                                        {"$arrayElemAt": [query_vector, "$$this"]}
                                                    ]
                                                }
                                            ]
                                        }
                                    }
                                },
                                {
                                    "$multiply": [
                                        {
                                            "$sqrt": {
                                                "$reduce": {
                                                    "input": "$chunks.embedding",
                                                    "initialValue": 0,
                                                    "in": {"$add": ["$$value", {"$multiply": ["$$this", "$$this"]}]}
                                                }
                                            }
                                        },
                                        {
                                            "$sqrt": {
                                                "$reduce": {
                                                    "input": query_vector,
                                                    "initialValue": 0,
                                                    "in": {"$add": ["$$value", {"$multiply": ["$$this", "$$this"]}]}
                                                }
                                            }
                                        }
                                    ]
                                }
                            ]
                        }
                    }
                },
                {"$sort": {"similarity": -1}},
                {"$limit": k},
                {
                    "$project": {
                        "file_name": 1,
                        "chunk_text": "$chunks.text",
                        "chunk_index": "$chunks.chunk_index",
                        "similarity": 1,
                        "_id": 0
                    }
                }
            ]
            
            results = list(self.documents.aggregate(pipeline))
            
            db_logger.info(f"✅ Found {len(results)} similar chunks")
            db_logger.debug(f"📊 Similarity scores: {[r.get('similarity', 0) for r in results]}")
            
            return results
            
        except Exception as e:
            db_logger.error(f"❌ Failed to search similar chunks: {str(e)}")
            db_logger.debug(f"🔍 Query vector shape: {len(query_vector) if query_vector else 'None'}")
            raise

# Create a singleton instance
db = MongoDB()
