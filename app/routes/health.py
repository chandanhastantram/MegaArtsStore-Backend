"""
Health Check & Monitoring Routes
System health, database status, and external service checks
"""

from fastapi import APIRouter, HTTPException, status
from datetime import datetime
import httpx
from typing import Dict, Any
import os

from app.database import db
from app.config import settings

router = APIRouter()


@router.get("/health")
async def health_check():
    """
    Basic health check endpoint.
    
    - Returns 200 if service is running
    - Useful for load balancers and monitoring tools
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "MegaArtsStore Backend"
    }


@router.get("/health/detailed")
async def detailed_health_check():
    """
    Detailed health check with all service statuses.
    
    - Checks database connection
    - Checks external services (Cloudinary, Razorpay)
    - Returns overall health status
    """
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {}
    }
    
    # Check Database
    try:
        await db.command("ping")
        health_status["services"]["database"] = {
            "status": "healthy",
            "type": "MongoDB",
            "message": "Connected successfully"
        }
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["services"]["database"] = {
            "status": "unhealthy",
            "type": "MongoDB",
            "message": str(e)
        }
    
    # Check Cloudinary
    cloudinary_status = await check_cloudinary()
    health_status["services"]["cloudinary"] = cloudinary_status
    if cloudinary_status["status"] == "unhealthy":
        health_status["status"] = "degraded"
    
    # Check Razorpay
    razorpay_status = await check_razorpay()
    health_status["services"]["razorpay"] = razorpay_status
    if razorpay_status["status"] == "unhealthy":
        health_status["status"] = "degraded"
    
    # Check SMTP
    smtp_status = check_smtp_config()
    health_status["services"]["smtp"] = smtp_status
    if smtp_status["status"] == "unhealthy":
        health_status["status"] = "degraded"
    
    return health_status


@router.get("/health/database")
async def database_health():
    """
    Check database connection and stats.
    
    - Returns database connection status
    - Returns collection counts
    """
    try:
        # Ping database
        await db.command("ping")
        
        # Get database stats
        stats = await db.command("dbStats")
        
        # Get collection counts
        collections = {
            "users": await db.users.count_documents({}),
            "products": await db.products.count_documents({}),
            "orders": await db.orders.count_documents({}),
            "reviews": await db.reviews.count_documents({})
        }
        
        return {
            "status": "healthy",
            "connected": True,
            "database": stats.get("db"),
            "collections": collections,
            "storage_size_mb": round(stats.get("dataSize", 0) / (1024 * 1024), 2)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database connection failed: {str(e)}"
        )


@router.get("/metrics")
async def get_metrics():
    """
    Get system metrics for monitoring.
    
    - Returns database statistics
    - Returns API usage metrics
    """
    try:
        metrics = {
            "timestamp": datetime.utcnow().isoformat(),
            "database": {
                "total_users": await db.users.count_documents({}),
                "active_users": await db.users.count_documents({"is_active": True}),
                "total_products": await db.products.count_documents({}),
                "active_products": await db.products.count_documents({"is_active": True}),
                "total_orders": await db.orders.count_documents({}),
                "pending_orders": await db.orders.count_documents({"status": "pending"}),
                "total_reviews": await db.reviews.count_documents({})
            }
        }
        
        return metrics
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch metrics: {str(e)}"
        )


# Helper Functions

async def check_cloudinary() -> Dict[str, Any]:
    """Check Cloudinary service availability"""
    try:
        cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME")
        api_key = os.getenv("CLOUDINARY_API_KEY")
        
        if not cloud_name or not api_key:
            return {
                "status": "unconfigured",
                "message": "Cloudinary credentials not configured"
            }
        
        # Try to ping Cloudinary API
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://api.cloudinary.com/v1_1/{cloud_name}/resources/image",
                timeout=5.0
            )
            
            if response.status_code in [200, 401]:  # 401 means service is up but auth failed
                return {
                    "status": "healthy",
                    "message": "Cloudinary service is reachable"
                }
            else:
                return {
                    "status": "unhealthy",
                    "message": f"Unexpected status code: {response.status_code}"
                }
    except Exception as e:
        return {
            "status": "unhealthy",
            "message": f"Connection failed: {str(e)}"
        }


async def check_razorpay() -> Dict[str, Any]:
    """Check Razorpay service availability"""
    try:
        key_id = os.getenv("RAZORPAY_KEY_ID")
        key_secret = os.getenv("RAZORPAY_KEY_SECRET")
        
        if not key_id or not key_secret:
            return {
                "status": "unconfigured",
                "message": "Razorpay credentials not configured"
            }
        
        # Try to ping Razorpay API
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://api.razorpay.com/v1/payments",
                auth=(key_id, key_secret),
                timeout=5.0
            )
            
            if response.status_code in [200, 401]:
                return {
                    "status": "healthy",
                    "message": "Razorpay service is reachable"
                }
            else:
                return {
                    "status": "unhealthy",
                    "message": f"Unexpected status code: {response.status_code}"
                }
    except Exception as e:
        return {
            "status": "unhealthy",
            "message": f"Connection failed: {str(e)}"
        }


def check_smtp_config() -> Dict[str, Any]:
    """Check SMTP configuration"""
    smtp_host = os.getenv("SMTP_HOST")
    smtp_user = os.getenv("SMTP_USER")
    smtp_password = os.getenv("SMTP_PASSWORD")
    
    if not all([smtp_host, smtp_user, smtp_password]):
        return {
            "status": "unconfigured",
            "message": "SMTP credentials not configured"
        }
    
    return {
        "status": "configured",
        "message": f"SMTP configured for {smtp_host}"
    }
