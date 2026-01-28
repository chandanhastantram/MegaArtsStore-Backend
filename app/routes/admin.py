"""
Admin Dashboard Routes
Analytics, reports, and admin-only operations
"""

from fastapi import APIRouter, Depends, Query
from typing import Optional
from datetime import datetime, timedelta
from bson import ObjectId

from app.database import get_orders_collection, get_products_collection, get_users_collection
from app.middleware.rbac import get_admin_user
from app.services import ar_analytics_service

router = APIRouter()


@router.get("/overview")
async def get_dashboard_overview(
    current_user: dict = Depends(get_admin_user)
):
    """
    Get admin dashboard overview.
    
    - Admin only
    - Returns key metrics and stats
    """
    orders_collection = get_orders_collection()
    products_collection = get_products_collection()
    users_collection = get_users_collection()
    
    # Get counts
    total_orders = await orders_collection.count_documents({})
    total_products = await products_collection.count_documents({})
    total_users = await users_collection.count_documents({"role": "user"})
    ar_products = await products_collection.count_documents({"ar_enabled": True})
    
    # Get today's stats
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    
    today_orders = await orders_collection.count_documents({"created_at": {"$gte": today}})
    
    # Revenue calculation
    revenue_pipeline = [
        {"$match": {"payment_status": "paid"}},
        {"$group": {"_id": None, "total": {"$sum": "$total"}}}
    ]
    revenue_result = await orders_collection.aggregate(revenue_pipeline).to_list(1)
    total_revenue = revenue_result[0]["total"] if revenue_result else 0
    
    # Today's revenue
    today_revenue_pipeline = [
        {"$match": {"payment_status": "paid", "created_at": {"$gte": today}}},
        {"$group": {"_id": None, "total": {"$sum": "$total"}}}
    ]
    today_result = await orders_collection.aggregate(today_revenue_pipeline).to_list(1)
    today_revenue = today_result[0]["total"] if today_result else 0
    
    # Pending orders
    pending_orders = await orders_collection.count_documents({"status": "pending"})
    
    return {
        "total_orders": total_orders,
        "total_products": total_products,
        "total_users": total_users,
        "ar_enabled_products": ar_products,
        "today_orders": today_orders,
        "pending_orders": pending_orders,
        "total_revenue": round(total_revenue, 2),
        "today_revenue": round(today_revenue, 2)
    }


@router.get("/sales-report")
async def get_sales_report(
    days: int = Query(30, ge=1, le=365),
    current_user: dict = Depends(get_admin_user)
):
    """
    Get sales report for specified period.
    
    - Admin only
    - Returns daily sales data
    """
    orders_collection = get_orders_collection()
    
    since = datetime.utcnow() - timedelta(days=days)
    
    # Daily sales aggregation
    pipeline = [
        {"$match": {"created_at": {"$gte": since}}},
        {"$group": {
            "_id": {
                "year": {"$year": "$created_at"},
                "month": {"$month": "$created_at"},
                "day": {"$dayOfMonth": "$created_at"}
            },
            "orders": {"$sum": 1},
            "revenue": {"$sum": "$total"},
            "paid_orders": {"$sum": {"$cond": [{"$eq": ["$payment_status", "paid"]}, 1, 0]}}
        }},
        {"$sort": {"_id.year": 1, "_id.month": 1, "_id.day": 1}}
    ]
    
    results = await orders_collection.aggregate(pipeline).to_list(365)
    
    daily_data = []
    for r in results:
        date_str = f"{r['_id']['year']}-{r['_id']['month']:02d}-{r['_id']['day']:02d}"
        daily_data.append({
            "date": date_str,
            "orders": r["orders"],
            "revenue": round(r["revenue"], 2),
            "paid_orders": r["paid_orders"]
        })
    
    # Totals
    total_orders = sum(d["orders"] for d in daily_data)
    total_revenue = sum(d["revenue"] for d in daily_data)
    avg_daily_revenue = total_revenue / days if days > 0 else 0
    
    return {
        "period_days": days,
        "daily_data": daily_data,
        "summary": {
            "total_orders": total_orders,
            "total_revenue": round(total_revenue, 2),
            "avg_daily_revenue": round(avg_daily_revenue, 2),
            "avg_order_value": round(total_revenue / total_orders, 2) if total_orders > 0 else 0
        }
    }


@router.get("/top-products")
async def get_top_selling_products(
    limit: int = Query(10, ge=1, le=50),
    days: int = Query(30, ge=1, le=365),
    current_user: dict = Depends(get_admin_user)
):
    """
    Get top selling products.
    
    - Admin only
    """
    orders_collection = get_orders_collection()
    products_collection = get_products_collection()
    
    since = datetime.utcnow() - timedelta(days=days)
    
    pipeline = [
        {"$match": {"created_at": {"$gte": since}}},
        {"$unwind": "$items"},
        {"$group": {
            "_id": "$items.product_id",
            "product_name": {"$first": "$items.product_name"},
            "quantity_sold": {"$sum": "$items.quantity"},
            "revenue": {"$sum": "$items.subtotal"}
        }},
        {"$sort": {"quantity_sold": -1}},
        {"$limit": limit}
    ]
    
    results = await orders_collection.aggregate(pipeline).to_list(limit)
    
    # Enrich with product details
    products = []
    for r in results:
        product = await products_collection.find_one({"_id": ObjectId(r["_id"])})
        products.append({
            "product_id": r["_id"],
            "product_name": r["product_name"],
            "quantity_sold": r["quantity_sold"],
            "revenue": round(r["revenue"], 2),
            "current_stock": product.get("stock", 0) if product else 0,
            "ar_enabled": product.get("ar_enabled", False) if product else False
        })
    
    return {"products": products, "period_days": days}


@router.get("/inventory-alerts")
async def get_inventory_alerts(
    threshold: int = Query(10, ge=0),
    current_user: dict = Depends(get_admin_user)
):
    """
    Get low stock and out of stock products.
    
    - Admin only
    """
    products_collection = get_products_collection()
    
    # Out of stock
    out_of_stock = await products_collection.find(
        {"stock": 0, "visibility": True}
    ).to_list(100)
    
    # Low stock
    low_stock = await products_collection.find(
        {"stock": {"$gt": 0, "$lte": threshold}, "visibility": True}
    ).to_list(100)
    
    return {
        "threshold": threshold,
        "out_of_stock": [
            {"id": str(p["_id"]), "name": p["name"], "stock": 0}
            for p in out_of_stock
        ],
        "low_stock": [
            {"id": str(p["_id"]), "name": p["name"], "stock": p["stock"]}
            for p in low_stock
        ],
        "out_of_stock_count": len(out_of_stock),
        "low_stock_count": len(low_stock)
    }


@router.get("/user-stats")
async def get_user_stats(
    days: int = Query(30, ge=1, le=365),
    current_user: dict = Depends(get_admin_user)
):
    """
    Get user statistics.
    
    - Admin only
    """
    users_collection = get_users_collection()
    orders_collection = get_orders_collection()
    
    since = datetime.utcnow() - timedelta(days=days)
    
    # New users
    new_users = await users_collection.count_documents({"created_at": {"$gte": since}})
    
    # Total by role
    role_pipeline = [
        {"$group": {"_id": "$role", "count": {"$sum": 1}}}
    ]
    role_results = await users_collection.aggregate(role_pipeline).to_list(10)
    roles = {r["_id"]: r["count"] for r in role_results}
    
    # Active users (placed order in period)
    active_pipeline = [
        {"$match": {"created_at": {"$gte": since}}},
        {"$group": {"_id": "$user_id"}},
        {"$count": "active_users"}
    ]
    active_result = await orders_collection.aggregate(active_pipeline).to_list(1)
    active_users = active_result[0]["active_users"] if active_result else 0
    
    return {
        "period_days": days,
        "new_users": new_users,
        "active_users": active_users,
        "total_by_role": roles,
        "total_users": sum(roles.values())
    }


@router.get("/ar-analytics")
async def get_ar_analytics(
    days: int = Query(30, ge=1, le=365),
    current_user: dict = Depends(get_admin_user)
):
    """
    Get AR usage analytics.
    
    - Admin only
    """
    stats = await ar_analytics_service.get_ar_dashboard_stats(days)
    top_products = await ar_analytics_service.get_top_tried_products(10, days)
    
    return {
        "period_days": days,
        "stats": stats,
        "top_tried_products": top_products
    }


@router.get("/order-status-breakdown")
async def get_order_status_breakdown(
    days: int = Query(30, ge=1, le=365),
    current_user: dict = Depends(get_admin_user)
):
    """
    Get order status breakdown.
    
    - Admin only
    """
    orders_collection = get_orders_collection()
    
    since = datetime.utcnow() - timedelta(days=days)
    
    pipeline = [
        {"$match": {"created_at": {"$gte": since}}},
        {"$group": {
            "_id": "$status",
            "count": {"$sum": 1},
            "revenue": {"$sum": "$total"}
        }}
    ]
    
    results = await orders_collection.aggregate(pipeline).to_list(20)
    
    breakdown = {}
    for r in results:
        breakdown[r["_id"]] = {
            "count": r["count"],
            "revenue": round(r["revenue"], 2)
        }
    
    return {
        "period_days": days,
        "breakdown": breakdown
    }
