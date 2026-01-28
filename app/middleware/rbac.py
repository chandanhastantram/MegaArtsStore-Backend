"""
Role-Based Access Control (RBAC) Middleware
Route protection based on user roles
"""

from functools import wraps
from typing import List, Callable
from fastapi import Depends, HTTPException, status

from app.utils.auth import get_current_user


class RoleChecker:
    """
    Dependency class for role-based access control.
    
    Usage:
        @router.get("/admin-only")
        async def admin_endpoint(user = Depends(RoleChecker(["admin"]))):
            ...
    """
    
    def __init__(self, allowed_roles: List[str]):
        """
        Initialize role checker.
        
        Args:
            allowed_roles: List of roles that can access the route
        """
        self.allowed_roles = allowed_roles
    
    async def __call__(self, current_user: dict = Depends(get_current_user)) -> dict:
        """
        Check if current user has required role.
        
        Args:
            current_user: User from JWT token
        
        Returns:
            User dict if authorized
        
        Raises:
            HTTPException: If user doesn't have required role
        """
        user_role = current_user.get("role", "user")
        
        if user_role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {', '.join(self.allowed_roles)}"
            )
        
        return current_user


# Pre-configured role checkers for convenience
require_admin = RoleChecker(["admin"])
require_admin_or_subadmin = RoleChecker(["admin", "subadmin"])
require_any_authenticated = RoleChecker(["admin", "subadmin", "user"])


async def get_admin_user(current_user: dict = Depends(require_admin)) -> dict:
    """Dependency that requires admin role"""
    return current_user


async def get_admin_or_subadmin(current_user: dict = Depends(require_admin_or_subadmin)) -> dict:
    """Dependency that requires admin or subadmin role"""
    return current_user


async def get_authenticated_user(current_user: dict = Depends(require_any_authenticated)) -> dict:
    """Dependency that requires any authenticated user"""
    return current_user


def role_required(allowed_roles: List[str]):
    """
    Decorator for role-based access control.
    Alternative to using Depends(RoleChecker(...)).
    
    Usage:
        @role_required(["admin", "subadmin"])
        async def some_function(current_user: dict):
            ...
    """
    checker = RoleChecker(allowed_roles)
    
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, current_user: dict = Depends(get_current_user), **kwargs):
            await checker(current_user)
            return await func(*args, current_user=current_user, **kwargs)
        return wrapper
    
    return decorator
