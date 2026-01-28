"""
Recommendations Service
Personalized product recommendations using AR analytics and purchase history
"""

from typing import List, Dict, Optional
from bson import ObjectId
from collections import defaultdict
from datetime import datetime, timedelta

from app.database import (
    get_products_collection,
    get_orders_collection,
    get_ar_analytics_collection,
    get_users_collection
)


async def get_personalized_recommendations(
    user_id: str,
    limit: int = 10,
    exclude_product_ids: List[str] = None
) -> List[Dict]:
    """
    Get personalized product recommendations for a user.
    
    Combines:
    - Collaborative filtering (users who bought X also bought Y)
    - Content-based filtering (similar to AR try-ons)
    - Purchase history
    
    Args:
        user_id: User ID
        limit: Number of recommendations
        exclude_product_ids: Products to exclude (e.g., already in cart)
    
    Returns:
        List of recommended products with scores
    """
    products_collection = get_products_collection()
    orders_collection = get_orders_collection()
    ar_collection = get_ar_analytics_collection()
    
    exclude_product_ids = exclude_product_ids or []
    recommendations = {}
    
    # 1. Collaborative Filtering - "Users who bought X also bought Y"
    user_purchases = await _get_user_purchases(user_id)
    if user_purchases:
        collab_recs = await _collaborative_filtering(user_purchases, limit * 2)
        for product_id, score in collab_recs.items():
            recommendations[product_id] = recommendations.get(product_id, 0) + score * 0.4
    
    # 2. Content-Based - Similar to AR try-ons
    ar_try_ons = await _get_user_ar_try_ons(user_id)
    if ar_try_ons:
        content_recs = await _content_based_filtering(ar_try_ons, limit * 2)
        for product_id, score in content_recs.items():
            recommendations[product_id] = recommendations.get(product_id, 0) + score * 0.3
    
    # 3. Trending products (fallback)
    trending = await _get_trending_products(limit * 2)
    for product_id, score in trending.items():
        recommendations[product_id] = recommendations.get(product_id, 0) + score * 0.3
    
    # Remove excluded products and user's own purchases
    for product_id in exclude_product_ids + user_purchases:
        recommendations.pop(product_id, None)
    
    # Sort by score and get top N
    sorted_recs = sorted(recommendations.items(), key=lambda x: x[1], reverse=True)[:limit]
    
    # Fetch product details
    product_ids = [ObjectId(pid) for pid, _ in sorted_recs]
    products = await products_collection.find(
        {"_id": {"$in": product_ids}, "visibility": True}
    ).to_list(limit)
    
    # Format response with scores
    result = []
    score_map = dict(sorted_recs)
    for product in products:
        product_id = str(product["_id"])
        result.append({
            "id": product_id,
            "name": product["name"],
            "price": product["price"],
            "image": product["images"][0] if product.get("images") else None,
            "category": product["category"],
            "ar_enabled": product.get("ar_enabled", False),
            "recommendation_score": round(score_map.get(product_id, 0), 2),
            "avg_rating": product.get("avg_rating", 0)
        })
    
    return result


async def get_similar_products(
    product_id: str,
    limit: int = 6
) -> List[Dict]:
    """
    Get products similar to a given product.
    
    Based on:
    - Same category
    - Similar price range
    - Similar material
    
    Args:
        product_id: Product ID
        limit: Number of similar products
    
    Returns:
        List of similar products
    """
    products_collection = get_products_collection()
    
    # Get the reference product
    product = await products_collection.find_one({"_id": ObjectId(product_id)})
    if not product:
        return []
    
    # Find similar products
    price_range = product["price"] * 0.3  # ±30% price range
    
    query = {
        "_id": {"$ne": ObjectId(product_id)},
        "visibility": True,
        "category": product["category"],
        "price": {
            "$gte": product["price"] - price_range,
            "$lte": product["price"] + price_range
        }
    }
    
    # Prefer same material
    similar = await products_collection.find(query).limit(limit * 2).to_list(limit * 2)
    
    # Score by similarity
    scored = []
    for p in similar:
        score = 0
        if p.get("material") == product.get("material"):
            score += 2
        if p.get("ar_enabled") == product.get("ar_enabled"):
            score += 1
        
        scored.append((p, score))
    
    # Sort by score and limit
    scored.sort(key=lambda x: x[1], reverse=True)
    
    result = []
    for p, _ in scored[:limit]:
        result.append({
            "id": str(p["_id"]),
            "name": p["name"],
            "price": p["price"],
            "image": p["images"][0] if p.get("images") else None,
            "category": p["category"],
            "material": p.get("material"),
            "ar_enabled": p.get("ar_enabled", False),
            "avg_rating": p.get("avg_rating", 0)
        })
    
    return result


async def get_frequently_bought_together(
    product_id: str,
    limit: int = 4
) -> List[Dict]:
    """
    Get products frequently bought together with this product.
    
    Args:
        product_id: Product ID
        limit: Number of products
    
    Returns:
        List of frequently bought together products
    """
    orders_collection = get_orders_collection()
    products_collection = get_products_collection()
    
    # Find orders containing this product
    pipeline = [
        {"$match": {"items.product_id": product_id}},
        {"$unwind": "$items"},
        {"$match": {"items.product_id": {"$ne": product_id}}},
        {"$group": {
            "_id": "$items.product_id",
            "count": {"$sum": 1}
        }},
        {"$sort": {"count": -1}},
        {"$limit": limit}
    ]
    
    results = await orders_collection.aggregate(pipeline).to_list(limit)
    
    if not results:
        return []
    
    # Fetch product details
    product_ids = [ObjectId(r["_id"]) for r in results]
    products = await products_collection.find(
        {"_id": {"$in": product_ids}, "visibility": True}
    ).to_list(limit)
    
    # Format response
    count_map = {r["_id"]: r["count"] for r in results}
    
    result = []
    for p in products:
        product_id = str(p["_id"])
        result.append({
            "id": product_id,
            "name": p["name"],
            "price": p["price"],
            "image": p["images"][0] if p.get("images") else None,
            "category": p["category"],
            "times_bought_together": count_map.get(product_id, 0)
        })
    
    return result


# ============ Helper Functions ============

async def _get_user_purchases(user_id: str) -> List[str]:
    """Get list of product IDs user has purchased"""
    orders_collection = get_orders_collection()
    
    pipeline = [
        {"$match": {"user_id": user_id}},
        {"$unwind": "$items"},
        {"$group": {"_id": "$items.product_id"}}
    ]
    
    results = await orders_collection.aggregate(pipeline).to_list(100)
    return [r["_id"] for r in results]


async def _get_user_ar_try_ons(user_id: str, days: int = 30) -> List[str]:
    """Get list of product IDs user has tried on with AR"""
    ar_collection = get_ar_analytics_collection()
    
    since = datetime.utcnow() - timedelta(days=days)
    
    pipeline = [
        {"$match": {"user_id": user_id, "created_at": {"$gte": since}}},
        {"$group": {"_id": "$product_id"}}
    ]
    
    results = await ar_collection.aggregate(pipeline).to_list(100)
    return [r["_id"] for r in results]


async def _collaborative_filtering(
    user_purchases: List[str],
    limit: int
) -> Dict[str, float]:
    """
    Collaborative filtering: find products bought by similar users.
    
    Returns dict of {product_id: score}
    """
    orders_collection = get_orders_collection()
    
    # Find users who bought the same products
    pipeline = [
        {"$match": {"items.product_id": {"$in": user_purchases}}},
        {"$unwind": "$items"},
        {"$match": {"items.product_id": {"$nin": user_purchases}}},
        {"$group": {
            "_id": "$items.product_id",
            "count": {"$sum": 1}
        }},
        {"$sort": {"count": -1}},
        {"$limit": limit}
    ]
    
    results = await orders_collection.aggregate(pipeline).to_list(limit)
    
    # Normalize scores
    max_count = max([r["count"] for r in results], default=1)
    return {r["_id"]: r["count"] / max_count for r in results}


async def _content_based_filtering(
    ar_try_ons: List[str],
    limit: int
) -> Dict[str, float]:
    """
    Content-based filtering: find similar products to AR try-ons.
    
    Returns dict of {product_id: score}
    """
    products_collection = get_products_collection()
    
    # Get categories and materials of tried-on products
    tried_products = await products_collection.find(
        {"_id": {"$in": [ObjectId(pid) for pid in ar_try_ons]}}
    ).to_list(100)
    
    categories = [p["category"] for p in tried_products]
    materials = [p.get("material") for p in tried_products if p.get("material")]
    
    # Find similar products
    similar = await products_collection.find({
        "_id": {"$nin": [ObjectId(pid) for pid in ar_try_ons]},
        "visibility": True,
        "$or": [
            {"category": {"$in": categories}},
            {"material": {"$in": materials}}
        ]
    }).limit(limit).to_list(limit)
    
    # Score by similarity
    scores = {}
    for p in similar:
        score = 0
        if p["category"] in categories:
            score += 0.6
        if p.get("material") in materials:
            score += 0.4
        scores[str(p["_id"])] = score
    
    return scores


async def _get_trending_products(limit: int) -> Dict[str, float]:
    """
    Get trending products based on recent AR try-ons and purchases.
    
    Returns dict of {product_id: score}
    """
    ar_collection = get_ar_analytics_collection()
    
    # Last 7 days
    since = datetime.utcnow() - timedelta(days=7)
    
    pipeline = [
        {"$match": {"created_at": {"$gte": since}}},
        {"$group": {
            "_id": "$product_id",
            "try_on_count": {"$sum": 1},
            "conversion_count": {"$sum": {"$cond": ["$purchased", 1, 0]}}
        }},
        {"$sort": {"try_on_count": -1}},
        {"$limit": limit}
    ]
    
    results = await ar_collection.aggregate(pipeline).to_list(limit)
    
    # Normalize scores
    max_count = max([r["try_on_count"] for r in results], default=1)
    return {r["_id"]: r["try_on_count"] / max_count for r in results}
