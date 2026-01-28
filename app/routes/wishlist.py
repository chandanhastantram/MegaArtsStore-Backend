"""
Wishlist Routes
User wishlist management endpoints
"""

from fastapi import APIRouter, HTTPException, status, Depends
from typing import List, Optional
from bson import ObjectId
from datetime import datetime
import secrets

from app.schemas.product import ProductResponse
from app.services import user_service, notifications_service
from app.services.product_service import get_product_by_id
from app.utils.auth import get_current_user
from app.database import get_database

router = APIRouter()


@router.get("/", response_model=List[ProductResponse])
async def get_wishlist(current_user: dict = Depends(get_current_user)):
    """
    Get current user's wishlist with full product details.
    
    - Authenticated users only
    """
    wishlist_ids = await user_service.get_wishlist(current_user["_id"])
    
    products = []
    for product_id in wishlist_ids:
        product = await get_product_by_id(product_id)
        if product:
            products.append(_format_product(product))
    
    return products


@router.post("/add/{product_id}")
async def add_to_wishlist(
    product_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Add a product to wishlist.
    
    - Authenticated users only
    """
    # Verify product exists
    product = await get_product_by_id(product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    await user_service.add_to_wishlist(current_user["_id"], product_id)
    
    return {"message": "Product added to wishlist", "product_id": product_id}


@router.delete("/remove/{product_id}")
async def remove_from_wishlist(
    product_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Remove a product from wishlist.
    
    - Authenticated users only
    """
    await user_service.remove_from_wishlist(current_user["_id"], product_id)
    
    return {"message": "Product removed from wishlist", "product_id": product_id}


@router.delete("/clear")
async def clear_wishlist(current_user: dict = Depends(get_current_user)):
    """
    Clear entire wishlist.
    
    - Authenticated users only
    """
    await user_service.clear_wishlist(current_user["_id"])
    
    return {"message": "Wishlist cleared"}


@router.get("/check/{product_id}")
async def check_in_wishlist(
    product_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Check if a product is in wishlist.
    
    - Authenticated users only
    """
    wishlist = await user_service.get_wishlist(current_user["_id"])
    
    return {"in_wishlist": product_id in wishlist}


@router.post("/share")
async def create_shareable_wishlist(
    current_user: dict = Depends(get_current_user)
):
    """
    Create a shareable link for wishlist.
    
    - Authenticated users only
    - Returns a public token that can be shared on social media
    """
    db = get_database()
    shared_wishlists = db["shared_wishlists"]
    
    # Generate unique token
    share_token = secrets.token_urlsafe(16)
    
    # Get current wishlist
    wishlist_ids = await user_service.get_wishlist(current_user["_id"])
    
    # Store shareable wishlist
    await shared_wishlists.insert_one({
        "token": share_token,
        "user_id": current_user["_id"],
        "user_name": current_user["name"],
        "product_ids": wishlist_ids,
        "created_at": datetime.utcnow(),
        "views": 0
    })
    
    share_url = f"http://localhost:3000/wishlist/shared/{share_token}"
    
    return {
        "share_token": share_token,
        "share_url": share_url,
        "product_count": len(wishlist_ids)
    }


@router.get("/shared/{share_token}")
async def get_shared_wishlist(share_token: str):
    """
    Get a shared wishlist by token.
    
    - Public endpoint
    - Anyone with the link can view
    """
    db = get_database()
    shared_wishlists = db["shared_wishlists"]
    
    # Find shared wishlist
    shared = await shared_wishlists.find_one({"token": share_token})
    
    if not shared:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shared wishlist not found"
        )
    
    # Increment view count
    await shared_wishlists.update_one(
        {"token": share_token},
        {"$inc": {"views": 1}}
    )
    
    # Get product details
    products = []
    for product_id in shared["product_ids"]:
        product = await get_product_by_id(product_id)
        if product:
            products.append(_format_product(product))
    
    return {
        "user_name": shared["user_name"],
        "products": products,
        "total": len(products),
        "views": shared["views"] + 1
    }


@router.post("/notify/{product_id}")
async def subscribe_back_in_stock(
    product_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Subscribe to back-in-stock notifications for a product.
    
    - Authenticated users only
    """
    # Verify product exists
    product = await get_product_by_id(product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    result = await notifications_service.subscribe_back_in_stock(
        user_id=current_user["_id"],
        product_id=product_id,
        email=current_user["email"]
    )
    
    return result


def _format_product(product: dict) -> ProductResponse:
    """Format product for response"""
    from app.schemas.product import ARConfigResponse
    
    ar_config = None
    if product.get("ar_config"):
        ar_config = ARConfigResponse(
            scale=product["ar_config"].get("scale", 1.0),
            rotation=product["ar_config"].get("rotation", [0, 0, 0]),
            offset=product["ar_config"].get("offset", [0, 0, 0]),
            wrist_diameter=product["ar_config"].get("wrist_diameter", 0.0)
        )
    
    return ProductResponse(
        id=product["_id"],
        name=product["name"],
        description=product["description"],
        price=product["price"],
        category=product["category"],
        material=product["material"],
        sizes=product.get("sizes", []),
        images=product.get("images", []),
        model_3d=product.get("model_3d"),
        ar_enabled=product.get("ar_enabled", False),
        ar_config=ar_config,
        visibility=product.get("visibility", True),
        featured=product.get("featured", False),
        stock=product.get("stock", 0),
        reviews=product.get("reviews", []),
        avg_rating=product.get("avg_rating", 0.0),
        created_at=product["created_at"]
    )
