import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Bot Configuration
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
XAI_API_KEY = os.getenv("XAI_API_KEY")

# Embedding Service Configuration
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")
EMBEDDING_SERVICE = os.getenv("EMBEDDING_SERVICE", "huggingface")  # Options: "huggingface", "local"
EMBEDDING_MODEL = "intfloat/multilingual-e5-large"  # HuggingFace model that supports feature extraction (1024 dimensions)
EMBEDDING_BATCH_SIZE = 50  # HuggingFace allows batch processing
EMBEDDING_MAX_RETRIES = 3
EMBEDDING_TIMEOUT = 30

# MongoDB Configuration
MONGODB_USERNAME = os.getenv("MONGODB_USERNAME")
MONGODB_PASSWORD = os.getenv("MONGODB_PASSWORD")
MONGODB_CLUSTER = os.getenv("MONGODB_CLUSTER")
MONGODB_APP_NAME = os.getenv("MONGODB_APP_NAME", "Cluster0")

# Construct MongoDB URI from environment variables
if MONGODB_USERNAME and MONGODB_PASSWORD and MONGODB_CLUSTER:
    MONGODB_URI = f"mongodb+srv://{MONGODB_USERNAME}:{MONGODB_PASSWORD}@{MONGODB_CLUSTER}/?retryWrites=true&w=majority&appName={MONGODB_APP_NAME}"
else:
    # Fallback to environment variable if components are missing
    MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME", "telegram_bot")
MONGODB_COLLECTIONS = {
    "messages": "message_queue",
    "documents": "documents"
}

# Vector Search Configuration
VECTOR_DIMENSIONS = 1024  # intfloat/multilingual-e5-large dimensions
VECTOR_SIMILARITY = "cosine"
VECTOR_INDEX_NAME = "default"

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
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Create logs directory
LOGS_DIR = "logs"
os.makedirs(LOGS_DIR, exist_ok=True)
