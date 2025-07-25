"""
Logging configuration for the Telegram Multi-Agent AI Bot
Docker-friendly console logging with colors
"""

import logging
import time
import sys
from typing import Optional, Any, Dict
from functools import wraps

# Import LOG_LEVEL with fallback
try:
    from app.config import LOG_LEVEL
except ImportError:
    import os
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# ANSI Color codes for terminal output
class Colors:
    # Reset
    RESET = '\033[0m'
    
    # Regular colors
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    # Bright colors
    BRIGHT_BLACK = '\033[90m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'
    
    # Background colors
    BG_BLACK = '\033[40m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'
    BG_MAGENTA = '\033[45m'
    BG_CYAN = '\033[46m'
    BG_WHITE = '\033[47m'
    
    # Styles
    BOLD = '\033[1m'
    DIM = '\033[2m'
    UNDERLINE = '\033[4m'

class ColoredFormatter(logging.Formatter):
    """Custom formatter that adds colors to log levels and messages"""
    
    # Color mapping for different log levels
    LEVEL_COLORS = {
        'DEBUG': Colors.BRIGHT_BLACK,
        'INFO': Colors.BRIGHT_BLUE,
        'WARNING': Colors.BRIGHT_YELLOW,
        'ERROR': Colors.BRIGHT_RED,
        'CRITICAL': Colors.BG_RED + Colors.BRIGHT_WHITE + Colors.BOLD,
    }
    
    # Component color mapping
    COMPONENT_COLORS = {
        'document_pipeline': Colors.GREEN,
        'message_pipeline': Colors.CYAN,
        'embedding_service': Colors.MAGENTA,
        'database': Colors.YELLOW,
        'performance': Colors.BRIGHT_MAGENTA,
        'user_interactions': Colors.BRIGHT_CYAN,
        'bot': Colors.BRIGHT_GREEN,
    }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Check if we're in a terminal that supports colors
        self.use_colors = hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()
    
    def format(self, record):
        if not self.use_colors:
            return super().format(record)
        
        # Get the base formatted message
        formatted = super().format(record)
        
        # Color the log level
        level_color = self.LEVEL_COLORS.get(record.levelname, Colors.WHITE)
        colored_level = f"{level_color}{record.levelname}{Colors.RESET}"
        
        # Color the component name if present
        component_name = record.name.split('.')[-1] if '.' in record.name else record.name
        component_color = self.COMPONENT_COLORS.get(component_name, Colors.WHITE)
        
        # Replace the level name with colored version
        formatted = formatted.replace(record.levelname, colored_level)
        
        # Add component color to the message if it contains emojis or specific patterns
        message = record.getMessage()
        
        # Color specific emoji patterns
        emoji_colors = {
            '🚀': Colors.BRIGHT_GREEN,
            '✅': Colors.BRIGHT_GREEN,
            '❌': Colors.BRIGHT_RED,
            '⚠️': Colors.BRIGHT_YELLOW,
            '💥': Colors.RED + Colors.BOLD,
            '🔍': Colors.CYAN,
            '📊': Colors.BLUE,
            '👤': Colors.MAGENTA,
            '🎯': Colors.YELLOW,
            '📝': Colors.GREEN,
            '🔢': Colors.MAGENTA,
            '🗃️': Colors.YELLOW,
            '🔗': Colors.CYAN,
            '💾': Colors.BLUE,
            '📋': Colors.GREEN,
            '📄': Colors.WHITE,
        }
        
        # Apply emoji colors
        colored_message = message
        for emoji, color in emoji_colors.items():
            if emoji in colored_message:
                colored_message = colored_message.replace(emoji, f"{color}{emoji}{Colors.RESET}")
        
        # Replace the original message with colored version
        formatted = formatted.replace(message, colored_message)
        
        return formatted

def setup_logging():
    """Configure logging for the entire application - Docker console with colors"""
    
    # Create colored console formatter
    colored_formatter = ColoredFormatter(
        fmt="%(asctime)s - %(levelname)s - [%(name)s] %(message)s",
        datefmt="%H:%M:%S"
    )
    
    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, LOG_LEVEL.upper()))
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Console handler with colors - Docker will capture this
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(colored_formatter)
    root_logger.addHandler(console_handler)
    
    # Log startup with colors
    logger = logging.getLogger(__name__)
    logger.info("🚀 Colorful logging system initialized")
    logger.info(f"📊 Log level: {LOG_LEVEL}")
    logger.info("🎨 Using colored console logging (Docker will capture)")
    
def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for a specific component"""
    return logging.getLogger(name)

# Performance logging decorator with colors
def log_performance(logger_name: Optional[str] = None):
    """Decorator to log function performance with colored output"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger = logging.getLogger(logger_name or func.__module__)
            start_time = time.time()
            
            logger.debug(f"🚀 Starting {Colors.BOLD}{func.__name__}{Colors.RESET} with args={len(args)}, kwargs={list(kwargs.keys())}")
            
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                logger.info(f"✅ {Colors.BOLD}{func.__name__}{Colors.RESET} completed in {Colors.BRIGHT_GREEN}{duration:.3f}s{Colors.RESET}")
                return result
            except Exception as e:
                duration = time.time() - start_time
                logger.error(f"❌ {Colors.BOLD}{func.__name__}{Colors.RESET} failed after {Colors.BRIGHT_RED}{duration:.3f}s{Colors.RESET}: {str(e)}")
                raise
        return wrapper
    return decorator

# Async performance logging decorator with colors
def log_async_performance(logger_name: Optional[str] = None):
    """Decorator to log async function performance with colored output"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            logger = logging.getLogger(logger_name or func.__module__)
            start_time = time.time()
            
            logger.debug(f"🚀 Starting async {Colors.BOLD}{func.__name__}{Colors.RESET} with args={len(args)}, kwargs={list(kwargs.keys())}")
            
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                logger.info(f"✅ {Colors.BOLD}{func.__name__}{Colors.RESET} completed in {Colors.BRIGHT_GREEN}{duration:.3f}s{Colors.RESET}")
                return result
            except Exception as e:
                duration = time.time() - start_time
                logger.error(f"❌ {Colors.BOLD}{func.__name__}{Colors.RESET} failed after {Colors.BRIGHT_RED}{duration:.3f}s{Colors.RESET}: {str(e)}")
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
    """Log user interactions for analytics and debugging with colors."""
    logger = logging.getLogger('user_interactions')
    
    details_str = f" - {Colors.DIM}{details}{Colors.RESET}" if details else ""
    logger.info(f"👤 User {Colors.BRIGHT_CYAN}{username}{Colors.RESET} ({Colors.YELLOW}{user_id}{Colors.RESET}) performed {Colors.BOLD}{action}{Colors.RESET}{details_str}")

def log_error_with_context(logger: logging.Logger, error: Exception, context: Dict[str, Any]):
    """Log error with additional context information and colors."""
    context_str = ", ".join([f"{Colors.CYAN}{k}{Colors.RESET}={Colors.YELLOW}{v}{Colors.RESET}" for k, v in context.items()])
    logger.error(f"💥 Error occurred: {Colors.BRIGHT_RED}{str(error)}{Colors.RESET} | Context: {context_str}", exc_info=True)

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
