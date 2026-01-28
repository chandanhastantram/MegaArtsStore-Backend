"""
Payment Service - Razorpay Integration
Handles payment creation, verification, and refunds
"""

import razorpay
import hmac
import hashlib
from typing import Dict, Optional
from datetime import datetime

from app.config import get_settings
from app.database import get_orders_collection


def get_razorpay_client():
    """Get Razorpay client instance"""
    settings = get_settings()
    return razorpay.Client(auth=(settings.razorpay_key_id, settings.razorpay_key_secret))


async def create_razorpay_order(
    order_id: str,
    amount: float,
    currency: str = "INR"
) -> Dict:
    """
    Create a Razorpay order for payment.
    
    Args:
        order_id: Internal order ID
        amount: Amount in INR
        currency: Currency code
    
    Returns:
        Razorpay order details
    """
    client = get_razorpay_client()
    
    # Razorpay expects amount in paise (smallest currency unit)
    amount_paise = int(amount * 100)
    
    razorpay_order = client.order.create({
        "amount": amount_paise,
        "currency": currency,
        "receipt": order_id,
        "notes": {
            "order_id": order_id
        }
    })
    
    # Store Razorpay order ID in our order
    orders_collection = get_orders_collection()
    await orders_collection.update_one(
        {"order_id": order_id},
        {
            "$set": {
                "razorpay_order_id": razorpay_order["id"],
                "payment_status": "pending",
                "updated_at": datetime.utcnow()
            }
        }
    )
    
    return {
        "razorpay_order_id": razorpay_order["id"],
        "amount": amount,
        "amount_paise": amount_paise,
        "currency": currency,
        "key_id": get_settings().razorpay_key_id
    }


def verify_payment_signature(
    razorpay_order_id: str,
    razorpay_payment_id: str,
    razorpay_signature: str
) -> bool:
    """
    Verify Razorpay payment signature.
    
    Args:
        razorpay_order_id: Razorpay order ID
        razorpay_payment_id: Razorpay payment ID
        razorpay_signature: Signature from Razorpay
    
    Returns:
        True if signature is valid
    """
    settings = get_settings()
    
    message = f"{razorpay_order_id}|{razorpay_payment_id}"
    
    generated_signature = hmac.new(
        settings.razorpay_key_secret.encode(),
        message.encode(),
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(generated_signature, razorpay_signature)


async def confirm_payment(
    order_id: str,
    razorpay_payment_id: str,
    razorpay_order_id: str,
    razorpay_signature: str
) -> Dict:
    """
    Confirm payment after successful Razorpay transaction.
    
    Args:
        order_id: Internal order ID
        razorpay_payment_id: Razorpay payment ID
        razorpay_order_id: Razorpay order ID
        razorpay_signature: Signature for verification
    
    Returns:
        Updated order details
    """
    # Verify signature
    is_valid = verify_payment_signature(
        razorpay_order_id,
        razorpay_payment_id,
        razorpay_signature
    )
    
    if not is_valid:
        return {"success": False, "error": "Invalid payment signature"}
    
    # Update order status
    orders_collection = get_orders_collection()
    
    result = await orders_collection.update_one(
        {"order_id": order_id},
        {
            "$set": {
                "payment_status": "paid",
                "payment_id": razorpay_payment_id,
                "status": "confirmed",
                "paid_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
        }
    )
    
    if result.modified_count == 0:
        return {"success": False, "error": "Order not found"}
    
    return {
        "success": True,
        "order_id": order_id,
        "payment_id": razorpay_payment_id,
        "status": "confirmed"
    }


async def process_refund(
    order_id: str,
    amount: float = None,
    reason: str = "requested_by_customer"
) -> Dict:
    """
    Process refund for an order.
    
    Args:
        order_id: Internal order ID
        amount: Amount to refund (None for full refund)
        reason: Refund reason
    
    Returns:
        Refund details
    """
    orders_collection = get_orders_collection()
    
    # Get order
    order = await orders_collection.find_one({"order_id": order_id})
    
    if not order:
        return {"success": False, "error": "Order not found"}
    
    if order.get("payment_status") != "paid":
        return {"success": False, "error": "Order not paid"}
    
    payment_id = order.get("payment_id")
    if not payment_id:
        return {"success": False, "error": "No payment ID found"}
    
    client = get_razorpay_client()
    
    refund_data = {"notes": {"reason": reason}}
    
    if amount:
        refund_data["amount"] = int(amount * 100)  # Convert to paise
    
    try:
        refund = client.payment.refund(payment_id, refund_data)
        
        # Update order
        await orders_collection.update_one(
            {"order_id": order_id},
            {
                "$set": {
                    "payment_status": "refunded",
                    "refund_id": refund["id"],
                    "refund_amount": amount or order["total"],
                    "refunded_at": datetime.utcnow(),
                    "status": "cancelled",
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        return {
            "success": True,
            "refund_id": refund["id"],
            "amount": amount or order["total"]
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}


async def get_payment_details(payment_id: str) -> Optional[Dict]:
    """Get payment details from Razorpay"""
    client = get_razorpay_client()
    
    try:
        payment = client.payment.fetch(payment_id)
        return {
            "payment_id": payment["id"],
            "amount": payment["amount"] / 100,
            "currency": payment["currency"],
            "status": payment["status"],
            "method": payment["method"],
            "email": payment.get("email"),
            "contact": payment.get("contact"),
            "created_at": datetime.fromtimestamp(payment["created_at"])
        }
    except Exception:
        return None
