"""
INTELLI AI - Logging Module
Provides structured logging with file output and different log levels.
"""
import logging
import os
from datetime import datetime
from pathlib import Path

# Create logs directory if it doesn't exist
LOG_DIR = Path(__file__).parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

# Log file path with date
LOG_FILE = LOG_DIR / f"intelli_{datetime.now().strftime('%Y%m%d')}.log"

def setup_logger(name: str = "INTELLI", level: int = logging.INFO) -> logging.Logger:
    """
    Set up a logger with file and console handlers.
    
    Args:
        name: Logger name
        level: Logging level (default: INFO)
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Prevent duplicate handlers
    if logger.handlers:
        return logger
    
    # Formatter
    formatter = logging.Formatter(
        fmt='%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # File handler - logs to file
    file_handler = logging.FileHandler(LOG_FILE, encoding='utf-8')
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    
    # Console handler - logs to terminal
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)  # Only warnings and above to console
    console_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


# Default logger instance
logger = setup_logger("INTELLI")

def log_info(message: str):
    """Log an info message."""
    logger.info(message)

def log_warning(message: str):
    """Log a warning message."""
    logger.warning(message)

def log_error(message: str, exc_info: bool = False):
    """Log an error message with optional exception info."""
    logger.error(message, exc_info=exc_info)

def log_debug(message: str):
    """Log a debug message."""
    logger.debug(message)
