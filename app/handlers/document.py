from typing import Dict, Any, List
from datetime import datetime
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, UnstructuredFileLoader
from langchain.chains import RetrievalQA
from langchain_xai import ChatXAI
from langchain.schema import Document as LangchainDocument
import os
import mimetypes
import logging
from langchain.prompts import ChatPromptTemplate

from ..config import CHUNK_SIZE, CHUNK_OVERLAP, VECTOR_INDEX_NAME, VECTOR_DIMENSIONS, LLM_MODEL, XAI_API_KEY
from ..database.mongodb import db
from ..models.document import Document
from ..services.embedding import embedding_service
from ..utils.logging import log_async_performance, get_logger, log_user_interaction

# Setup dedicated logger for document pipeline
doc_logger = get_logger('document_pipeline')

class DocumentHandler:
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
            length_function=len,
            separators=["\n\n", "\n", ".", "!", "?", ";", ":", " ", ""]
        )
        self.db = db  # Initialize MongoDB connection
        
        # Use the HuggingFace embedding service
        self.embedding_service = embedding_service
        self.embedding_dim = self.embedding_service.dimensions
        
        # Initialize xAI Chat model
        self.llm = ChatXAI(
            api_key=XAI_API_KEY,
            model=LLM_MODEL,
            temperature=0.7
        )
        
        mimetypes.init()
    
    async def _embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for documents using the HuggingFace service"""
        return await self.embedding_service.embed_documents(texts)
    
    async def _embed_query(self, query: str) -> List[float]:
        """Generate embedding for query using the HuggingFace service"""
        return await self.embedding_service.embed_query(query)
    
    def _get_loader(self, file_path: str):
        """Get appropriate loader based on file type"""
        mime_type, _ = mimetypes.guess_type(file_path)
        
        if mime_type == 'application/pdf':
            return PyPDFLoader(file_path)
        elif mime_type in ['application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']:
            return Docx2txtLoader(file_path)
        else:
            # Fallback to simple text reading for unsupported file types
            try:
                from langchain_community.document_loaders import UnstructuredFileLoader
                return UnstructuredFileLoader(file_path)
            except ImportError:
                # If unstructured is not available, use a simple text loader
                from langchain_community.document_loaders import TextLoader
                return TextLoader(file_path)
    
    async def process_document(self, file_path: str, user_id: str) -> Dict[str, Any]:
        """Process a document and store it with embeddings in MongoDB"""
        doc_logger.info(f"📄 Starting document processing for user {user_id}")
        doc_logger.info(f"📁 File path: {file_path}")
        doc_logger.info(f"📊 File size: {os.path.getsize(file_path) / 1024:.2f} KB")
        
        try:
            # Create document instance
            doc_logger.debug("🔨 Creating document instance")
            document = Document.create(user_id, file_path)
            doc_logger.info(f"🔍 Document hash: {document.file_hash}")
            doc_logger.info(f"📝 Document metadata: {document.metadata}")
            
            # Check if document already exists
            doc_logger.debug("🔍 Checking for existing document")
            existing_doc = self.db.get_document_by_hash(document.file_hash)
            if existing_doc:
                doc_logger.info(f"♻️  Document already exists with ID: {existing_doc['_id']}")
                return {"status": "exists", "doc_id": existing_doc["_id"]}
            
            # Load and split document
            doc_logger.info("📖 Loading document content")
            loader = self._get_loader(file_path)
            doc_logger.debug(f"🔧 Using loader: {type(loader).__name__}")
            
            raw_documents = loader.load()
            doc_logger.info(f"📚 Loaded {len(raw_documents)} raw document(s)")
            
            # Combine all text from the document
            full_text = "\n\n".join([doc.page_content for doc in raw_documents])
            doc_logger.info(f"📝 Full text length: {len(full_text)} characters")
            doc_logger.debug(f"📄 Text preview: {full_text[:200]}...")
            
            # Split into chunks with better context preservation
            doc_logger.info("✂️  Splitting document into chunks")
            chunks = self.text_splitter.create_documents(
                texts=[full_text],
                metadatas=[{
                    "user_id": user_id,
                    "file_hash": document.file_hash,
                    "file_name": os.path.basename(file_path),
                    "source": file_path
                }]
            )
            doc_logger.info(f"📊 Created {len(chunks)} chunks")
            doc_logger.debug(f"📏 Average chunk size: {sum(len(chunk.page_content) for chunk in chunks) / len(chunks):.0f} chars")
            
            # Update document with chunk information
            document.chunk_count = len(chunks)
            doc_logger.info(f"📋 Updated document with {document.chunk_count} chunks")
            
            # Get embeddings for all chunks using the service
            chunk_texts = [chunk.page_content for chunk in chunks]
            doc_logger.info(f"🧠 Generating embeddings for {len(chunk_texts)} chunks")
            doc_logger.debug(f"🔧 Using embedding service: {type(self.embedding_service).__name__}")
            
            embedding_start_time = datetime.now()
            all_embeddings = await self._embed_documents(chunk_texts)
            embedding_duration = (datetime.now() - embedding_start_time).total_seconds()
            
            doc_logger.info(f"✅ Generated {len(all_embeddings)} embeddings in {embedding_duration:.2f}s")
            doc_logger.debug(f"📊 Embedding dimensions: {len(all_embeddings[0])} per chunk")
            doc_logger.debug(f"⚡ Average embedding time: {embedding_duration / len(chunk_texts):.3f}s per chunk")
            
            # Create chunks with embeddings and better metadata
            chunks_data = []
            doc_logger.info("📦 Processing chunks for storage")
            
            for i, (chunk, embedding) in enumerate(zip(chunks, all_embeddings)):
                chunk_id = f"{document.file_hash}_{i}"
                chunk_text = chunk.page_content.strip()
                
                # Skip empty chunks
                if not chunk_text:
                    doc_logger.debug(f"⏭️  Skipping empty chunk {i}")
                    continue
                
                doc_logger.debug(f"📝 Processing chunk {i+1}/{len(chunks)}: {len(chunk_text)} chars")
                
                # Create chunk metadata
                chunk_metadata = {
                    "user_id": user_id,
                    "file_hash": document.file_hash,
                    "chunk_id": chunk_id,
                    "chunk_index": i,
                    "source": file_path,
                    "file_name": os.path.basename(file_path),
                    "total_chunks": len(chunks),
                    "char_length": len(chunk_text),
                    "word_count": len(chunk_text.split()),
                    "created_at": datetime.utcnow(),
                    "embedding_service": type(self.embedding_service).__name__,
                    "embedding_model": getattr(self.embedding_service, 'model', 'unknown')
                }
                
                chunks_data.append({
                    "chunk_id": chunk_id,
                    "content": chunk_text,
                    "embedding": embedding,
                    "metadata": chunk_metadata
                })
            
            doc_logger.info(f"📦 Prepared {len(chunks_data)} chunks for storage")
            doc_logger.debug(f"📊 Total characters processed: {sum(len(chunk['content']) for chunk in chunks_data)}")
            doc_logger.debug(f"📈 Average words per chunk: {sum(chunk['metadata']['word_count'] for chunk in chunks_data) / len(chunks_data):.1f}")
            
            # Update document with chunks data
            document.chunks = chunks_data
            document.status = "processed"
            doc_logger.info(f"✅ Document status updated to: {document.status}")
            
            # Store document in MongoDB
            doc_logger.info("💾 Storing document in MongoDB")
            storage_start_time = datetime.now()
            doc_id = self.db.add_document(document.to_dict())
            storage_duration = (datetime.now() - storage_start_time).total_seconds()
            
            doc_logger.info(f"✅ Document stored successfully with ID: {doc_id}")
            doc_logger.info(f"⏱️  Storage completed in {storage_duration:.3f}s")
            
            return {
                "status": "success",
                "doc_id": doc_id,
                "file_hash": document.file_hash,
                "chunk_count": len(chunks_data),
                "metadata": document.metadata
            }
            
        except Exception as e:
            doc_logger.error(f"❌ Document processing failed for user {user_id}")
            doc_logger.error(f"📁 File: {file_path}")
            doc_logger.error(f"💥 Error: {str(e)}", exc_info=True)
            
            error_info = {
                "user_id": user_id,
                "file_path": file_path,
                "error": str(e),
                "timestamp": datetime.utcnow(),
                "status": "failed"
            }
            
            try:
                self.db.add_document(error_info)
                doc_logger.info("📝 Error info stored in database")
            except Exception as db_error:
                doc_logger.error(f"💥 Failed to store error info: {str(db_error)}")
            
            raise
    
    async def query_documents(self, query: str, user_id: str, k: int = 20) -> Dict[str, Any]:
        """Query documents using MongoDB vector search"""
        doc_logger.info(f"🔍 Starting document query for user {user_id}")
        doc_logger.info(f"❓ Query: '{query}'")
        doc_logger.debug(f"📊 Requested results: {k}")
        
        try:
            # Get user's documents from MongoDB
            doc_logger.debug("📚 Fetching user documents from database")
            user_docs = self.db.get_user_documents(user_id)
            
            if not user_docs:
                doc_logger.info(f"📭 No documents found for user {user_id}")
                return {
                    "answer": "No documents found in your collection.",
                    "sources": []
                }
            
            doc_logger.info(f"📚 Found {len(user_docs)} documents for user")
            total_chunks = sum(len(doc.get('chunks', [])) for doc in user_docs)
            doc_logger.debug(f"📦 Total searchable chunks: {total_chunks}")

            # Generate semantic variations for better search coverage
            doc_logger.debug("🔄 Generating semantic query variations")
            semantic_variations = [
                query,  # Original query
                f"find information about {query}",  # Explicit search
                f"what does the document say about {query}",  # Document-focused
                f"find content related to {query}",  # Related content
                query.replace("?", "").strip(),  # Clean query
                f"extract information about {query}"  # Information extraction
            ]
            doc_logger.debug(f"🔍 Created {len(semantic_variations)} query variations")
            
            all_chunks = []
            seen_chunk_ids = set()
            
            # Search with each variation and collect results
            for variation in semantic_variations:
                # Get embedding for the variation using the service
                query_embedding = await self._embed_query(variation)
                
                # Search similar chunks
                chunks = self.db.search_similar_chunks(query_embedding, user_id, k=5)
                
                # Add unique chunks to results
                for chunk in chunks:
                    chunk_id = f"{chunk['metadata'].get('file_hash', '')}_{chunk['metadata'].get('chunk_index', '')}"
                    if chunk_id not in seen_chunk_ids:
                        seen_chunk_ids.add(chunk_id)
                        all_chunks.append(chunk)
            
            if not all_chunks:
                return {
                    "answer": "No relevant content found in your documents.",
                    "sources": []
                }
            
            # Sort chunks by similarity score
            all_chunks.sort(key=lambda x: x.get("score", 0), reverse=True)
            
            # Take top k most relevant chunks
            top_chunks = all_chunks[:k]
            
            # Create context with full content
            contexts = []
            sources = []
            
            for chunk in top_chunks:
                metadata = chunk["metadata"]
                score = chunk.get("score", 0)
                
                # Create Langchain Document objects
                doc = LangchainDocument(
                    page_content=chunk["content"],
                    metadata={
                        "source": metadata.get("file_name", "Unknown"),
                        "section": metadata.get("chunk_index", 0) + 1,
                        "score": score
                    }
                )
                contexts.append(doc)
                
                # Add to sources with full content
                sources.append({
                    "content": chunk["content"],
                    "metadata": metadata,
                    "similarity_score": score
                })
            
            # Create context string from documents
            context_str = "\n\n".join([
                f"From {doc.metadata['source']} (Section {doc.metadata['section']}):\n{doc.page_content}"
                for doc in contexts
            ])

            # Create prompt template
            from langchain.prompts import PromptTemplate
            from langchain_core.runnables import RunnablePassthrough
            
            prompt = PromptTemplate(
                template="""You are a knowledgeable assistant providing clear and concise information.

            Context:
            {context}

            Question: {question}

            Instructions:
            1. Answer directly and naturally, as if you inherently know the information
            2. Don't say phrases like "According to the document" or "I found in the documents"
            3. Don't mention sources unless specifically asked
            4. Keep the answer focused and to the point
            5. Use a conversational but professional tone
            6. If information isn't available, say so briefly and clearly
            7. Avoid repeating information

            Answer:""",
                input_variables=["context", "question"]
            )
            
            
            # Create chain using xAI Chat model
            chain = (
                {
                    "context": lambda x: context_str,
                    "question": lambda x: x["question"]
                }
                | prompt
                | self.llm
            )
            
            # Get response using the new invoke method
            response = chain.invoke({"question": query})
            answer = response.content if hasattr(response, 'content') else str(response)
            

            return {
                "answer": answer,
                "sources": sources,
                "total_docs": len(user_docs),
                "docs_used": len(seen_chunk_ids)
            }

        except Exception as e:
            print(f"Error in query_documents: {str(e)}")
            # Fallback to direct content return
            if all_chunks:
                answer = "Here's what I found in the documents:\n\n"
                for chunk in all_chunks[:3]:
                    answer += f"- {chunk['content']}\n\n"
                return {
                    "answer": answer,
                    "sources": all_chunks[:3],
                    "total_docs": len(user_docs),
                    "docs_used": len(all_chunks)
                }
            return {
                "answer": f"Error querying documents: {str(e)}",
                "sources": []
            }

# Create a singleton instance
document_handler = DocumentHandler()
