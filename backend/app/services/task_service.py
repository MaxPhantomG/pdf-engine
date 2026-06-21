from typing import Any

def enqueue_processing_task(func, *args, **kwargs) -> Any:
    return func(*args, **kwargs)
