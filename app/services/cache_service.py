"""
Cache Service
Simple in-memory caching service
"""

from typing import Any, Optional
from datetime import datetime, timedelta
import asyncio

class CacheService:
    """
    Simple in-memory cache with TTL.
    """
    
    def __init__(self):
        self._cache = {}
        self._lock = asyncio.Lock()
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        async with self._lock:
            if key in self._cache:
                entry = self._cache[key]
                if datetime.utcnow() < entry["expire_at"]:
                    return entry["value"]
                else:
                    del self._cache[key]
        return None
    
    async def set(self, key: str, value: Any, ttl_seconds: int = 300):
        """Set value in cache"""
        async with self._lock:
            self._cache[key] = {
                "value": value,
                "expire_at": datetime.utcnow() + timedelta(seconds=ttl_seconds)
            }
            
    async def delete(self, key: str):
        """Delete value from cache"""
        async with self._lock:
            if key in self._cache:
                del self._cache[key]
                
    async def clear(self):
        """Clear all cache"""
        async with self._lock:
            self._cache.clear()

# Global cache instance
cache = CacheService()
