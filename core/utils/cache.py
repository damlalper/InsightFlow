"""
Caching utilities using Redis.
"""
from functools import wraps
from typing import Callable, Any, Optional
from django.core.cache import cache
import hashlib
import json


def cached_result(key_prefix: str, timeout: int = 300):
    """
    Decorator to cache function results.
    
    Args:
        key_prefix: Prefix for cache key
        timeout: Cache timeout in seconds (default: 5 minutes)
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key from function name and arguments
            cache_key = f"{key_prefix}:{func.__name__}"
            if args or kwargs:
                key_data = json.dumps({
                    'args': str(args),
                    'kwargs': sorted(kwargs.items())
                }, sort_keys=True)
                key_hash = hashlib.md5(key_data.encode()).hexdigest()
                cache_key = f"{cache_key}:{key_hash}"
            
            # Try to get from cache
            result = cache.get(cache_key)
            if result is not None:
                return result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache.set(cache_key, result, timeout)
            return result
        
        return wrapper
    return decorator


def invalidate_cache(pattern: str):
    """
    Invalidate cache entries matching pattern.
    
    Note: This is a simplified version. In production, use Redis keys command
    with proper pattern matching.
    """
    # In production, implement proper cache invalidation
    # For now, this is a placeholder
    pass
