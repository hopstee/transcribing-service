import time
import logging
from functools import wraps

logging.getLogger(__name__)

def log_duration(step_name=None):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            name = step_name or func.__name__
            start = time.time()
            result = func(*args, **kwargs)
            logging.info(f"{name} заняло {time.time() - start:.2f} сек")
            return result
        return wrapper
    return decorator
