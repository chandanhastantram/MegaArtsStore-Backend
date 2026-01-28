"""
Payment Routes
Razorpay payment processing endpoints
"""

from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from typing import Optional

from app.services import payment_service
from app.database import get_orders_collection
from app.utils.auth import get_current_user
from app.middleware.rbac import get_admin_user
from bson import ObjectId

router = APIRouter()


# ============ Schemas ============

class CreatePaymentRequest(BaseModel):
    """Schema for creating a payment"""
    order_id: str


class CreatePaymentResponse(BaseModel):
    """Schema for payment creation response"""
    razorpay_order_id: str
    amount: float
    amount_paise: int
    currency: str
    key_id: str


class VerifyPaymentRequest(BaseModel):
    """Schema for verifying payment"""
    order_id: str
    razorpay_payment_id: str
    razorpay_order_id: str
    razorpay_signature: str


class RefundRequest(BaseModel):
    """Schema for refund request"""
    order_id: str
    amount: Optional[float] = None
    reason: str = "requested_by_customer"


# ============ Routes ============

@router.post("/create", response_model=CreatePaymentResponse)
async def create_payment(
    request: CreatePaymentRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Create a Razorpay order for payment.
    
    - Returns Razorpay order ID and key for frontend integration
    """
    orders_collection = get_orders_collection()
    
    # Get order
    order = await orders_collection.find_one({"order_id": request.order_id})
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Verify ownership
    if order["user_id"] != current_user["_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Check if already paid
    if order.get("payment_status") == "paid":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order already paid"
        )
    
    # Create Razorpay order
    result = await payment_service.create_razorpay_order(
        order_id=request.order_id,
        amount=order["total"]
    )
    
    return CreatePaymentResponse(**result)


@router.post("/verify")
async def verify_payment(
    request: VerifyPaymentRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Verify and confirm payment after successful Razorpay transaction.
    
    - Called after Razorpay checkout success
    - Verifies signature and updates order status
    """
    result = await payment_service.confirm_payment(
        order_id=request.order_id,
        razorpay_payment_id=request.razorpay_payment_id,
        razorpay_order_id=request.razorpay_order_id,
        razorpay_signature=request.razorpay_signature
    )
    
    if not result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get("error", "Payment verification failed")
        )
    
    return result


@router.post("/webhook")
async def payment_webhook(payload: dict):
    """
    Razorpay webhook handler.
    
    - Handles payment.captured, payment.failed events
    - Configure webhook URL in Razorpay dashboard
    """
    event = payload.get("event")
    
    if event == "payment.captured":
        payment = payload.get("payload", {}).get("payment", {}).get("entity", {})
        order_id = payment.get("notes", {}).get("order_id")
        
        if order_id:
            orders_collection = get_orders_collection()
            await orders_collection.update_one(
                {"order_id": order_id},
                {
                    "$set": {
                        "payment_status": "paid",
                        "payment_id": payment.get("id"),
                        "status": "confirmed"
                    }
                }
            )
    
    elif event == "payment.failed":
        payment = payload.get("payload", {}).get("payment", {}).get("entity", {})
        order_id = payment.get("notes", {}).get("order_id")
        
        if order_id:
            orders_collection = get_orders_collection()
            await orders_collection.update_one(
                {"order_id": order_id},
                {"$set": {"payment_status": "failed"}}
            )
    
    return {"status": "ok"}


@router.post("/refund")
async def process_refund(
    request: RefundRequest,
    current_user: dict = Depends(get_admin_user)
):
    """
    Process a refund for an order.
    
    - Admin only
    - Supports partial and full refunds
    """
    result = await payment_service.process_refund(
        order_id=request.order_id,
        amount=request.amount,
        reason=request.reason
    )
    
    if not result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get("error", "Refund failed")
        )
    
    return result


@router.get("/status/{order_id}")
async def get_payment_status(
    order_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get payment status for an order.
    """
    orders_collection = get_orders_collection()
    
    order = await orders_collection.find_one({"order_id": order_id})
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Check access
    if current_user["role"] != "admin" and order["user_id"] != current_user["_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    return {
        "order_id": order_id,
        "payment_status": order.get("payment_status", "pending"),
        "payment_id": order.get("payment_id"),
        "razorpay_order_id": order.get("razorpay_order_id"),
        "amount": order.get("total")
    }
