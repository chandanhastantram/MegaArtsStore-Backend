"""
Product Pydantic Schemas
Request/Response models for product endpoints
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# ============ Request Schemas ============

class ProductCreate(BaseModel):
    """Schema for creating a new product"""
    name: str = Field(min_length=2, max_length=200)
    description: str = Field(min_length=10, max_length=2000)
    price: float = Field(gt=0)
    category: str
    material: str = Field(pattern="^(gold|silver|kundan|diamond|platinum)$")
    sizes: List[str] = ["S", "M", "L"]
    stock: int = Field(ge=0, default=0)


class ProductUpdate(BaseModel):
    """Schema for updating a product"""
    name: Optional[str] = Field(None, min_length=2, max_length=200)
    description: Optional[str] = Field(None, min_length=10, max_length=2000)
    price: Optional[float] = Field(None, gt=0)
    category: Optional[str] = None
    material: Optional[str] = Field(None, pattern="^(gold|silver|kundan|diamond|platinum)$")
    sizes: Optional[List[str]] = None
    stock: Optional[int] = Field(None, ge=0)
    visibility: Optional[bool] = None
    featured: Optional[bool] = None
    ar_enabled: Optional[bool] = None


class ProductFilter(BaseModel):
    """Schema for filtering products"""
    category: Optional[str] = None
    material: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    search: Optional[str] = None
    ar_enabled: Optional[bool] = None
    featured: Optional[bool] = None


class ReviewCreate(BaseModel):
    """Schema for creating a product review"""
    rating: int = Field(ge=1, le=5)
    comment: str = Field(min_length=10, max_length=1000)


# ============ Response Schemas ============

class ARConfigResponse(BaseModel):
    """Schema for AR configuration response"""
    scale: float
    rotation: List[float]
    offset: List[float]
    wrist_diameter: float


class ReviewResponse(BaseModel):
    """Schema for review response"""
    user_id: str
    user_name: str
    rating: int
    comment: str
    created_at: datetime


class ProductResponse(BaseModel):
    """Schema for product response"""
    id: str
    name: str
    description: str
    price: float
    category: str
    material: str
    sizes: List[str]
    images: List[str]
    model_3d: Optional[str] = None
    ar_enabled: bool
    ar_config: Optional[ARConfigResponse] = None
    visibility: bool
    featured: bool
    stock: int
    reviews: List[ReviewResponse] = []
    avg_rating: float
    created_at: datetime
    
    class Config:
        from_attributes = True


class ProductListResponse(BaseModel):
    """Schema for paginated product list"""
    products: List[ProductResponse]
    total: int
    page: int
    per_page: int


# ============ Category Schemas ============

class CategoryCreate(BaseModel):
    """Schema for creating a category"""
    name: str = Field(min_length=2, max_length=100)
    description: Optional[str] = None
    image: Optional[str] = None


class CategoryResponse(BaseModel):
    """Schema for category response"""
    id: str
    name: str
    description: Optional[str] = None
    image: Optional[str] = None
    product_count: int = 0
