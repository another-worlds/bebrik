import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Bot Configuration
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
XAI_API_KEY = os.getenv("XAI_API_KEY")

# MongoDB Configuration
MONGODB_URI = "mongodb+srv://aegorshev:vbu677776A.@cluster0.c2qsjcq.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME", "telegram_bot")
MONGODB_COLLECTIONS = {
    "messages": "message_queue",
    "documents": "documents"
}

# Vector Search Configuration
VECTOR_DIMENSIONS = 384  # Sentence Transformers all-MiniLM-L6-v2 dimensions
VECTOR_SIMILARITY = "cosine"
VECTOR_INDEX_NAME = "default"

# Embedding Model Configuration
EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # Fast and efficient sentence transformer model

# Message Processing Configuration
WAIT_TIME = 15  # seconds to wait for additional messages
MAX_MESSAGES_PER_BATCH = 10  # maximum number of messages to process in one batch

# Document Processing Configuration
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
DOCUMENT_UPLOAD_PATH = os.getenv("DOCUMENT_UPLOAD_PATH", "uploads")

# Language Model Configuration
LLM_MODEL = "grok-3"  # xAI's Grok model
LLM_TEMPERATURE = 0.7

# Create necessary directories
os.makedirs(DOCUMENT_UPLOAD_PATH, exist_ok=True)

# Logging configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
