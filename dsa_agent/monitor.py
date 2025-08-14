import asyncio
import time
from functools import wraps

from .logger import logger


def _log_execution_time(start_time: float, func_name: str, component_type: str = None):
    end_time = time.perf_counter()
    execution_time = end_time - start_time
    component = component_type or func_name
    logger.info(f"\n{component} {func_name} took {execution_time:.4f} seconds\n")


def time_component(component_type: str = None):
    def decorator(func):
        if asyncio.iscoroutinefunction(func):

            @wraps(func)
            async def wrapper(*args, **kwargs):
                start_time = time.perf_counter()
                result = await func(*args, **kwargs)
                _log_execution_time(start_time, func.__name__, component_type)
                return result

        else:

            @wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.perf_counter()
                result = func(*args, **kwargs)
                _log_execution_time(start_time, func.__name__, component_type)
                return result

        return wrapper

    return decorator
