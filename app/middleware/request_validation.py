"""
Request Validation Middleware
Input sanitization and security validation
"""

from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
import re
from typing import Any, Dict, List
import html


class RequestValidator:
    """
    Request validation and sanitization utilities.
    """
    
    # Patterns for dangerous input
    SQL_INJECTION_PATTERNS = [
        r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|UNION|ALTER|CREATE|TRUNCATE)\b)",
        r"(--|\#|\/\*|\*\/)",
        r"(\bOR\b|\bAND\b)\s+\d+\s*=\s*\d+",
    ]
    
    XSS_PATTERNS = [
        r"<script[^>]*>.*?</script>",
        r"javascript:",
        r"on\w+\s*=",
        r"<iframe[^>]*>",
    ]
    
    PATH_TRAVERSAL_PATTERNS = [
        r"\.\./",
        r"\.\.\\",
        r"%2e%2e",
    ]
    
    # Maximum sizes
    MAX_STRING_LENGTH = 10000
    MAX_ARRAY_LENGTH = 100
    MAX_OBJECT_DEPTH = 10
    
    @classmethod
    def sanitize_string(cls, value: str) -> str:
        """Sanitize a string value"""
        if not isinstance(value, str):
            return value
        
        # Trim excessive length
        if len(value) > cls.MAX_STRING_LENGTH:
            value = value[:cls.MAX_STRING_LENGTH]
        
        # HTML escape
        value = html.escape(value)
        
        return value
    
    @classmethod
    def check_sql_injection(cls, value: str) -> bool:
        """Check if value contains potential SQL injection"""
        if not isinstance(value, str):
            return False
        
        value_upper = value.upper()
        for pattern in cls.SQL_INJECTION_PATTERNS:
            if re.search(pattern, value_upper, re.IGNORECASE):
                return True
        return False
    
    @classmethod
    def check_xss(cls, value: str) -> bool:
        """Check if value contains potential XSS"""
        if not isinstance(value, str):
            return False
        
        for pattern in cls.XSS_PATTERNS:
            if re.search(pattern, value, re.IGNORECASE):
                return True
        return False
    
    @classmethod
    def check_path_traversal(cls, value: str) -> bool:
        """Check if value contains path traversal attempt"""
        if not isinstance(value, str):
            return False
        
        for pattern in cls.PATH_TRAVERSAL_PATTERNS:
            if re.search(pattern, value, re.IGNORECASE):
                return True
        return False
    
    @classmethod
    def validate_and_sanitize(cls, data: Any, depth: int = 0) -> Any:
        """
        Recursively validate and sanitize data.
        
        Args:
            data: Input data (dict, list, or scalar)
            depth: Current nesting depth
        
        Returns:
            Sanitized data
        
        Raises:
            ValueError: If dangerous input detected
        """
        if depth > cls.MAX_OBJECT_DEPTH:
            raise ValueError("Object nesting too deep")
        
        if isinstance(data, dict):
            return {
                cls.sanitize_string(k): cls.validate_and_sanitize(v, depth + 1)
                for k, v in data.items()
            }
        
        elif isinstance(data, list):
            if len(data) > cls.MAX_ARRAY_LENGTH:
                raise ValueError(f"Array too large (max {cls.MAX_ARRAY_LENGTH})")
            return [cls.validate_and_sanitize(item, depth + 1) for item in data]
        
        elif isinstance(data, str):
            # Check for attacks
            if cls.check_sql_injection(data):
                raise ValueError("Potential SQL injection detected")
            if cls.check_xss(data):
                raise ValueError("Potential XSS detected")
            if cls.check_path_traversal(data):
                raise ValueError("Potential path traversal detected")
            
            return cls.sanitize_string(data)
        
        else:
            return data


class ValidationMiddleware(BaseHTTPMiddleware):
    """
    Request validation middleware.
    
    Validates and sanitizes incoming requests.
    """
    
    # Paths to skip validation
    SKIP_PATHS = [
        "/docs",
        "/redoc",
        "/openapi.json",
    ]
    
    # Content types to validate
    VALIDATE_CONTENT_TYPES = [
        "application/json",
        "application/x-www-form-urlencoded",
    ]
    
    async def dispatch(self, request: Request, call_next):
        # Skip for certain paths
        if request.url.path in self.SKIP_PATHS:
            return await call_next(request)
        
        # Validate content length
        content_length = request.headers.get("content-length")
        if content_length:
            try:
                length = int(content_length)
                if length > 10 * 1024 * 1024:  # 10MB max
                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail="Request body too large"
                    )
            except ValueError:
                pass
        
        # Validate query parameters
        try:
            for key, value in request.query_params.items():
                RequestValidator.validate_and_sanitize(value)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid query parameter: {str(e)}"
            )
        
        # Validate path parameters
        try:
            for key, value in request.path_params.items():
                RequestValidator.validate_and_sanitize(value)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid path parameter: {str(e)}"
            )
        
        return await call_next(request)


# ============ Input Validators ============

def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_phone(phone: str) -> bool:
    """Validate Indian phone number"""
    # Remove spaces and dashes
    phone = re.sub(r'[\s-]', '', phone)
    
    # Check format: +91XXXXXXXXXX or XXXXXXXXXX
    pattern = r'^(\+91)?[6-9]\d{9}$'
    return bool(re.match(pattern, phone))


def validate_pincode(pincode: str) -> bool:
    """Validate Indian pincode"""
    pattern = r'^[1-9][0-9]{5}$'
    return bool(re.match(pattern, pincode))


def validate_order_id(order_id: str) -> bool:
    """Validate order ID format"""
    pattern = r'^ORD-[A-Z0-9]{8,12}$'
    return bool(re.match(pattern, order_id))


def sanitize_filename(filename: str) -> str:
    """Sanitize a filename for safe storage"""
    # Remove path separators
    filename = filename.replace("/", "").replace("\\", "")
    
    # Remove dangerous characters
    filename = re.sub(r'[<>:"|?*]', '', filename)
    
    # Limit length
    if len(filename) > 100:
        name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
        filename = name[:95] + '.' + ext if ext else name[:100]
    
    return filename
