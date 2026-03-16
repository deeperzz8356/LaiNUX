import logging
import os

def setup_logger():
    """Sets up a basic logger for the Agentic OS."""
    logger = logging.getLogger("agentic_os")
    logger.setLevel(logging.INFO)
    
    # Create console handler
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    
    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    
    # Add handler to logger
    if not logger.handlers:
        logger.addHandler(ch)
        
    return logger

logger = setup_logger()
