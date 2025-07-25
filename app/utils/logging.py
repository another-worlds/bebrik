"""
Logging configuration for the Telegram Multi-Agent AI Bot
"""

import logging
import logging.handlers
import os
import time
from typing import Optional, Any, Dict
from datetime import datetime
from functools import wraps
from ..config import LOG_LEVEL, LOG_FORMAT, LOG_DATE_FORMAT, LOGS_DIR

def setup_logging():
    """Configure logging for the entire application"""
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        fmt=LOG_FORMAT,
        datefmt=LOG_DATE_FORMAT
    )
    
    simple_formatter = logging.Formatter(
        fmt="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%H:%M:%S"
    )
    
    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, LOG_LEVEL.upper()))
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(simple_formatter)
    root_logger.addHandler(console_handler)
    
    # File handler for all logs
    file_handler = logging.handlers.RotatingFileHandler(
        filename=os.path.join(LOGS_DIR, "bot.log"),
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(getattr(logging, LOG_LEVEL.upper()))
    file_handler.setFormatter(detailed_formatter)
    root_logger.addHandler(file_handler)
    
    # Separate handlers for specific components
    setup_component_loggers(detailed_formatter)
    
    # Log startup
    logger = logging.getLogger(__name__)
    logger.info("🚀 Logging system initialized")
    logger.info(f"📊 Log level: {LOG_LEVEL}")
    logger.info(f"📁 Logs directory: {LOGS_DIR}")
    
def setup_component_loggers(formatter):
    """Setup specialized loggers for different components"""
    
    # Document processing logger
    doc_logger = logging.getLogger('document_pipeline')
    doc_handler = logging.handlers.RotatingFileHandler(
        filename=os.path.join(LOGS_DIR, "document_pipeline.log"),
        maxBytes=5*1024*1024,  # 5MB
        backupCount=3,
        encoding='utf-8'
    )
    doc_handler.setFormatter(formatter)
    doc_logger.addHandler(doc_handler)
    doc_logger.setLevel(logging.DEBUG)
    
    # Message processing logger
    msg_logger = logging.getLogger('message_pipeline')
    msg_handler = logging.handlers.RotatingFileHandler(
        filename=os.path.join(LOGS_DIR, "message_pipeline.log"),
        maxBytes=5*1024*1024,  # 5MB
        backupCount=3,
        encoding='utf-8'
    )
    msg_handler.setFormatter(formatter)
    msg_logger.addHandler(msg_handler)
    msg_logger.setLevel(logging.DEBUG)
    
    # Embedding service logger
    embed_logger = logging.getLogger('embedding_service')
    embed_handler = logging.handlers.RotatingFileHandler(
        filename=os.path.join(LOGS_DIR, "embedding_service.log"),
        maxBytes=5*1024*1024,  # 5MB
        backupCount=3,
        encoding='utf-8'
    )
    embed_handler.setFormatter(formatter)
    embed_logger.addHandler(embed_handler)
    embed_logger.setLevel(logging.DEBUG)
    
    # Database operations logger
    db_logger = logging.getLogger('database')
    db_handler = logging.handlers.RotatingFileHandler(
        filename=os.path.join(LOGS_DIR, "database.log"),
        maxBytes=5*1024*1024,  # 5MB
        backupCount=3,
        encoding='utf-8'
    )
    db_handler.setFormatter(formatter)
    db_logger.addHandler(db_handler)
    db_logger.setLevel(logging.DEBUG)
    
    # Performance logger
    perf_logger = logging.getLogger('performance')
    perf_handler = logging.handlers.RotatingFileHandler(
        filename=os.path.join(LOGS_DIR, "performance.log"),
        maxBytes=5*1024*1024,  # 5MB
        backupCount=3,
        encoding='utf-8'
    )
    perf_handler.setFormatter(formatter)
    perf_logger.addHandler(perf_handler)
    perf_logger.setLevel(logging.DEBUG)
    
    # User interactions logger
    user_logger = logging.getLogger('user_interactions')
    user_handler = logging.handlers.RotatingFileHandler(
        filename=os.path.join(LOGS_DIR, "user_interactions.log"),
        maxBytes=5*1024*1024,  # 5MB
        backupCount=3,
        encoding='utf-8'
    )
    user_handler.setFormatter(formatter)
    user_logger.addHandler(user_handler)
    user_logger.setLevel(logging.INFO)

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
                
                # Also log to performance logger
                perf_logger = logging.getLogger('performance')
                perf_logger.info(f"{func.__name__} completed in {duration:.3f}s", extra={
                    'operation': func.__name__,
                    'duration': duration,
                    'status': 'success'
                })
                return result
            except Exception as e:
                duration = time.time() - start_time
                logger.error(f"❌ {func.__name__} failed after {duration:.3f}s: {str(e)}")
                
                # Also log to performance logger
                perf_logger = logging.getLogger('performance')
                perf_logger.error(f"{func.__name__} failed in {duration:.3f}s: {str(e)}", extra={
                    'operation': func.__name__,
                    'duration': duration,
                    'status': 'error',
                    'error': str(e)
                })
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
                
                # Also log to performance logger
                perf_logger = logging.getLogger('performance')
                perf_logger.info(f"{func.__name__} completed in {duration:.3f}s", extra={
                    'operation': func.__name__,
                    'duration': duration,
                    'status': 'success'
                })
                return result
            except Exception as e:
                duration = time.time() - start_time
                logger.error(f"❌ {func.__name__} failed after {duration:.3f}s: {str(e)}")
                
                # Also log to performance logger
                perf_logger = logging.getLogger('performance')
                perf_logger.error(f"{func.__name__} failed in {duration:.3f}s: {str(e)}", extra={
                    'operation': func.__name__,
                    'duration': duration,
                    'status': 'error',
                    'error': str(e)
                })
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
    interaction_logger = logging.getLogger('user_interactions')
    
    log_data = {
        'user_id': user_id,
        'username': username,
        'action': action,
        'timestamp': time.time()
    }
    
    if details:
        log_data.update(details)
    
    interaction_logger.info(
        f"👤 User {username} ({user_id}) performed {action}",
        extra=log_data
    )

def log_error_with_context(logger: logging.Logger, error: Exception, context: Dict[str, Any]):
    """Log error with additional context information."""
    logger.error(
        f"💥 Error occurred: {str(error)}",
        extra={
            'error_type': type(error).__name__,
            'error_message': str(error),
            'context': context
        },
        exc_info=True
    )

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
    
    def _log_with_context(self, level: int, message: str, **kwargs):
        """Log message with context."""
        extra = {**self.context, **kwargs}
        self.logger.log(level, message, extra=extra)
    
    def debug(self, message: str, **kwargs):
        self._log_with_context(logging.DEBUG, message, **kwargs)
    
    def info(self, message: str, **kwargs):
        self._log_with_context(logging.INFO, message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        self._log_with_context(logging.WARNING, message, **kwargs)
    
    def error(self, message: str, **kwargs):
        self._log_with_context(logging.ERROR, message, **kwargs)
    
    def critical(self, message: str, **kwargs):
        self._log_with_context(logging.CRITICAL, message, **kwargs)

# Ensure setup_logging is called when module is imported
try:
    setup_logging()
except Exception as e:
    # Fallback to basic logging if setup fails
    logging.basicConfig(level=logging.INFO)
