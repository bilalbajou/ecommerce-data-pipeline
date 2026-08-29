import logging
import sys

def get_logger(name: str) -> logging.Logger:
    """Returns a structured logger for the ETL pipeline."""
    logger = logging.getLogger(name)
    
    # Avoid adding multiple handlers if get_logger is called multiple times
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        
        # We use a structured, predictable text format, making it easy to parse
        # e.g. [2023-10-27 10:00:00] [INFO] [extract] - Starting extraction...
        formatter = logging.Formatter(
            fmt='[%(asctime)s] [%(levelname)s] [%(name)s] - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Log to standard output
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        # Prevent propagation to the root logger to avoid duplicate logs
        logger.propagate = False
        
    return logger
