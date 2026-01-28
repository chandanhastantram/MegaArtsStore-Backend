"""
Rate Limiting Middleware
Protects API from abuse using sliding window rate limiting
"""

from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from collections import defaultdict
from datetime import datetime, timedelta
import asyncio
from typing import Dict, Tuple


class RateLimiter:
    """
    Sliding window rate limiter.
    
    Tracks requests per IP/user and enforces limits.
    """
    
    def __init__(
        self,
        requests_per_minute: int = 60,
        requests_per_hour: int = 1000,
        burst_limit: int = 10
    ):
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        self.burst_limit = burst_limit
        
        # Request tracking
        self.minute_requests: Dict[str, list] = defaultdict(list)
        self.hour_requests: Dict[str, list] = defaultdict(list)
        
        # Cleanup lock
        self._lock = asyncio.Lock()
    
    async def is_allowed(self, identifier: str) -> Tuple[bool, str]:
        """
        Check if request is allowed.
        
        Args:
            identifier: IP address or user ID
        
        Returns:
            Tuple of (allowed, reason)
        """
        now = datetime.utcnow()
        
        async with self._lock:
            # Clean old entries
            await self._cleanup(identifier, now)
            
            # Check minute limit
            minute_count = len(self.minute_requests[identifier])
            if minute_count >= self.requests_per_minute:
                return False, f"Rate limit exceeded: {self.requests_per_minute}/min"
            
            # Check hour limit
            hour_count = len(self.hour_requests[identifier])
            if hour_count >= self.requests_per_hour:
                return False, f"Rate limit exceeded: {self.requests_per_hour}/hour"
            
            # Check burst (last second)
            one_second_ago = now - timedelta(seconds=1)
            recent = [t for t in self.minute_requests[identifier] if t > one_second_ago]
            if len(recent) >= self.burst_limit:
                return False, f"Burst limit exceeded: {self.burst_limit}/sec"
            
            # Record request
            self.minute_requests[identifier].append(now)
            self.hour_requests[identifier].append(now)
            
            return True, "OK"
    
    async def _cleanup(self, identifier: str, now: datetime):
        """Clean old request records"""
        one_minute_ago = now - timedelta(minutes=1)
        one_hour_ago = now - timedelta(hours=1)
        
        # Clean minute window
        self.minute_requests[identifier] = [
            t for t in self.minute_requests[identifier]
            if t > one_minute_ago
        ]
        
        # Clean hour window
        self.hour_requests[identifier] = [
            t for t in self.hour_requests[identifier]
            if t > one_hour_ago
        ]
    
    def get_limits_info(self, identifier: str) -> dict:
        """Get current rate limit info for identifier"""
        return {
            "requests_per_minute": self.requests_per_minute,
            "requests_per_hour": self.requests_per_hour,
            "current_minute_count": len(self.minute_requests.get(identifier, [])),
            "current_hour_count": len(self.hour_requests.get(identifier, []))
        }


# Global rate limiter instance
rate_limiter = RateLimiter(
    requests_per_minute=100,
    requests_per_hour=2000,
    burst_limit=20
)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware for FastAPI.
    
    Applies rate limiting based on client IP.
    """
    
    # Paths to skip rate limiting
    SKIP_PATHS = [
        "/docs",
        "/redoc",
        "/openapi.json",
        "/health",
        "/"
    ]
    
    async def dispatch(self, request: Request, call_next):
        # Skip for certain paths
        if request.url.path in self.SKIP_PATHS:
            return await call_next(request)
        
        # Get client identifier
        identifier = self._get_identifier(request)
        
        # Check rate limit
        allowed, reason = await rate_limiter.is_allowed(identifier)
        
        if not allowed:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=reason,
                headers={"Retry-After": "60"}
            )
        
        # Add rate limit headers to response
        response = await call_next(request)
        
        limits = rate_limiter.get_limits_info(identifier)
        response.headers["X-RateLimit-Limit"] = str(limits["requests_per_minute"])
        response.headers["X-RateLimit-Remaining"] = str(
            limits["requests_per_minute"] - limits["current_minute_count"]
        )
        
        return response
    
    def _get_identifier(self, request: Request) -> str:
        """Get unique identifier for rate limiting"""
        # Try to get real IP from headers (for proxies)
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # Fall back to client host
        return request.client.host if request.client else "unknown"


# ============ Endpoint-specific Rate Limiters ============

auth_rate_limiter = RateLimiter(
    requests_per_minute=10,  # Stricter for auth
    requests_per_hour=100,
    burst_limit=3
)


async def check_auth_rate_limit(request: Request) -> bool:
    """
    Dependency for auth endpoints.
    
    Usage:
        @router.post("/login")
        async def login(..., _=Depends(check_auth_rate_limit)):
    """
    identifier = request.client.host if request.client else "unknown"
    
    allowed, reason = await auth_rate_limiter.is_allowed(identifier)
    
    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many login attempts. Please try again later.",
            headers={"Retry-After": "300"}  # 5 minutes
        )
    
    return True
