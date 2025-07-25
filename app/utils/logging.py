"""
Logging configuration for the Telegram Multi-Agent AI Bot
Docker-friendly console logging only
"""

import logging
import time
from typing import Optional, Any, Dict
from functools import wraps

# Import LOG_LEVEL with fallback
try:
    from app.config import LOG_LEVEL
except ImportError:
    import os
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

def setup_logging():
    """Configure logging for the entire application - Docker console only"""
    
    # Create console formatter
    console_formatter = logging.Formatter(
        fmt="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%H:%M:%S"
    )
    
    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, LOG_LEVEL.upper()))
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Console handler only - Docker will capture this
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # Log startup
    logger = logging.getLogger(__name__)
    logger.info("🚀 Logging system initialized")
    logger.info(f"📊 Log level: {LOG_LEVEL}")
    logger.info("📝 Using console logging (Docker will capture)")
    
def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for a specific component"""
    return logging.getLogger(name)

# Performance logging decorator
def log_performance(logger_name: Optional[str] = None):
    """Decorator to log function performance"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger = logging.getLogger(logger_name or func.__module__)
            start_time = time.time()
            
            logger.debug(f"🚀 Starting {func.__name__} with args={len(args)}, kwargs={list(kwargs.keys())}")
            
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                logger.info(f"✅ {func.__name__} completed in {duration:.3f}s")
                return result
            except Exception as e:
                duration = time.time() - start_time
                logger.error(f"❌ {func.__name__} failed after {duration:.3f}s: {str(e)}")
                raise
        return wrapper
    return decorator

# Async performance logging decorator
def log_async_performance(logger_name: Optional[str] = None):
    """Decorator to log async function performance"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            logger = logging.getLogger(logger_name or func.__module__)
            start_time = time.time()
            
            logger.debug(f"🚀 Starting async {func.__name__} with args={len(args)}, kwargs={list(kwargs.keys())}")
            
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                logger.info(f"✅ {func.__name__} completed in {duration:.3f}s")
                return result
            except Exception as e:
                duration = time.time() - start_time
                logger.error(f"❌ {func.__name__} failed after {duration:.3f}s: {str(e)}")
                raise
        return wrapper
    return decorator

# Create module-level loggers that can be imported directly
document_logger = logging.getLogger("document_pipeline")
message_logger = logging.getLogger("message_pipeline")
embedding_logger = logging.getLogger("embedding_service")
db_logger = logging.getLogger("database")
performance_logger = logging.getLogger("performance")

def log_user_interaction(user_id: int, username: str, action: str, details: Optional[Dict[str, Any]] = None):
    """Log user interactions for analytics and debugging."""
    logger = logging.getLogger('user_interactions')
    
    details_str = f" - {details}" if details else ""
    logger.info(f"👤 User {username} ({user_id}) performed {action}{details_str}")

def log_error_with_context(logger: logging.Logger, error: Exception, context: Dict[str, Any]):
    """Log error with additional context information."""
    context_str = ", ".join([f"{k}={v}" for k, v in context.items()])
    logger.error(f"💥 Error occurred: {str(error)} | Context: {context_str}", exc_info=True)

class StructuredLogger:
    """A structured logger that adds consistent formatting and context."""
    
    def __init__(self, name: str):
        self.logger = get_logger(name)
        self.context = {}
    
    def add_context(self, **kwargs):
        """Add persistent context to all log messages."""
        self.context.update(kwargs)
    
    def clear_context(self):
        """Clear all persistent context."""
        self.context.clear()
    
    def _format_message(self, message: str) -> str:
        """Format message with context."""
        if self.context:
            context_str = ", ".join([f"{k}={v}" for k, v in self.context.items()])
            return f"{message} | Context: {context_str}"
        return message
    
    def debug(self, message: str, **kwargs):
        formatted_msg = self._format_message(message)
        self.logger.debug(formatted_msg)
    
    def info(self, message: str, **kwargs):
        formatted_msg = self._format_message(message)
        self.logger.info(formatted_msg)
    
    def warning(self, message: str, **kwargs):
        formatted_msg = self._format_message(message)
        self.logger.warning(formatted_msg)
    
    def error(self, message: str, **kwargs):
        formatted_msg = self._format_message(message)
        self.logger.error(formatted_msg)
    
    def critical(self, message: str, **kwargs):
        formatted_msg = self._format_message(message)
        self.logger.critical(formatted_msg)
