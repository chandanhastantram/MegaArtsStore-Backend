"""
Recommendations Routes
Personalized product recommendations
"""

from fastapi import APIRouter, Depends, Query
from typing import List, Optional

from app.utils.auth import get_current_user
from app.services import recommendations_service

router = APIRouter()


@router.get("/for-you")
async def get_recommendations_for_user(
    limit: int = Query(10, ge=1, le=50),
    exclude: Optional[str] = Query(None, description="Comma-separated product IDs to exclude"),
    current_user: dict = Depends(get_current_user)
):
    """
    Get personalized recommendations for the current user.
    
    - Authenticated users only
    - Based on purchase history and AR try-ons
    """
    exclude_ids = exclude.split(",") if exclude else []
    
    recommendations = await recommendations_service.get_personalized_recommendations(
        user_id=current_user["_id"],
        limit=limit,
        exclude_product_ids=exclude_ids
    )
    
    return {
        "recommendations": recommendations,
        "total": len(recommendations)
    }


@router.get("/similar/{product_id}")
async def get_similar_products(
    product_id: str,
    limit: int = Query(6, ge=1, le=20)
):
    """
    Get products similar to a given product.
    
    - Public endpoint
    - Based on category, price, material
    """
    similar = await recommendations_service.get_similar_products(
        product_id=product_id,
        limit=limit
    )
    
    return {
        "product_id": product_id,
        "similar_products": similar,
        "total": len(similar)
    }


@router.get("/frequently-bought-together/{product_id}")
async def get_frequently_bought_together(
    product_id: str,
    limit: int = Query(4, ge=1, le=10)
):
    """
    Get products frequently bought together with this product.
    
    - Public endpoint
    - Based on order history
    """
    products = await recommendations_service.get_frequently_bought_together(
        product_id=product_id,
        limit=limit
    )
    
    return {
        "product_id": product_id,
        "frequently_bought_together": products,
        "total": len(products)
    }


@router.get("/trending")
async def get_trending_products(
    limit: int = Query(10, ge=1, le=50)
):
    """
    Get trending products based on recent activity.
    
    - Public endpoint
    - Based on AR try-ons and purchases in last 7 days
    """
    from app.services.recommendations_service import _get_trending_products
    from app.database import get_products_collection
    from bson import ObjectId
    
    trending_scores = await _get_trending_products(limit * 2)
    
    # Fetch product details
    products_collection = get_products_collection()
    product_ids = [ObjectId(pid) for pid in trending_scores.keys()]
    products = await products_collection.find(
        {"_id": {"$in": product_ids}, "visibility": True}
    ).to_list(limit)
    
    result = []
    for p in products:
        product_id = str(p["_id"])
        result.append({
            "id": product_id,
            "name": p["name"],
            "price": p["price"],
            "image": p["images"][0] if p.get("images") else None,
            "category": p["category"],
            "trending_score": round(trending_scores.get(product_id, 0), 2)
        })
    
    # Sort by score
    result.sort(key=lambda x: x["trending_score"], reverse=True)
    
    return {
        "trending_products": result[:limit],
        "total": len(result[:limit])
    }
