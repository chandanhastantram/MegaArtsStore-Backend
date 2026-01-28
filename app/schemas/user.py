"""
User Pydantic Schemas
Request/Response models for user endpoints
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime


# ============ Request Schemas ============

class UserCreate(BaseModel):
    """Schema for user registration"""
    email: EmailStr
    password: str = Field(min_length=8, description="Minimum 8 characters")
    name: str = Field(min_length=2, max_length=100)


class UserLogin(BaseModel):
    """Schema for user login"""
    email: EmailStr
    password: str


class SubAdminCreate(BaseModel):
    """Schema for creating sub-admin (Admin only)"""
    email: EmailStr
    password: str = Field(min_length=8)
    name: str = Field(min_length=2, max_length=100)


class UserUpdate(BaseModel):
    """Schema for updating user profile"""
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    password: Optional[str] = Field(None, min_length=8)


# ============ Response Schemas ============

class UserResponse(BaseModel):
    """Schema for user response (excludes password)"""
    id: str
    email: EmailStr
    name: str
    role: str
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    """Schema for JWT token response"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class TokenData(BaseModel):
    """Schema for decoded JWT token data"""
    user_id: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None


# ============ Admin Response Schemas ============

class UserListResponse(BaseModel):
    """Schema for paginated user list (Admin)"""
    users: List[UserResponse]
    total: int
    page: int
    per_page: int
