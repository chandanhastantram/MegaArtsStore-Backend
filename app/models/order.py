"""
Order Model for MongoDB
Supports order creation and tracking
"""

from datetime import datetime
from typing import Optional, List, Literal
from pydantic import BaseModel, Field
from bson import ObjectId


# Order status types
OrderStatus = Literal["pending", "confirmed", "processing", "shipped", "delivered", "cancelled"]


class ShippingAddress(BaseModel):
    """Shipping address embedded document"""
    full_name: str
    phone: str
    address_line_1: str
    address_line_2: Optional[str] = None
    city: str
    state: str
    pincode: str
    country: str = "India"


class OrderItem(BaseModel):
    """Order item embedded document"""
    product_id: str
    product_name: str
    product_image: str
    size: str
    quantity: int = Field(ge=1)
    price: float
    subtotal: float


class OrderDocument:
    """
    Order document structure for MongoDB.
    
    Attributes:
        _id: MongoDB ObjectId
        order_id: Human-readable order ID (e.g., MAS-2024-001)
        user_id: User ID who placed the order
        items: List of order items
        subtotal: Total before shipping/tax
        shipping_cost: Shipping charges
        tax: GST/tax amount
        total: Final order total
        status: Order status
        shipping_address: Delivery address
        payment_status: Payment status
        payment_id: Razorpay payment ID (if applicable)
        created_at: Order placement timestamp
        updated_at: Last update timestamp
    """
    
    @staticmethod
    def generate_order_id() -> str:
        """Generate human-readable order ID"""
        from datetime import datetime
        import random
        year = datetime.now().year
        random_num = random.randint(1000, 9999)
        return f"MAS-{year}-{random_num}"
    
    @staticmethod
    def create_document(
        user_id: str,
        items: List[dict],
        shipping_address: dict,
        subtotal: float,
        shipping_cost: float = 0,
        tax: float = 0
    ) -> dict:
        """Create a new order document"""
        now = datetime.utcnow()
        return {
            "order_id": OrderDocument.generate_order_id(),
            "user_id": user_id,
            "items": items,
            "subtotal": subtotal,
            "shipping_cost": shipping_cost,
            "tax": tax,
            "total": subtotal + shipping_cost + tax,
            "status": "pending",
            "shipping_address": shipping_address,
            "payment_status": "pending",
            "payment_id": None,
            "created_at": now,
            "updated_at": now
        }


class OrderInDB(BaseModel):
    """Order model as stored in database"""
    id: Optional[str] = Field(default=None, alias="_id")
    order_id: str
    user_id: str
    items: List[OrderItem]
    subtotal: float
    shipping_cost: float = 0
    tax: float = 0
    total: float
    status: OrderStatus = "pending"
    shipping_address: ShippingAddress
    payment_status: str = "pending"
    payment_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}
