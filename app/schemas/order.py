"""
Order Pydantic Schemas
Request/Response models for order endpoints
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# ============ Request Schemas ============

class ShippingAddressCreate(BaseModel):
    """Schema for shipping address"""
    full_name: str = Field(min_length=2, max_length=100)
    phone: str = Field(pattern=r"^\+?[0-9]{10,14}$")
    address_line_1: str = Field(min_length=5, max_length=200)
    address_line_2: Optional[str] = Field(None, max_length=200)
    city: str = Field(min_length=2, max_length=100)
    state: str = Field(min_length=2, max_length=100)
    pincode: str = Field(pattern=r"^[0-9]{6}$")
    country: str = "India"


class OrderItemCreate(BaseModel):
    """Schema for order item"""
    product_id: str
    size: str
    quantity: int = Field(ge=1, default=1)


class OrderCreate(BaseModel):
    """Schema for creating an order"""
    items: List[OrderItemCreate]
    shipping_address: ShippingAddressCreate


class OrderStatusUpdate(BaseModel):
    """Schema for updating order status (Admin)"""
    status: str = Field(pattern="^(pending|confirmed|processing|shipped|delivered|cancelled)$")


# ============ Response Schemas ============

class OrderItemResponse(BaseModel):
    """Schema for order item response"""
    product_id: str
    product_name: str
    product_image: str
    size: str
    quantity: int
    price: float
    subtotal: float


class ShippingAddressResponse(BaseModel):
    """Schema for shipping address response"""
    full_name: str
    phone: str
    address_line_1: str
    address_line_2: Optional[str] = None
    city: str
    state: str
    pincode: str
    country: str


class OrderResponse(BaseModel):
    """Schema for order response"""
    id: str
    order_id: str
    user_id: str
    items: List[OrderItemResponse]
    subtotal: float
    shipping_cost: float
    tax: float
    total: float
    status: str
    shipping_address: ShippingAddressResponse
    payment_status: str
    payment_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class OrderListResponse(BaseModel):
    """Schema for paginated order list"""
    orders: List[OrderResponse]
    total: int
    page: int
    per_page: int


# ============ Cart Schemas ============

class CartItem(BaseModel):
    """Schema for cart item"""
    product_id: str
    size: str
    quantity: int = Field(ge=1)


class CartResponse(BaseModel):
    """Schema for cart response"""
    items: List[OrderItemResponse]
    subtotal: float
    item_count: int
