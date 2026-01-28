"""
User Model for MongoDB
Supports Admin, SubAdmin, and User roles
"""

from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field, EmailStr
from bson import ObjectId


class PyObjectId(str):
    """Custom ObjectId type for Pydantic"""
    
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    
    @classmethod
    def validate(cls, v, info=None):
        if isinstance(v, ObjectId):
            return str(v)
        if isinstance(v, str) and ObjectId.is_valid(v):
            return v
        raise ValueError("Invalid ObjectId")


# Role type definition
UserRole = Literal["admin", "subadmin", "user"]


class UserDocument:
    """
    User document structure for MongoDB.
    
    Attributes:
        _id: MongoDB ObjectId
        email: Unique email address
        password: Bcrypt hashed password
        name: User's display name
        role: One of 'admin', 'subadmin', 'user'
        is_active: Account activation status
        created_at: Account creation timestamp
        updated_at: Last update timestamp
    """
    
    @staticmethod
    def create_document(
        email: str,
        hashed_password: str,
        name: str,
        role: UserRole = "user"
    ) -> dict:
        """Create a new user document"""
        now = datetime.utcnow()
        return {
            "email": email.lower(),
            "password": hashed_password,
            "name": name,
            "role": role,
            "is_active": True,
            "wishlist": [],
            "cart": [],
            "created_at": now,
            "updated_at": now
        }


class UserInDB(BaseModel):
    """User model as stored in database"""
    id: Optional[str] = Field(default=None, alias="_id")
    email: EmailStr
    password: str
    name: str
    role: UserRole = "user"
    is_active: bool = True
    wishlist: list = []
    cart: list = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}
