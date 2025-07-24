"""
Simple in-memory cache for improved performance
"""
import time
from typing import Any, Optional

class SimpleCache:
    def __init__(self):
        self._cache = {}
        self._timestamps = {}
    
    def get(self, key: str, default_ttl: int = 300) -> Optional[Any]:
        """Get cached value if not expired"""
        if key in self._cache:
            timestamp = self._timestamps.get(key, 0)
            if time.time() - timestamp < default_ttl:
                return self._cache[key]
            else:
                # Clean expired entry
                self._cache.pop(key, None)
                self._timestamps.pop(key, None)
        return None
    
    def set(self, key: str, value: Any) -> None:
        """Set cached value with current timestamp"""
        self._cache[key] = value
        self._timestamps[key] = time.time()
    
    def clear(self) -> None:
        """Clear all cached entries"""
        self._cache.clear()
        self._timestamps.clear()

# Global cache instance
cache = SimpleCache()