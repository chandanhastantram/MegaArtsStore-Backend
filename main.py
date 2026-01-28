"""
MegaArtsStore - AR Jewellery Ecommerce Backend
Main FastAPI Application Entry Point
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import get_settings
from app.database import connect_to_database, close_database_connection
from app.routes import (
    auth, products, orders, render, wishlist, cart, reviews, ar_analytics,
    admin, search, payment, recommendations, bulk_operations, tasks,
    health, coupons, inventory, exports, security
)
from app.middleware.rate_limit import RateLimitMiddleware
from app.middleware.request_validation import ValidationMiddleware
from app.services.task_queue import task_queue


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Handles startup and shutdown events.
    """
    # Startup
    print("🚀 Starting MegaArtsStore Backend...")
    await connect_to_database()
    await task_queue.start()
    print("✅ Task queue started")
    
    yield
    
    # Shutdown
    await task_queue.stop()
    await close_database_connection()
    print("👋 MegaArtsStore Backend stopped")


# Initialize FastAPI app
settings = get_settings()

app = FastAPI(
    title="MegaArtsStore API",
    description="Production-grade AR Jewellery Ecommerce Backend with Advanced Features",
    version="1.0.0",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security Middleware
app.add_middleware(ValidationMiddleware)
app.add_middleware(RateLimitMiddleware)

# API v1 Routes
API_V1_PREFIX = "/api/v1"

# Core Features
app.include_router(auth.router, prefix=f"{API_V1_PREFIX}/auth", tags=["Authentication"])
app.include_router(products.router, prefix=f"{API_V1_PREFIX}/products", tags=["Products"])
app.include_router(orders.router, prefix=f"{API_V1_PREFIX}/orders", tags=["Orders"])
app.include_router(cart.router, prefix=f"{API_V1_PREFIX}/cart", tags=["Cart"])
app.include_router(wishlist.router, prefix=f"{API_V1_PREFIX}/wishlist", tags=["Wishlist"])
app.include_router(reviews.router, prefix=f"{API_V1_PREFIX}/reviews", tags=["Reviews"])
app.include_router(payment.router, prefix=f"{API_V1_PREFIX}/payment", tags=["Payments"])

# AR & 3D Features
app.include_router(render.router, prefix=f"{API_V1_PREFIX}/render", tags=["3D Rendering"])
app.include_router(ar_analytics.router, prefix=f"{API_V1_PREFIX}/ar", tags=["AR Analytics"])

# Admin Features
app.include_router(admin.router, prefix=f"{API_V1_PREFIX}/admin", tags=["Admin Dashboard"])
app.include_router(bulk_operations.router, prefix=f"{API_V1_PREFIX}/bulk", tags=["Bulk Operations"])
app.include_router(inventory.router, prefix=f"{API_V1_PREFIX}/inventory", tags=["Inventory Management"])
app.include_router(exports.router, prefix=f"{API_V1_PREFIX}/exports", tags=["Data Export"])

# Advanced Features
app.include_router(coupons.router, prefix=f"{API_V1_PREFIX}/coupons", tags=["Coupons & Discounts"])
app.include_router(security.router, prefix=f"{API_V1_PREFIX}/security", tags=["Security"])
app.include_router(search.router, prefix=f"{API_V1_PREFIX}/search", tags=["Search"])
app.include_router(recommendations.router, prefix=f"{API_V1_PREFIX}/recommendations", tags=["Recommendations"])
app.include_router(tasks.router, prefix=f"{API_V1_PREFIX}/tasks", tags=["Task Queue"])

# Health & Monitoring (no versioning for health checks)
app.include_router(health.router, prefix="/health", tags=["Health & Monitoring"])


@app.get("/", tags=["Root"])
async def root():
    """API root endpoint"""
    return {
        "service": "MegaArtsStore API",
        "version": "1.0.0",
        "api_version": "v1",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/api", tags=["Root"])
async def api_info():
    """API information"""
    return {
        "version": "1.0.0",
        "api_prefix": "/api/v1",
        "features": [
            "Authentication & Authorization",
            "Product Management",
            "Order Processing",
            "Payment Integration (Razorpay)",
            "3D Rendering & AR",
            "Inventory Management",
            "Coupon System",
            "Advanced Security (2FA, Password Reset)",
            "Data Export (CSV)",
            "Health Monitoring"
        ]
    }
