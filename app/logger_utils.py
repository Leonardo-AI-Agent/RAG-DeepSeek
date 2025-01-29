# app/logger_utils.py

import time
from loguru import logger

def log_performance(func):
    """
    Decorator to log function execution time.
    
    Args:
        func (function): The function whose execution time needs to be logged.

    Returns:
        function: Wrapped function with execution time logging.
    """
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        execution_time = time.time() - start_time

        # Log execution details
        logger.info(f"Function '{func.__name__}' executed in {execution_time:.4f} seconds.")

        return result
    return wrapper
