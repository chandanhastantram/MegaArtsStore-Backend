"""
AR Analytics Routes
AR try-on tracking, size recommendation, and model preload endpoints
"""

from fastapi import APIRouter, HTTPException, status, Depends, Query
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

from app.services import ar_analytics_service
from app.services.product_service import get_product_by_id, get_products
from app.utils.auth import get_current_user
from app.middleware.rbac import get_admin_user

router = APIRouter()


# ============ Schemas ============

class TryOnEventCreate(BaseModel):
    """Schema for logging a try-on event"""
    product_id: str
    session_id: Optional[str] = None
    device_type: str = Field(default="mobile", pattern="^(mobile|tablet|desktop)$")
    duration_seconds: int = Field(ge=0, default=0)
    screenshot_taken: bool = False


class TryOnEventResponse(BaseModel):
    """Schema for try-on event response"""
    event_id: str
    product_id: str
    user_id: Optional[str] = None
    session_id: str
    device_type: str
    duration_seconds: int
    screenshot_taken: bool
    created_at: datetime


class TryOnConversionUpdate(BaseModel):
    """Schema for updating try-on conversion"""
    event_id: str
    added_to_cart: bool = False
    purchased: bool = False


class WristMeasurementCreate(BaseModel):
    """Schema for saving wrist measurement"""
    wrist_circumference: float = Field(gt=0, description="Wrist circumference in cm")
    wrist_width: float = Field(gt=0, description="Wrist width in cm")
    measurement_method: str = "ar_scan"
    confidence_score: float = Field(ge=0, le=1, default=0.0)


class SizeRecommendationRequest(BaseModel):
    """Schema for size recommendation request"""
    wrist_circumference: Optional[float] = Field(None, gt=0, description="Wrist circumference in cm")


class SizeRecommendationResponse(BaseModel):
    """Schema for size recommendation response"""
    wrist_circumference: float
    required_diameter: float
    recommended_size: str
    recommended_diameter: float
    fit_type: str
    note: str


class ProductARStats(BaseModel):
    """Schema for product AR stats"""
    total_try_ons: int
    unique_users: int
    avg_duration_seconds: float
    screenshot_rate: float
    cart_conversion_rate: float
    purchase_conversion_rate: float


class ModelPreloadItem(BaseModel):
    """Schema for model preload item"""
    product_id: str
    product_name: str
    model_url: str
    file_size: Optional[int] = None
    thumbnail: Optional[str] = None


class ModelPreloadResponse(BaseModel):
    """Schema for model preload response"""
    models: List[ModelPreloadItem]
    total: int


# ============ Try-On Analytics Routes ============

@router.post("/try-on/log", response_model=TryOnEventResponse)
async def log_try_on(
    event: TryOnEventCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    Log an AR try-on event.
    
    - Authenticated users
    - Tracks when user tries on a product using AR
    """
    # Verify product exists
    product = await get_product_by_id(event.product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    result = await ar_analytics_service.log_try_on_event(
        product_id=event.product_id,
        user_id=current_user["_id"],
        session_id=event.session_id,
        device_type=event.device_type,
        duration_seconds=event.duration_seconds,
        screenshot_taken=event.screenshot_taken
    )
    
    return TryOnEventResponse(
        event_id=result["event_id"],
        product_id=result["product_id"],
        user_id=result.get("user_id"),
        session_id=result["session_id"],
        device_type=result["device_type"],
        duration_seconds=result["duration_seconds"],
        screenshot_taken=result["screenshot_taken"],
        created_at=result["created_at"]
    )


@router.post("/try-on/anonymous", response_model=TryOnEventResponse)
async def log_try_on_anonymous(event: TryOnEventCreate):
    """
    Log an AR try-on event for anonymous users.
    
    - Public endpoint
    - Uses session_id to track anonymous users
    """
    product = await get_product_by_id(event.product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    result = await ar_analytics_service.log_try_on_event(
        product_id=event.product_id,
        user_id=None,
        session_id=event.session_id,
        device_type=event.device_type,
        duration_seconds=event.duration_seconds,
        screenshot_taken=event.screenshot_taken
    )
    
    return TryOnEventResponse(
        event_id=result["event_id"],
        product_id=result["product_id"],
        user_id=None,
        session_id=result["session_id"],
        device_type=result["device_type"],
        duration_seconds=result["duration_seconds"],
        screenshot_taken=result["screenshot_taken"],
        created_at=result["created_at"]
    )


@router.post("/try-on/conversion")
async def update_conversion(update: TryOnConversionUpdate):
    """
    Update try-on event with conversion data.
    
    - Call when user adds to cart or purchases after AR try-on
    """
    success = await ar_analytics_service.update_try_on_conversion(
        event_id=update.event_id,
        added_to_cart=update.added_to_cart,
        purchased=update.purchased
    )
    
    return {"success": success}


@router.get("/stats/{product_id}", response_model=ProductARStats)
async def get_product_ar_stats(
    product_id: str,
    current_user: dict = Depends(get_admin_user)
):
    """
    Get AR analytics for a specific product.
    
    - Admin only
    """
    stats = await ar_analytics_service.get_product_ar_stats(product_id)
    return ProductARStats(**stats)


@router.get("/dashboard")
async def get_ar_dashboard(
    days: int = Query(30, ge=1, le=365),
    current_user: dict = Depends(get_admin_user)
):
    """
    Get AR analytics dashboard.
    
    - Admin only
    - Returns overall AR usage statistics
    """
    stats = await ar_analytics_service.get_ar_dashboard_stats(days)
    return stats


@router.get("/top-products")
async def get_top_tried_products(
    limit: int = Query(10, ge=1, le=50),
    days: int = Query(30, ge=1, le=365),
    current_user: dict = Depends(get_admin_user)
):
    """
    Get most tried-on products.
    
    - Admin only
    """
    products = await ar_analytics_service.get_top_tried_products(limit, days)
    return {"products": products}


# ============ Size Recommendation Routes ============

@router.post("/wrist-measurement")
async def save_wrist_measurement(
    measurement: WristMeasurementCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    Save wrist measurement from AR scan.
    
    - Authenticated users only
    - Stores measurement for future size recommendations
    """
    result = await ar_analytics_service.save_wrist_measurement(
        user_id=current_user["_id"],
        wrist_circumference=measurement.wrist_circumference,
        wrist_width=measurement.wrist_width,
        measurement_method=measurement.measurement_method,
        confidence_score=measurement.confidence_score
    )
    
    return {
        "message": "Measurement saved",
        "measurement_id": result["measurement_id"]
    }


@router.get("/wrist-measurements")
async def get_my_measurements(
    current_user: dict = Depends(get_current_user)
):
    """
    Get user's saved wrist measurements.
    
    - Authenticated users only
    """
    measurements = await ar_analytics_service.get_user_measurements(current_user["_id"])
    return {"measurements": measurements}


@router.post("/size-recommendation", response_model=SizeRecommendationResponse)
async def get_size_recommendation(
    request: SizeRecommendationRequest = None,
    current_user: dict = Depends(get_current_user)
):
    """
    Get bangle size recommendation.
    
    - Uses provided wrist measurement or saved measurements
    - Returns recommended Indian bangle size
    """
    wrist_circumference = request.wrist_circumference if request else None
    
    result = await ar_analytics_service.recommend_bangle_size(
        user_id=current_user["_id"],
        wrist_circumference=wrist_circumference
    )
    
    if "error" in result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["error"]
        )
    
    return SizeRecommendationResponse(**result)


@router.get("/size-chart")
async def get_size_chart():
    """
    Get bangle size chart.
    
    - Public endpoint
    - Returns Indian bangle sizing standard
    """
    SIZE_CHART = {
        "2-2": {"diameter_cm": 5.08, "diameter_inches": 2.0, "wrist_range": "13-15 cm"},
        "2-4": {"diameter_cm": 5.4, "diameter_inches": 2.125, "wrist_range": "15-16 cm"},
        "2-6": {"diameter_cm": 5.72, "diameter_inches": 2.25, "wrist_range": "16-17 cm"},
        "2-8": {"diameter_cm": 6.03, "diameter_inches": 2.375, "wrist_range": "17-18 cm"},
        "2-10": {"diameter_cm": 6.35, "diameter_inches": 2.5, "wrist_range": "18-19 cm"},
        "2-12": {"diameter_cm": 6.67, "diameter_inches": 2.625, "wrist_range": "19-20 cm"},
        "2-14": {"diameter_cm": 6.98, "diameter_inches": 2.75, "wrist_range": "20-21 cm"}
    }
    
    return {"size_chart": SIZE_CHART, "standard": "Indian Bangle Sizing"}


# ============ Model Preload Routes ============

@router.get("/preload/featured", response_model=ModelPreloadResponse)
async def preload_featured_models():
    """
    Get featured AR-enabled models for preloading.
    
    - Public endpoint
    - Returns models that should be cached for offline AR
    """
    from app.schemas.product import ProductFilter
    
    products, total = await get_products(
        filters=ProductFilter(ar_enabled=True, featured=True),
        page=1,
        per_page=10
    )
    
    models = []
    for p in products:
        if p.get("model_3d"):
            models.append(ModelPreloadItem(
                product_id=p["_id"],
                product_name=p["name"],
                model_url=p["model_3d"],
                thumbnail=p["images"][0] if p.get("images") else None
            ))
    
    return ModelPreloadResponse(models=models, total=len(models))


@router.get("/preload/category/{category}")
async def preload_category_models(category: str):
    """
    Get AR-enabled models by category for preloading.
    
    - Public endpoint
    """
    from app.schemas.product import ProductFilter
    
    products, total = await get_products(
        filters=ProductFilter(category=category, ar_enabled=True),
        page=1,
        per_page=20
    )
    
    models = []
    for p in products:
        if p.get("model_3d"):
            models.append({
                "product_id": p["_id"],
                "product_name": p["name"],
                "model_url": p["model_3d"],
                "thumbnail": p["images"][0] if p.get("images") else None
            })
    
    return {"models": models, "total": len(models), "category": category}


@router.post("/preload/batch")
async def preload_batch_models(product_ids: List[str]):
    """
    Get specific models for batch preloading.
    
    - Public endpoint
    - Accepts list of product IDs
    """
    models = []
    
    for product_id in product_ids:
        product = await get_product_by_id(product_id)
        if product and product.get("model_3d") and product.get("ar_enabled"):
            models.append({
                "product_id": product["_id"],
                "product_name": product["name"],
                "model_url": product["model_3d"],
                "ar_config": product.get("ar_config"),
                "thumbnail": product["images"][0] if product.get("images") else None
            })
    
    return {"models": models, "total": len(models)}
