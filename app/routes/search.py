"""
Search Routes
Full-text search and advanced filtering
"""

from fastapi import APIRouter, Query
from typing import Optional, List
from bson import ObjectId

from app.database import get_products_collection, get_categories_collection

router = APIRouter()


@router.get("/products")
async def search_products(
    q: str = Query(..., min_length=1, description="Search query"),
    category: Optional[str] = None,
    material: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    ar_enabled: Optional[bool] = None,
    sort_by: str = Query("relevance", pattern="^(relevance|price_asc|price_desc|newest|rating)$"),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100)
):
    """
    Full-text search for products.
    
    - Public endpoint
    - Searches in name, description, category, material
    - Supports filters and sorting
    """
    products_collection = get_products_collection()
    
    # Build search query
    search_conditions = [
        {"visibility": True},
        {"$or": [
            {"name": {"$regex": q, "$options": "i"}},
            {"description": {"$regex": q, "$options": "i"}},
            {"category": {"$regex": q, "$options": "i"}},
            {"material": {"$regex": q, "$options": "i"}}
        ]}
    ]
    
    # Apply filters
    if category:
        search_conditions.append({"category": category})
    
    if material:
        search_conditions.append({"material": material})
    
    if min_price is not None:
        search_conditions.append({"price": {"$gte": min_price}})
    
    if max_price is not None:
        search_conditions.append({"price": {"$lte": max_price}})
    
    if ar_enabled is not None:
        search_conditions.append({"ar_enabled": ar_enabled})
    
    query = {"$and": search_conditions}
    
    # Sorting
    sort_options = {
        "relevance": [("_id", -1)],  # Default
        "price_asc": [("price", 1)],
        "price_desc": [("price", -1)],
        "newest": [("created_at", -1)],
        "rating": [("avg_rating", -1)]
    }
    sort = sort_options.get(sort_by, [("_id", -1)])
    
    # Get total count
    total = await products_collection.count_documents(query)
    
    # Get paginated results
    skip = (page - 1) * per_page
    cursor = products_collection.find(query).sort(sort).skip(skip).limit(per_page)
    products = await cursor.to_list(length=per_page)
    
    # Format response
    results = []
    for p in products:
        results.append({
            "id": str(p["_id"]),
            "name": p["name"],
            "description": p["description"][:100] + "..." if len(p.get("description", "")) > 100 else p.get("description", ""),
            "price": p["price"],
            "category": p["category"],
            "material": p["material"],
            "image": p["images"][0] if p.get("images") else None,
            "ar_enabled": p.get("ar_enabled", False),
            "avg_rating": p.get("avg_rating", 0),
            "stock": p.get("stock", 0)
        })
    
    return {
        "query": q,
        "results": results,
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": (total + per_page - 1) // per_page
    }


@router.get("/suggestions")
async def get_search_suggestions(
    q: str = Query(..., min_length=2, description="Partial search query")
):
    """
    Get search suggestions (autocomplete).
    
    - Public endpoint
    - Returns matching product names and categories
    """
    products_collection = get_products_collection()
    categories_collection = get_categories_collection()
    
    # Search products
    product_cursor = products_collection.find(
        {
            "visibility": True,
            "name": {"$regex": f"^{q}", "$options": "i"}
        },
        {"name": 1, "category": 1}
    ).limit(5)
    products = await product_cursor.to_list(5)
    
    # Search categories
    category_cursor = categories_collection.find(
        {"name": {"$regex": f"^{q}", "$options": "i"}},
        {"name": 1}
    ).limit(3)
    categories = await category_cursor.to_list(3)
    
    suggestions = []
    
    # Add categories first
    for cat in categories:
        suggestions.append({
            "type": "category",
            "value": cat["name"],
            "display": f"Category: {cat['name']}"
        })
    
    # Add products
    for prod in products:
        suggestions.append({
            "type": "product",
            "value": prod["name"],
            "display": prod["name"],
            "id": str(prod["_id"])
        })
    
    return {"suggestions": suggestions}


@router.get("/filters")
async def get_available_filters():
    """
    Get available filter options.
    
    - Public endpoint
    - Returns categories, materials, price range
    """
    products_collection = get_products_collection()
    
    # Get unique categories
    categories = await products_collection.distinct("category", {"visibility": True})
    
    # Get unique materials
    materials = await products_collection.distinct("material", {"visibility": True})
    
    # Get price range
    price_pipeline = [
        {"$match": {"visibility": True}},
        {"$group": {
            "_id": None,
            "min_price": {"$min": "$price"},
            "max_price": {"$max": "$price"}
        }}
    ]
    price_result = await products_collection.aggregate(price_pipeline).to_list(1)
    
    price_range = {"min": 0, "max": 100000}
    if price_result:
        price_range = {
            "min": price_result[0].get("min_price", 0),
            "max": price_result[0].get("max_price", 100000)
        }
    
    # Get AR-enabled count
    ar_count = await products_collection.count_documents({"visibility": True, "ar_enabled": True})
    
    return {
        "categories": categories,
        "materials": materials,
        "price_range": price_range,
        "ar_enabled_count": ar_count
    }


@router.get("/trending")
async def get_trending_searches():
    """
    Get trending search terms and products.
    
    - Public endpoint
    """
    products_collection = get_products_collection()
    
    # Get featured products
    featured = await products_collection.find(
        {"visibility": True, "featured": True}
    ).limit(6).to_list(6)
    
    # Get top-rated products
    top_rated = await products_collection.find(
        {"visibility": True, "avg_rating": {"$gte": 4}}
    ).sort("avg_rating", -1).limit(6).to_list(6)
    
    return {
        "trending_terms": [
            "gold bangles",
            "silver bracelet",
            "diamond ring",
            "kundan set",
            "temple jewellery"
        ],
        "featured_products": [
            {"id": str(p["_id"]), "name": p["name"], "image": p["images"][0] if p.get("images") else None}
            for p in featured
        ],
        "top_rated": [
            {"id": str(p["_id"]), "name": p["name"], "rating": p.get("avg_rating", 0)}
            for p in top_rated
        ]
    }
