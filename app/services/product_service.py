"""
Product Service
Business logic for product management
"""

from typing import List, Optional, Dict
from bson import ObjectId
from datetime import datetime

from app.database import get_products_collection, get_categories_collection
from app.models.product import ProductDocument
from app.schemas.product import ProductCreate, ProductUpdate, ProductFilter
from app.services.cache_service import cache


async def create_product(
    product_data: ProductCreate,
    created_by: str,
    images: List[str] = None
) -> Dict:
    # ... (same)
    products_collection = get_products_collection()
    
    # Create product document
    product_doc = ProductDocument.create_document(
        name=product_data.name,
        description=product_data.description,
        price=product_data.price,
        category=product_data.category,
        material=product_data.material,
        created_by=created_by,
        sizes=product_data.sizes,
        images=images or [],
        stock=product_data.stock
    )
    
    # Insert into database
    result = await products_collection.insert_one(product_doc)
    product_doc["_id"] = str(result.inserted_id)
    
    # Invalidate caches
    await cache.delete("all_categories")
    await cache.delete("products:home")
    
    return product_doc


async def get_product_by_id(product_id: str) -> Optional[Dict]:
    """
    Get a product by ID.
    
    Args:
        product_id: Product ObjectId as string
    
    Returns:
        Product document or None
    """
    # Check cache
    cached = await cache.get(f"product:{product_id}")
    if cached:
        return cached

    products_collection = get_products_collection()
    
    try:
        product = await products_collection.find_one({"_id": ObjectId(product_id)})
        if product:
            product["_id"] = str(product["_id"])
            # Cache result
            await cache.set(f"product:{product_id}", product, ttl_seconds=300)
        return product
    except:
        return None


async def get_products(
    filters: ProductFilter = None,
    page: int = 1,
    per_page: int = 20,
    include_hidden: bool = False
) -> tuple[List[Dict], int]:
    """
    Get paginated products with filters.
    
    Args:
        filters: Filter criteria
        page: Page number (1-indexed)
        per_page: Items per page
        include_hidden: Include non-visible products (admin only)
    
    Returns:
        Tuple of (products list, total count)
    """
    # Check cache for homepage (common case)
    cache_key = "products:home"
    if not filters and page == 1 and not include_hidden:
        cached = await cache.get(cache_key)
        if cached:
            return cached["products"], cached["total"]

    products_collection = get_products_collection()
    
    # Build query
    query = {}
    
    if not include_hidden:
        query["visibility"] = True
    
    if filters:
        if filters.category:
            query["category"] = filters.category
        if filters.material:
            query["material"] = filters.material
        if filters.min_price is not None:
            query["price"] = {"$gte": filters.min_price}
        if filters.max_price is not None:
            if "price" in query:
                query["price"]["$lte"] = filters.max_price
            else:
                query["price"] = {"$lte": filters.max_price}
        if filters.ar_enabled is not None:
            query["ar_enabled"] = filters.ar_enabled
        if filters.featured is not None:
            query["featured"] = filters.featured
        if filters.search:
            query["$or"] = [
                {"name": {"$regex": filters.search, "$options": "i"}},
                {"description": {"$regex": filters.search, "$options": "i"}}
            ]
    
    # Get total count
    total = await products_collection.count_documents(query)
    
    # Get paginated products
    skip = (page - 1) * per_page
    cursor = products_collection.find(query).sort("created_at", -1).skip(skip).limit(per_page)
    products = await cursor.to_list(length=per_page)
    
    # Convert ObjectIds to strings
    for product in products:
        product["_id"] = str(product["_id"])
    
    # Cache first page results if no filters (homepage)
    if not filters and page == 1 and not include_hidden:
        await cache.set(cache_key, {"products": products, "total": total}, ttl_seconds=300)
    
    return products, total


async def update_product(
    product_id: str,
    update_data: ProductUpdate
) -> Optional[Dict]:
    """
    Update a product.
    
    Args:
        product_id: Product ObjectId as string
        update_data: Fields to update
    
    Returns:
        Updated product document or None
    """
    products_collection = get_products_collection()
    
    # Build update document
    update_doc = {"updated_at": datetime.utcnow()}
    
    for field, value in update_data.model_dump(exclude_unset=True).items():
        if value is not None:
            update_doc[field] = value
    
    # Update product
    result = await products_collection.update_one(
        {"_id": ObjectId(product_id)},
        {"$set": update_doc}
    )
    
    # Invalidate caches
    await cache.delete("all_categories")
    await cache.delete(f"product:{product_id}")
    await cache.delete("products:home")
    
    if result.modified_count == 0:
        return None
    
    return await get_product_by_id(product_id)


async def delete_product(product_id: str) -> bool:
    """
    Delete a product.
    
    Args:
        product_id: Product ObjectId as string
    
    Returns:
        True if deleted
    """
    products_collection = get_products_collection()
    
    result = await products_collection.delete_one({"_id": ObjectId(product_id)})
    return result.deleted_count > 0


async def add_product_images(product_id: str, image_urls: List[str]) -> Optional[Dict]:
    """Add images to a product"""
    products_collection = get_products_collection()
    
    result = await products_collection.update_one(
        {"_id": ObjectId(product_id)},
        {
            "$push": {"images": {"$each": image_urls}},
            "$set": {"updated_at": datetime.utcnow()}
        }
    )
    
    if result.modified_count == 0:
        return None
    
    return await get_product_by_id(product_id)


async def update_product_3d_model(
    product_id: str,
    model_url: str,
    original_url: str = None
) -> Optional[Dict]:
    """Update product's 3D model URL"""
    products_collection = get_products_collection()
    
    update_doc = {
        "model_3d": model_url,
        "updated_at": datetime.utcnow()
    }
    
    if original_url:
        update_doc["model_original"] = original_url
    
    result = await products_collection.update_one(
        {"_id": ObjectId(product_id)},
        {"$set": update_doc}
    )
    
    if result.modified_count == 0:
        return None
    
    return await get_product_by_id(product_id)


async def update_ar_config(product_id: str, ar_config: Dict) -> Optional[Dict]:
    """Update product's AR configuration"""
    products_collection = get_products_collection()
    
    result = await products_collection.update_one(
        {"_id": ObjectId(product_id)},
        {
            "$set": {
                "ar_config": ar_config,
                "updated_at": datetime.utcnow()
            }
        }
    )
    
    if result.modified_count == 0:
        return None
    
    return await get_product_by_id(product_id)


async def add_review(
    product_id: str,
    user_id: str,
    user_name: str,
    rating: int,
    comment: str
) -> Optional[Dict]:
    """Add a review to a product and update average rating"""
    products_collection = get_products_collection()
    
    review = {
        "user_id": user_id,
        "user_name": user_name,
        "rating": rating,
        "comment": comment,
        "created_at": datetime.utcnow()
    }
    
    # Add review
    await products_collection.update_one(
        {"_id": ObjectId(product_id)},
        {
            "$push": {"reviews": review},
            "$set": {"updated_at": datetime.utcnow()}
        }
    )
    
    # Recalculate average rating
    product = await get_product_by_id(product_id)
    if product and product.get("reviews"):
        reviews = product["reviews"]
        avg_rating = sum(r["rating"] for r in reviews) / len(reviews)
        
        await products_collection.update_one(
            {"_id": ObjectId(product_id)},
            {"$set": {"avg_rating": round(avg_rating, 1)}}
        )
    
    return await get_product_by_id(product_id)


# ============ Category Functions ============

async def create_category(name: str, description: str = None, image: str = None) -> Dict:
    """Create a new category"""
    categories_collection = get_categories_collection()
    
    category_doc = {
        "name": name,
        "description": description,
        "image": image,
        "created_at": datetime.utcnow()
    }
    
    result = await categories_collection.insert_one(category_doc)
    category_doc["_id"] = str(result.inserted_id)
    
    return category_doc


async def get_categories() -> List[Dict]:
    """Get all categories with product counts"""
    # Check cache
    cached = await cache.get("all_categories")
    if cached:
        return cached

    categories_collection = get_categories_collection()
    products_collection = get_products_collection()
    
    categories = await categories_collection.find().to_list(length=100)
    
    for category in categories:
        category["_id"] = str(category["_id"])
        # Count products in this category
        count = await products_collection.count_documents({"category": category["name"]})
        category["product_count"] = count
    
    # Cache result
    await cache.set("all_categories", categories, ttl_seconds=600)
    
    return categories
