"""
Coupon Service
Business logic for coupon validation and management
"""

from datetime import datetime
from typing import Optional, Dict, Any
from bson import ObjectId

from app.database import db
from app.models.coupon import CouponDocument, CouponUsageDocument


class CouponService:
    """Service for coupon operations"""

    @staticmethod
    async def validate_coupon(
        code: str,
        user_id: str,
        order_value: float,
        product_ids: list = [],
        category_ids: list = []
    ) -> Dict[str, Any]:
        """
        Validate a coupon code and calculate discount.
        
        Returns:
            dict with validation result and discount amount
        """
        # Find coupon
        coupon = await db.coupons.find_one({"code": code.upper()})
        
        if not coupon:
            return {
                "valid": False,
                "message": "Invalid coupon code",
                "discount_amount": 0.0
            }
        
        # Check if active
        if not coupon.get("is_active"):
            return {
                "valid": False,
                "message": "This coupon is no longer active",
                "discount_amount": 0.0
            }
        
        # Check validity period
        now = datetime.utcnow()
        valid_from = coupon.get("valid_from")
        valid_until = coupon.get("valid_until")
        
        if now < valid_from:
            return {
                "valid": False,
                "message": f"Coupon is not yet valid. Valid from {valid_from.strftime('%Y-%m-%d')}",
                "discount_amount": 0.0
            }
        
        if now > valid_until:
            return {
                "valid": False,
                "message": "This coupon has expired",
                "discount_amount": 0.0
            }
        
        # Check minimum order value
        min_order = coupon.get("min_order_value", 0)
        if order_value < min_order:
            return {
                "valid": False,
                "message": f"Minimum order value of ₹{min_order} required",
                "discount_amount": 0.0
            }
        
        # Check total usage limit
        usage_limit = coupon.get("usage_limit")
        usage_count = coupon.get("usage_count", 0)
        
        if usage_limit and usage_count >= usage_limit:
            return {
                "valid": False,
                "message": "Coupon usage limit reached",
                "discount_amount": 0.0
            }
        
        # Check per-user usage limit
        user_usage_limit = coupon.get("user_usage_limit", 1)
        user_usage = await db.coupon_usage.count_documents({
            "coupon_id": str(coupon["_id"]),
            "user_id": user_id
        })
        
        if user_usage >= user_usage_limit:
            return {
                "valid": False,
                "message": "You have already used this coupon",
                "discount_amount": 0.0
            }
        
        # Check applicable categories
        applicable_categories = coupon.get("applicable_categories", [])
        if applicable_categories and category_ids:
            if not any(cat in applicable_categories for cat in category_ids):
                return {
                    "valid": False,
                    "message": "Coupon not applicable to selected products",
                    "discount_amount": 0.0
                }
        
        # Check applicable products
        applicable_products = coupon.get("applicable_products", [])
        if applicable_products and product_ids:
            if not any(prod in applicable_products for prod in product_ids):
                return {
                    "valid": False,
                    "message": "Coupon not applicable to selected products",
                    "discount_amount": 0.0
                }
        
        # Calculate discount
        discount_type = coupon.get("discount_type")
        discount_value = coupon.get("discount_value")
        
        if discount_type == "percentage":
            discount_amount = (order_value * discount_value) / 100
            max_discount = coupon.get("max_discount")
            if max_discount:
                discount_amount = min(discount_amount, max_discount)
        else:  # fixed
            discount_amount = discount_value
        
        # Ensure discount doesn't exceed order value
        discount_amount = min(discount_amount, order_value)
        final_amount = order_value - discount_amount
        
        return {
            "valid": True,
            "message": "Coupon applied successfully",
            "discount_amount": round(discount_amount, 2),
            "final_amount": round(final_amount, 2),
            "coupon": coupon
        }

    @staticmethod
    async def apply_coupon(
        coupon_id: str,
        user_id: str,
        order_id: str,
        discount_applied: float
    ):
        """
        Record coupon usage and increment usage count.
        """
        # Record usage
        usage = CouponUsageDocument(
            coupon_id=coupon_id,
            user_id=user_id,
            order_id=order_id,
            discount_applied=discount_applied
        )
        
        await db.coupon_usage.insert_one(usage.dict(by_alias=True))
        
        # Increment usage count
        await db.coupons.update_one(
            {"_id": ObjectId(coupon_id)},
            {"$inc": {"usage_count": 1}}
        )

    @staticmethod
    async def get_user_coupons(user_id: str):
        """Get all available coupons for a user"""
        now = datetime.utcnow()
        
        # Get all active coupons
        coupons = await db.coupons.find({
            "is_active": True,
            "valid_from": {"$lte": now},
            "valid_until": {"$gte": now}
        }).to_list(length=100)
        
        # Filter out fully used coupons
        available_coupons = []
        for coupon in coupons:
            # Check total usage
            usage_limit = coupon.get("usage_limit")
            if usage_limit and coupon.get("usage_count", 0) >= usage_limit:
                continue
            
            # Check user usage
            user_usage_limit = coupon.get("user_usage_limit", 1)
            user_usage = await db.coupon_usage.count_documents({
                "coupon_id": str(coupon["_id"]),
                "user_id": user_id
            })
            
            if user_usage >= user_usage_limit:
                continue
            
            available_coupons.append(coupon)
        
        return available_coupons
