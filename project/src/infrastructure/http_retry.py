import time
from functools import wraps
from typing import Callable, Any

def with_backoff(max_retries: int = 5, base_delay: float = 1.0, max_delay: float = 60.0) -> Callable:
    """Retries execution with exponential backoff on 429 or quota errors."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            retries = 0
            delay = base_delay
            while True:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    err_msg = str(e).lower()
                    if "429" in err_msg or "quota" in err_msg:
                        if retries >= max_retries:
                            raise
                        time.sleep(delay)
                        retries += 1
                        delay = min(delay * 2, max_delay)
                    else:
                        raise
        return wrapper
    return decorator
