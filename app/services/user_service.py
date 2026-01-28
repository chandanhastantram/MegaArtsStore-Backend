"""
User Service
Business logic for user management
"""

from typing import List, Optional, Dict
from bson import ObjectId
from datetime import datetime

from app.database import get_users_collection


async def get_user_by_id(user_id: str) -> Optional[Dict]:
    """Get a user by ID"""
    users_collection = get_users_collection()
    
    try:
        user = await users_collection.find_one({"_id": ObjectId(user_id)})
        if user:
            user["_id"] = str(user["_id"])
        return user
    except:
        return None


async def get_user_by_email(email: str) -> Optional[Dict]:
    """Get a user by email"""
    users_collection = get_users_collection()
    
    user = await users_collection.find_one({"email": email.lower()})
    if user:
        user["_id"] = str(user["_id"])
    return user


async def update_user(user_id: str, update_data: Dict) -> Optional[Dict]:
    """Update user profile"""
    users_collection = get_users_collection()
    
    update_data["updated_at"] = datetime.utcnow()
    
    result = await users_collection.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": update_data}
    )
    
    if result.modified_count == 0:
        return None
    
    return await get_user_by_id(user_id)


# ============ Wishlist Functions ============

async def add_to_wishlist(user_id: str, product_id: str) -> Optional[Dict]:
    """Add a product to user's wishlist"""
    users_collection = get_users_collection()
    
    result = await users_collection.update_one(
        {"_id": ObjectId(user_id)},
        {
            "$addToSet": {"wishlist": product_id},
            "$set": {"updated_at": datetime.utcnow()}
        }
    )
    
    if result.modified_count == 0 and result.matched_count == 0:
        return None
    
    return await get_user_by_id(user_id)


async def remove_from_wishlist(user_id: str, product_id: str) -> Optional[Dict]:
    """Remove a product from user's wishlist"""
    users_collection = get_users_collection()
    
    result = await users_collection.update_one(
        {"_id": ObjectId(user_id)},
        {
            "$pull": {"wishlist": product_id},
            "$set": {"updated_at": datetime.utcnow()}
        }
    )
    
    if result.modified_count == 0 and result.matched_count == 0:
        return None
    
    return await get_user_by_id(user_id)


async def get_wishlist(user_id: str) -> List[str]:
    """Get user's wishlist product IDs"""
    user = await get_user_by_id(user_id)
    
    if not user:
        return []
    
    return user.get("wishlist", [])


async def clear_wishlist(user_id: str) -> bool:
    """Clear user's entire wishlist"""
    users_collection = get_users_collection()
    
    result = await users_collection.update_one(
        {"_id": ObjectId(user_id)},
        {
            "$set": {"wishlist": [], "updated_at": datetime.utcnow()}
        }
    )
    
    return result.modified_count > 0
