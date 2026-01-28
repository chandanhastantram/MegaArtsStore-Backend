"""
Order Routes
Order creation, history, and management endpoints
"""

from fastapi import APIRouter, HTTPException, status, Depends, Query, BackgroundTasks
from app.services import email_service
from typing import List
from bson import ObjectId
from datetime import datetime

from app.database import get_orders_collection, get_products_collection, get_users_collection
from app.schemas.order import (
    OrderCreate,
    OrderResponse,
    OrderListResponse,
    OrderStatusUpdate,
    OrderItemResponse,
    ShippingAddressResponse
)
from app.models.order import OrderDocument
from app.utils.auth import get_current_user
from app.middleware.rbac import get_admin_user

router = APIRouter()


@router.post("/create", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    order_data: OrderCreate,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new order.
    
    - Authenticated users only
    - Validates product availability and stock
    """
    products_collection = get_products_collection()
    orders_collection = get_orders_collection()
    
    # Validate and build order items
    order_items = []
    subtotal = 0.0
    
    for item in order_data.items:
        # Get product
        product = await products_collection.find_one({"_id": ObjectId(item.product_id)})
        
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product {item.product_id} not found"
            )
        
        if not product.get("visibility", True):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Product {product['name']} is not available"
            )
        
        if product.get("stock", 0) < item.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient stock for {product['name']}"
            )
        
        # Build order item
        item_subtotal = product["price"] * item.quantity
        order_items.append({
            "product_id": item.product_id,
            "product_name": product["name"],
            "product_image": product["images"][0] if product.get("images") else "",
            "size": item.size,
            "quantity": item.quantity,
            "price": product["price"],
            "subtotal": item_subtotal
        })
        subtotal += item_subtotal
    
    # Calculate tax (18% GST)
    tax = round(subtotal * 0.18, 2)
    
    # Shipping cost (free above 5000)
    shipping_cost = 0 if subtotal >= 5000 else 150
    
    # Create order document
    order_doc = OrderDocument.create_document(
        user_id=current_user["_id"],
        items=order_items,
        shipping_address=order_data.shipping_address.model_dump(),
        subtotal=subtotal,
        shipping_cost=shipping_cost,
        tax=tax
    )
    
    # Insert order
    result = await orders_collection.insert_one(order_doc)
    order_doc["_id"] = str(result.inserted_id)
    
    # Update stock for each product
    for item in order_data.items:
        await products_collection.update_one(
            {"_id": ObjectId(item.product_id)},
            {"$inc": {"stock": -item.quantity}}
        )
    
    # Send confirmation email
    background_tasks.add_task(
        email_service.send_order_confirmation,
        order_doc,
        current_user["email"],
        current_user["name"]
    )
    
    return _format_order_response(order_doc)


@router.get("/history", response_model=OrderListResponse)
async def get_order_history(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(get_current_user)
):
    """
    Get current user's order history.
    
    - Authenticated users only
    """
    orders_collection = get_orders_collection()
    
    query = {"user_id": current_user["_id"]}
    
    # Get total count
    total = await orders_collection.count_documents(query)
    
    # Get paginated orders
    skip = (page - 1) * per_page
    cursor = orders_collection.find(query).sort("created_at", -1).skip(skip).limit(per_page)
    orders = await cursor.to_list(length=per_page)
    
    return OrderListResponse(
        orders=[_format_order_response(o) for o in orders],
        total=total,
        page=page,
        per_page=per_page
    )


@router.get("/admin/all", response_model=OrderListResponse)
async def get_all_orders(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    status_filter: str = None,
    current_user: dict = Depends(get_admin_user)
):
    """
    Get all orders.
    
    - Admin only
    - Supports status filtering
    """
    orders_collection = get_orders_collection()
    
    query = {}
    if status_filter:
        query["status"] = status_filter
    
    # Get total count
    total = await orders_collection.count_documents(query)
    
    # Get paginated orders
    skip = (page - 1) * per_page
    cursor = orders_collection.find(query).sort("created_at", -1).skip(skip).limit(per_page)
    orders = await cursor.to_list(length=per_page)
    
    return OrderListResponse(
        orders=[_format_order_response(o) for o in orders],
        total=total,
        page=page,
        per_page=per_page
    )


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get order details.
    
    - Users can only view their own orders
    - Admins can view any order
    """
    orders_collection = get_orders_collection()
    
    order = await orders_collection.find_one({"_id": ObjectId(order_id)})
    
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
    
    return _format_order_response(order)


@router.put("/admin/{order_id}/status", response_model=OrderResponse)
async def update_order_status(
    order_id: str,
    status_update: OrderStatusUpdate,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_admin_user)
):
    """
    Update order status.
    
    - Admin only
    """
    orders_collection = get_orders_collection()
    users_collection = get_users_collection()
    
    order = await orders_collection.find_one({"_id": ObjectId(order_id)})
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Update status
    await orders_collection.update_one(
        {"_id": ObjectId(order_id)},
        {
            "$set": {
                "status": status_update.status,
                "updated_at": datetime.utcnow()
            }
        }
    )
    
    # Send email notifications
    if status_update.status in ["shipped", "delivered"]:
        user = await users_collection.find_one({"_id": ObjectId(order["user_id"])})
        if user:
            if status_update.status == "shipped":
                background_tasks.add_task(
                    email_service.send_shipping_update,
                    order["order_id"],
                    user["email"],
                    user["name"]
                )
            elif status_update.status == "delivered":
                background_tasks.add_task(
                    email_service.send_delivery_confirmation,
                    order["order_id"],
                    user["email"],
                    user["name"]
                )
    
    order["status"] = status_update.status
    order["updated_at"] = datetime.utcnow()
    
    return _format_order_response(order)


@router.get("/admin/analytics/revenue")
async def get_revenue_analytics(
    current_user: dict = Depends(get_admin_user)
):
    """
    Get revenue analytics.
    
    - Admin only
    - Returns total sales, revenue, order counts
    """
    orders_collection = get_orders_collection()
    
    # Aggregate revenue data
    pipeline = [
        {"$match": {"status": {"$ne": "cancelled"}}},
        {"$group": {
            "_id": None,
            "total_orders": {"$sum": 1},
            "total_revenue": {"$sum": "$total"},
            "avg_order_value": {"$avg": "$total"}
        }}
    ]
    
    result = await orders_collection.aggregate(pipeline).to_list(1)
    
    if not result:
        return {
            "total_orders": 0,
            "total_revenue": 0,
            "avg_order_value": 0
        }
    
    return {
        "total_orders": result[0]["total_orders"],
        "total_revenue": round(result[0]["total_revenue"], 2),
        "avg_order_value": round(result[0]["avg_order_value"], 2)
    }


# ============ Helper Functions ============

def _format_order_response(order: dict) -> OrderResponse:
    """Format order document to response schema"""
    return OrderResponse(
        id=str(order["_id"]) if isinstance(order["_id"], ObjectId) else order["_id"],
        order_id=order["order_id"],
        user_id=order["user_id"],
        items=[
            OrderItemResponse(**item)
            for item in order["items"]
        ],
        subtotal=order["subtotal"],
        shipping_cost=order["shipping_cost"],
        tax=order["tax"],
        total=order["total"],
        status=order["status"],
        shipping_address=ShippingAddressResponse(**order["shipping_address"]),
        payment_status=order.get("payment_status", "pending"),
        payment_id=order.get("payment_id"),
        created_at=order["created_at"],
        updated_at=order["updated_at"]
    )
