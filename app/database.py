"""
Database Connection Module
MongoDB Atlas connection using Motor async driver
"""

from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional
from app.config import get_settings

# Global database client
_client: Optional[AsyncIOMotorClient] = None
_database = None


async def connect_to_database():
    """Initialize MongoDB connection"""
    global _client, _database
    
    settings = get_settings()
    
    try:
        _client = AsyncIOMotorClient(settings.mongodb_uri)
        _database = _client[settings.database_name]
        
        # Test connection
        await _client.admin.command('ping')
        print(f"✅ Connected to MongoDB: {settings.database_name}")
        
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        raise


async def close_database_connection():
    """Close MongoDB connection"""
    global _client
    
    if _client:
        _client.close()
        print("✅ MongoDB connection closed")


def get_database():
    """Get database instance"""
    if _database is None:
        raise Exception("Database not initialized. Call connect_to_database() first.")
    return _database


def get_products_collection():
    """Get products collection"""
    return get_database()["products"]


def get_categories_collection():
    """Get categories collection"""
    return get_database()["categories"]


def get_users_collection():
    """Get users collection"""
    return get_database()["users"]


def get_orders_collection():
    """Get orders collection"""
    return get_database()["orders"]


def get_carts_collection():
    """Get carts collection"""
    return get_database()["carts"]


def get_reviews_collection():
    """Get reviews collection"""
    return get_database()["reviews"]


def get_render_jobs_collection():
    """Get render jobs collection"""
    return get_database()["render_jobs"]


def get_ar_sessions_collection():
    """Get AR sessions collection"""
    return get_database()["ar_sessions"]


def get_payments_collection():
    """Get payments collection"""
    return get_database()["payments"]


def get_notifications_collection():
    """Get notifications collection"""
    return get_database()["notifications"]


def get_ar_analytics_collection():
    """Get AR analytics collection"""
    return get_database()["ar_analytics"]


def get_wishlists_collection():
    """Get wishlists collection"""
    return get_database()["wishlists"]


def get_search_logs_collection():
    """Get search logs collection"""
    return get_database()["search_logs"]

