"""
Coupon Routes
Coupon CRUD and validation endpoints
"""

from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import List, Optional
from datetime import datetime
from bson import ObjectId

from app.schemas.coupon import (
    CouponCreate,
    CouponUpdate,
    CouponValidate,
    CouponResponse,
    CouponValidationResponse
)
from app.services.coupon_service import CouponService
from app.database import db
from app.utils.auth import get_current_user
from app.middleware.rbac import get_admin_user

router = APIRouter()


@router.post("/", response_model=CouponResponse, status_code=status.HTTP_201_CREATED)
async def create_coupon(
    coupon_data: CouponCreate,
    current_user: dict = Depends(get_admin_user)
):
    """
    Create a new coupon.
    
    - Admin only
    - Coupon code must be unique
    """
    # Check if code already exists
    existing = await db.coupons.find_one({"code": coupon_data.code.upper()})
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Coupon code already exists"
        )
    
    # Create coupon
    coupon_dict = coupon_data.dict()
    coupon_dict["code"] = coupon_dict["code"].upper()
    coupon_dict["usage_count"] = 0
    coupon_dict["is_active"] = True
    coupon_dict["created_by"] = str(current_user["_id"])
    coupon_dict["created_at"] = datetime.utcnow()
    coupon_dict["updated_at"] = datetime.utcnow()
    
    result = await db.coupons.insert_one(coupon_dict)
    coupon_dict["_id"] = result.inserted_id
    
    return _format_coupon_response(coupon_dict)


@router.get("/", response_model=List[CouponResponse])
async def list_coupons(
    active_only: bool = Query(False),
    current_user: dict = Depends(get_admin_user)
):
    """
    List all coupons.
    
    - Admin only
    - Optionally filter by active status
    """
    query = {}
    if active_only:
        query["is_active"] = True
        query["valid_until"] = {"$gte": datetime.utcnow()}
    
    coupons = await db.coupons.find(query).to_list(length=100)
    return [_format_coupon_response(c) for c in coupons]


@router.get("/available", response_model=List[CouponResponse])
async def get_available_coupons(
    current_user: dict = Depends(get_current_user)
):
    """
    Get all available coupons for current user.
    
    - Authenticated users only
    - Returns coupons that user can still use
    """
    coupons = await CouponService.get_user_coupons(str(current_user["_id"]))
    return [_format_coupon_response(c) for c in coupons]


@router.get("/{coupon_id}", response_model=CouponResponse)
async def get_coupon(
    coupon_id: str,
    current_user: dict = Depends(get_admin_user)
):
    """
    Get a single coupon by ID.
    
    - Admin only
    """
    if not ObjectId.is_valid(coupon_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid coupon ID"
        )
    
    coupon = await db.coupons.find_one({"_id": ObjectId(coupon_id)})
    if not coupon:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Coupon not found"
        )
    
    return _format_coupon_response(coupon)


@router.put("/{coupon_id}", response_model=CouponResponse)
async def update_coupon(
    coupon_id: str,
    update_data: CouponUpdate,
    current_user: dict = Depends(get_admin_user)
):
    """
    Update a coupon.
    
    - Admin only
    """
    if not ObjectId.is_valid(coupon_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid coupon ID"
        )
    
    # Get existing coupon
    coupon = await db.coupons.find_one({"_id": ObjectId(coupon_id)})
    if not coupon:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Coupon not found"
        )
    
    # Update coupon
    update_dict = update_data.dict(exclude_unset=True)
    update_dict["updated_at"] = datetime.utcnow()
    
    await db.coupons.update_one(
        {"_id": ObjectId(coupon_id)},
        {"$set": update_dict}
    )
    
    updated_coupon = await db.coupons.find_one({"_id": ObjectId(coupon_id)})
    return _format_coupon_response(updated_coupon)


@router.delete("/{coupon_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_coupon(
    coupon_id: str,
    current_user: dict = Depends(get_admin_user)
):
    """
    Delete a coupon.
    
    - Admin only
    - Soft delete (sets is_active to False)
    """
    if not ObjectId.is_valid(coupon_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid coupon ID"
        )
    
    result = await db.coupons.update_one(
        {"_id": ObjectId(coupon_id)},
        {"$set": {"is_active": False, "updated_at": datetime.utcnow()}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Coupon not found"
        )


@router.post("/validate", response_model=CouponValidationResponse)
async def validate_coupon(
    validation_data: CouponValidate,
    current_user: dict = Depends(get_current_user)
):
    """
    Validate a coupon code.
    
    - Authenticated users only
    - Returns discount amount if valid
    """
    result = await CouponService.validate_coupon(
        code=validation_data.code,
        user_id=validation_data.user_id,
        order_value=validation_data.order_value,
        product_ids=validation_data.product_ids,
        category_ids=validation_data.category_ids
    )
    
    response = CouponValidationResponse(
        valid=result["valid"],
        message=result["message"],
        discount_amount=result.get("discount_amount", 0.0),
        final_amount=result.get("final_amount")
    )
    
    if result["valid"] and result.get("coupon"):
        response.coupon = _format_coupon_response(result["coupon"])
    
    return response


# Helper Functions

def _format_coupon_response(coupon: dict) -> CouponResponse:
    """Format coupon document to response schema"""
    return CouponResponse(
        id=str(coupon["_id"]),
        code=coupon["code"],
        description=coupon["description"],
        discount_type=coupon["discount_type"],
        discount_value=coupon["discount_value"],
        min_order_value=coupon.get("min_order_value", 0.0),
        max_discount=coupon.get("max_discount"),
        usage_limit=coupon.get("usage_limit"),
        usage_count=coupon.get("usage_count", 0),
        user_usage_limit=coupon.get("user_usage_limit", 1),
        valid_from=coupon["valid_from"],
        valid_until=coupon["valid_until"],
        is_active=coupon.get("is_active", True),
        applicable_categories=coupon.get("applicable_categories", []),
        applicable_products=coupon.get("applicable_products", []),
        created_at=coupon.get("created_at", datetime.utcnow())
    )
