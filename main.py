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
    admin, search, payment, recommendations, bulk_operations, tasks
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
    description="Production-grade AR Jewellery Ecommerce Backend",
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

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(admin.router, prefix="/admin", tags=["Admin Dashboard"])
app.include_router(payment.router, prefix="/payment", tags=["Payments"])
app.include_router(products.router, prefix="/product", tags=["Products"])
app.include_router(search.router, prefix="/search", tags=["Search"])
app.include_router(recommendations.router, prefix="/recommendations", tags=["Recommendations"])
app.include_router(orders.router, prefix="/order", tags=["Orders"])
app.include_router(render.router, prefix="/render", tags=["3D Rendering"])
app.include_router(wishlist.router, prefix="/wishlist", tags=["Wishlist"])
app.include_router(cart.router, prefix="/cart", tags=["Cart"])
app.include_router(reviews.router, prefix="/reviews", tags=["Reviews"])
app.include_router(ar_analytics.router, prefix="/ar", tags=["AR Analytics"])
app.include_router(bulk_operations.router, prefix="/bulk", tags=["Bulk Operations"])
app.include_router(tasks.router, prefix="/tasks", tags=["Task Queue"])


@app.get("/", tags=["Health"])
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "MegaArtsStore API",
        "version": "1.0.0"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "database": "connected",
        "blender_enabled": settings.blender_enabled
    }
