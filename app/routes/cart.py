"""
Cart Routes
Shopping cart management endpoints
"""

from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, Field
from typing import List, Optional
from bson import ObjectId
from datetime import datetime

from app.database import get_users_collection, get_products_collection
from app.utils.auth import get_current_user

router = APIRouter()


# ============ Schemas ============

class CartItemAdd(BaseModel):
    """Schema for adding item to cart"""
    product_id: str
    size: str
    quantity: int = Field(ge=1, default=1)


class CartItemUpdate(BaseModel):
    """Schema for updating cart item"""
    quantity: int = Field(ge=1)


class CartItemResponse(BaseModel):
    """Schema for cart item response"""
    product_id: str
    product_name: str
    product_image: str
    size: str
    quantity: int
    price: float
    subtotal: float


class CartResponse(BaseModel):
    """Schema for cart response"""
    items: List[CartItemResponse]
    subtotal: float
    item_count: int


# ============ Routes ============

@router.get("/", response_model=CartResponse)
async def get_cart(current_user: dict = Depends(get_current_user)):
    """
    Get current user's cart.
    
    - Authenticated users only
    """
    users_collection = get_users_collection()
    products_collection = get_products_collection()
    
    user = await users_collection.find_one({"_id": ObjectId(current_user["_id"])})
    cart_items = user.get("cart", [])
    
    items = []
    subtotal = 0.0
    
    for item in cart_items:
        product = await products_collection.find_one({"_id": ObjectId(item["product_id"])})
        if product:
            item_subtotal = product["price"] * item["quantity"]
            items.append(CartItemResponse(
                product_id=item["product_id"],
                product_name=product["name"],
                product_image=product["images"][0] if product.get("images") else "",
                size=item["size"],
                quantity=item["quantity"],
                price=product["price"],
                subtotal=item_subtotal
            ))
            subtotal += item_subtotal
    
    return CartResponse(
        items=items,
        subtotal=subtotal,
        item_count=len(items)
    )


@router.post("/add")
async def add_to_cart(
    item: CartItemAdd,
    current_user: dict = Depends(get_current_user)
):
    """
    Add item to cart.
    
    - Authenticated users only
    - If item already exists with same size, quantity is increased
    """
    users_collection = get_users_collection()
    products_collection = get_products_collection()
    
    # Verify product exists and is available
    product = await products_collection.find_one({"_id": ObjectId(item.product_id)})
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    if not product.get("visibility", True):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Product is not available"
        )
    
    if product.get("stock", 0) < item.quantity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Insufficient stock"
        )
    
    # Check if item already in cart
    user = await users_collection.find_one({"_id": ObjectId(current_user["_id"])})
    cart = user.get("cart", [])
    
    # Find existing item with same product and size
    existing_index = None
    for i, cart_item in enumerate(cart):
        if cart_item["product_id"] == item.product_id and cart_item["size"] == item.size:
            existing_index = i
            break
    
    if existing_index is not None:
        # Update quantity
        cart[existing_index]["quantity"] += item.quantity
        await users_collection.update_one(
            {"_id": ObjectId(current_user["_id"])},
            {"$set": {"cart": cart, "updated_at": datetime.utcnow()}}
        )
    else:
        # Add new item
        await users_collection.update_one(
            {"_id": ObjectId(current_user["_id"])},
            {
                "$push": {"cart": {
                    "product_id": item.product_id,
                    "size": item.size,
                    "quantity": item.quantity
                }},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )
    
    return {"message": "Item added to cart"}


@router.put("/update/{product_id}/{size}")
async def update_cart_item(
    product_id: str,
    size: str,
    update: CartItemUpdate,
    current_user: dict = Depends(get_current_user)
):
    """
    Update cart item quantity.
    
    - Authenticated users only
    """
    users_collection = get_users_collection()
    
    user = await users_collection.find_one({"_id": ObjectId(current_user["_id"])})
    cart = user.get("cart", [])
    
    # Find and update item
    found = False
    for item in cart:
        if item["product_id"] == product_id and item["size"] == size:
            item["quantity"] = update.quantity
            found = True
            break
    
    if not found:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found in cart"
        )
    
    await users_collection.update_one(
        {"_id": ObjectId(current_user["_id"])},
        {"$set": {"cart": cart, "updated_at": datetime.utcnow()}}
    )
    
    return {"message": "Cart updated"}


@router.delete("/remove/{product_id}/{size}")
async def remove_from_cart(
    product_id: str,
    size: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Remove item from cart.
    
    - Authenticated users only
    """
    users_collection = get_users_collection()
    
    await users_collection.update_one(
        {"_id": ObjectId(current_user["_id"])},
        {
            "$pull": {"cart": {"product_id": product_id, "size": size}},
            "$set": {"updated_at": datetime.utcnow()}
        }
    )
    
    return {"message": "Item removed from cart"}


@router.delete("/clear")
async def clear_cart(current_user: dict = Depends(get_current_user)):
    """
    Clear entire cart.
    
    - Authenticated users only
    """
    users_collection = get_users_collection()
    
    await users_collection.update_one(
        {"_id": ObjectId(current_user["_id"])},
        {"$set": {"cart": [], "updated_at": datetime.utcnow()}}
    )
    
    return {"message": "Cart cleared"}


@router.get("/count")
async def get_cart_count(current_user: dict = Depends(get_current_user)):
    """
    Get cart item count.
    
    - Authenticated users only
    """
    users_collection = get_users_collection()
    
    user = await users_collection.find_one({"_id": ObjectId(current_user["_id"])})
    cart = user.get("cart", [])
    
    total_items = sum(item.get("quantity", 0) for item in cart)
    
    return {"count": total_items}
