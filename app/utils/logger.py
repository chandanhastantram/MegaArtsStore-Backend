"""
Logger Config
Structured logging configuration
"""

import logging
import sys
from app.config import get_settings

def setup_logging():
    """Configure structured logging"""
    settings = get_settings()
    
    # Set log level
    log_level = logging.DEBUG if settings.debug else logging.INFO
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    
    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.addHandler(console_handler)
    
    # Supress noisy libraries
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    
    return root_logger

logger = setup_logging()
