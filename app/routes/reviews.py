"""
Reviews Routes
Product review management endpoints
"""

from fastapi import APIRouter, HTTPException, status, Depends, Query
from pydantic import BaseModel, Field
from typing import List, Optional
from bson import ObjectId
from datetime import datetime

from app.database import get_products_collection
from app.utils.auth import get_current_user
from app.middleware.rbac import get_admin_user

router = APIRouter()


# ============ Schemas ============

class ReviewCreate(BaseModel):
    """Schema for creating a review"""
    rating: int = Field(ge=1, le=5)
    comment: str = Field(min_length=10, max_length=1000)


class ReviewResponse(BaseModel):
    """Schema for review response"""
    user_id: str
    user_name: str
    rating: int
    comment: str
    created_at: datetime


class ReviewListResponse(BaseModel):
    """Schema for review list response"""
    reviews: List[ReviewResponse]
    total: int
    avg_rating: float


# ============ Routes ============

@router.get("/{product_id}", response_model=ReviewListResponse)
async def get_product_reviews(
    product_id: str,
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=50)
):
    """
    Get all reviews for a product.
    
    - Public endpoint
    """
    products_collection = get_products_collection()
    
    product = await products_collection.find_one({"_id": ObjectId(product_id)})
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    reviews = product.get("reviews", [])
    total = len(reviews)
    avg_rating = product.get("avg_rating", 0.0)
    
    # Paginate
    start = (page - 1) * per_page
    end = start + per_page
    paginated_reviews = reviews[start:end]
    
    return ReviewListResponse(
        reviews=[ReviewResponse(**r) for r in paginated_reviews],
        total=total,
        avg_rating=avg_rating
    )


@router.post("/{product_id}")
async def add_review(
    product_id: str,
    review_data: ReviewCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    Add a review to a product.
    
    - Authenticated users only
    - One review per user per product
    """
    products_collection = get_products_collection()
    
    product = await products_collection.find_one({"_id": ObjectId(product_id)})
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Check if user already reviewed
    existing_reviews = product.get("reviews", [])
    for review in existing_reviews:
        if review["user_id"] == current_user["_id"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You have already reviewed this product"
            )
    
    # Add review
    new_review = {
        "user_id": current_user["_id"],
        "user_name": current_user["name"],
        "rating": review_data.rating,
        "comment": review_data.comment,
        "created_at": datetime.utcnow()
    }
    
    await products_collection.update_one(
        {"_id": ObjectId(product_id)},
        {
            "$push": {"reviews": new_review},
            "$set": {"updated_at": datetime.utcnow()}
        }
    )
    
    # Recalculate average rating
    product = await products_collection.find_one({"_id": ObjectId(product_id)})
    reviews = product.get("reviews", [])
    avg_rating = sum(r["rating"] for r in reviews) / len(reviews) if reviews else 0
    
    await products_collection.update_one(
        {"_id": ObjectId(product_id)},
        {"$set": {"avg_rating": round(avg_rating, 1)}}
    )
    
    return {"message": "Review added successfully", "avg_rating": round(avg_rating, 1)}


@router.put("/{product_id}")
async def update_review(
    product_id: str,
    review_data: ReviewCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    Update own review on a product.
    
    - Authenticated users only
    - Can only update own review
    """
    products_collection = get_products_collection()
    
    product = await products_collection.find_one({"_id": ObjectId(product_id)})
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Find user's review
    reviews = product.get("reviews", [])
    review_index = None
    for i, review in enumerate(reviews):
        if review["user_id"] == current_user["_id"]:
            review_index = i
            break
    
    if review_index is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="You have not reviewed this product"
        )
    
    # Update review
    reviews[review_index]["rating"] = review_data.rating
    reviews[review_index]["comment"] = review_data.comment
    reviews[review_index]["updated_at"] = datetime.utcnow()
    
    await products_collection.update_one(
        {"_id": ObjectId(product_id)},
        {"$set": {"reviews": reviews, "updated_at": datetime.utcnow()}}
    )
    
    # Recalculate average rating
    avg_rating = sum(r["rating"] for r in reviews) / len(reviews) if reviews else 0
    
    await products_collection.update_one(
        {"_id": ObjectId(product_id)},
        {"$set": {"avg_rating": round(avg_rating, 1)}}
    )
    
    return {"message": "Review updated successfully", "avg_rating": round(avg_rating, 1)}


@router.delete("/{product_id}")
async def delete_own_review(
    product_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Delete own review from a product.
    
    - Authenticated users only
    - Can only delete own review
    """
    products_collection = get_products_collection()
    
    product = await products_collection.find_one({"_id": ObjectId(product_id)})
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Remove user's review
    result = await products_collection.update_one(
        {"_id": ObjectId(product_id)},
        {
            "$pull": {"reviews": {"user_id": current_user["_id"]}},
            "$set": {"updated_at": datetime.utcnow()}
        }
    )
    
    # Recalculate average rating
    product = await products_collection.find_one({"_id": ObjectId(product_id)})
    reviews = product.get("reviews", [])
    avg_rating = sum(r["rating"] for r in reviews) / len(reviews) if reviews else 0
    
    await products_collection.update_one(
        {"_id": ObjectId(product_id)},
        {"$set": {"avg_rating": round(avg_rating, 1)}}
    )
    
    return {"message": "Review deleted successfully"}


@router.delete("/admin/{product_id}/{user_id}")
async def admin_delete_review(
    product_id: str,
    user_id: str,
    current_user: dict = Depends(get_admin_user)
):
    """
    Admin delete any review.
    
    - Admin only
    """
    products_collection = get_products_collection()
    
    result = await products_collection.update_one(
        {"_id": ObjectId(product_id)},
        {
            "$pull": {"reviews": {"user_id": user_id}},
            "$set": {"updated_at": datetime.utcnow()}
        }
    )
    
    if result.modified_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )
    
    # Recalculate average rating
    product = await products_collection.find_one({"_id": ObjectId(product_id)})
    reviews = product.get("reviews", [])
    avg_rating = sum(r["rating"] for r in reviews) / len(reviews) if reviews else 0
    
    await products_collection.update_one(
        {"_id": ObjectId(product_id)},
        {"$set": {"avg_rating": round(avg_rating, 1)}}
    )
    
    return {"message": "Review deleted by admin"}
