"""
Coupon Schemas
Request and response schemas for coupon management
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, validator


class CouponCreate(BaseModel):
    """Schema for creating a new coupon"""
    code: str = Field(..., min_length=3, max_length=50)
    description: str
    discount_type: str = Field(..., pattern="^(percentage|fixed)$")
    discount_value: float = Field(..., gt=0)
    min_order_value: Optional[float] = 0.0
    max_discount: Optional[float] = None
    usage_limit: Optional[int] = None
    user_usage_limit: Optional[int] = 1
    valid_from: datetime
    valid_until: datetime
    applicable_categories: Optional[List[str]] = []
    applicable_products: Optional[List[str]] = []

    @validator('discount_value')
    def validate_discount_value(cls, v, values):
        if values.get('discount_type') == 'percentage' and (v < 0 or v > 100):
            raise ValueError('Percentage discount must be between 0 and 100')
        return v

    @validator('valid_until')
    def validate_dates(cls, v, values):
        if 'valid_from' in values and v <= values['valid_from']:
            raise ValueError('valid_until must be after valid_from')
        return v


class CouponUpdate(BaseModel):
    """Schema for updating a coupon"""
    description: Optional[str] = None
    discount_value: Optional[float] = None
    min_order_value: Optional[float] = None
    max_discount: Optional[float] = None
    usage_limit: Optional[int] = None
    user_usage_limit: Optional[int] = None
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None
    is_active: Optional[bool] = None
    applicable_categories: Optional[List[str]] = None
    applicable_products: Optional[List[str]] = None


class CouponValidate(BaseModel):
    """Schema for validating a coupon"""
    code: str
    user_id: str
    order_value: float
    product_ids: Optional[List[str]] = []
    category_ids: Optional[List[str]] = []


class CouponResponse(BaseModel):
    """Schema for coupon response"""
    id: str
    code: str
    description: str
    discount_type: str
    discount_value: float
    min_order_value: float
    max_discount: Optional[float]
    usage_limit: Optional[int]
    usage_count: int
    user_usage_limit: int
    valid_from: datetime
    valid_until: datetime
    is_active: bool
    applicable_categories: List[str]
    applicable_products: List[str]
    created_at: datetime

    class Config:
        from_attributes = True


class CouponValidationResponse(BaseModel):
    """Schema for coupon validation response"""
    valid: bool
    message: str
    discount_amount: Optional[float] = 0.0
    final_amount: Optional[float] = None
    coupon: Optional[CouponResponse] = None
