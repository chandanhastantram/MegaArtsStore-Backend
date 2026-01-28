"""
Coupon Model
Discount and coupon code management
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from bson import ObjectId


class CouponDocument(BaseModel):
    """Coupon database model"""
    id: Optional[str] = Field(default=None, alias="_id")
    code: str  # Unique coupon code
    description: str
    discount_type: str  # "percentage" or "fixed"
    discount_value: float  # Percentage (0-100) or fixed amount
    min_order_value: Optional[float] = 0.0
    max_discount: Optional[float] = None  # Max discount for percentage type
    usage_limit: Optional[int] = None  # Total usage limit
    usage_count: int = 0  # Current usage count
    user_usage_limit: Optional[int] = 1  # Per user usage limit
    valid_from: datetime
    valid_until: datetime
    is_active: bool = True
    applicable_categories: Optional[list] = []  # Empty = all categories
    applicable_products: Optional[list] = []  # Empty = all products
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: str  # Admin user ID

    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}


class CouponUsageDocument(BaseModel):
    """Track coupon usage by users"""
    id: Optional[str] = Field(default=None, alias="_id")
    coupon_id: str
    user_id: str
    order_id: str
    discount_applied: float
    used_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}
