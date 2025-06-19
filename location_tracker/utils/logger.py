import logging
from logging.handlers import RotatingFileHandler
import os

def setup_logger(name):
    """Configure logger with rotation."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        handler = RotatingFileHandler(
            "location_tracker.log",
            maxBytes=5*1024*1024,  # 5MB
            backupCount=3
        )
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger