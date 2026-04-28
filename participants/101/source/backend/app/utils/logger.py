# backend/app/utils/logger.py
import logging
import os
from datetime import datetime


def setup_logger(name: str):
    """Setup logger configuration"""
    logger = logging.getLogger(name)

    if not logger.handlers:
        logger.setLevel(logging.INFO)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        # File handler
        os.makedirs("logs", exist_ok=True)
        file_handler = logging.FileHandler(f"logs/app_{datetime.now().strftime('%Y%m%d')}.log")
        file_handler.setLevel(logging.INFO)

        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)

        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

    return logger