"""
Product Routes
Product CRUD, filtering, and management endpoints
"""

from fastapi import APIRouter, HTTPException, status, Depends, UploadFile, File, Query
from typing import List, Optional
from bson import ObjectId

from app.schemas.product import (
    ProductCreate,
    ProductUpdate,
    ProductFilter,
    ProductResponse,
    ProductListResponse,
    ReviewCreate,
    CategoryCreate,
    CategoryResponse,
    ARConfigResponse
)
from app.services import product_service
from app.services.storage_service import upload_image
from app.utils.auth import get_current_user
from app.middleware.rbac import get_admin_user, get_admin_or_subadmin

router = APIRouter()


@router.post("/create", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    product_data: ProductCreate,
    current_user: dict = Depends(get_admin_or_subadmin)
):
    """
    Create a new product.
    
    - Admin and SubAdmin only
    - Returns created product
    """
    product = await product_service.create_product(
        product_data=product_data,
        created_by=current_user["_id"]
    )
    
    return _format_product_response(product)


@router.get("/list", response_model=ProductListResponse)
async def list_products(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    category: Optional[str] = None,
    material: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    search: Optional[str] = None,
    ar_enabled: Optional[bool] = None,
    featured: Optional[bool] = None
):
    """
    List products with filtering and pagination.
    
    - Public endpoint
    - Supports filtering by category, material, price range, AR status
    """
    filters = ProductFilter(
        category=category,
        material=material,
        min_price=min_price,
        max_price=max_price,
        search=search,
        ar_enabled=ar_enabled,
        featured=featured
    )
    
    products, total = await product_service.get_products(
        filters=filters,
        page=page,
        per_page=per_page
    )
    
    return ProductListResponse(
        products=[_format_product_response(p) for p in products],
        total=total,
        page=page,
        per_page=per_page
    )


@router.get("/admin/list", response_model=ProductListResponse)
async def list_all_products(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(get_admin_or_subadmin)
):
    """
    List all products including hidden ones.
    
    - Admin and SubAdmin only
    """
    products, total = await product_service.get_products(
        page=page,
        per_page=per_page,
        include_hidden=True
    )
    
    return ProductListResponse(
        products=[_format_product_response(p) for p in products],
        total=total,
        page=page,
        per_page=per_page
    )


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(product_id: str):
    """
    Get a single product by ID.
    
    - Public endpoint
    """
    product = await product_service.get_product_by_id(product_id)
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    return _format_product_response(product)


@router.put("/update/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: str,
    update_data: ProductUpdate,
    current_user: dict = Depends(get_admin_user)
):
    """
    Update a product.
    
    - Admin only
    """
    # Check if product exists
    existing = await product_service.get_product_by_id(product_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    product = await product_service.update_product(product_id, update_data)
    
    return _format_product_response(product)


@router.delete("/delete/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: str,
    current_user: dict = Depends(get_admin_user)
):
    """
    Delete a product.
    
    - Admin only
    """
    deleted = await product_service.delete_product(product_id)
    
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    return None


@router.post("/{product_id}/images", response_model=ProductResponse)
async def upload_product_images(
    product_id: str,
    files: List[UploadFile] = File(...),
    current_user: dict = Depends(get_admin_or_subadmin)
):
    """
    Upload images for a product.
    
    - Admin and SubAdmin only
    - Supports multiple image uploads
    """
    # Check if product exists
    existing = await product_service.get_product_by_id(product_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Upload images
    image_urls = []
    for file in files:
        result = await upload_image(file, folder=f"megaartsstore/products/{product_id}")
        image_urls.append(result["url"])
    
    # Update product
    product = await product_service.add_product_images(product_id, image_urls)
    
    return _format_product_response(product)


@router.post("/{product_id}/review", response_model=ProductResponse)
async def add_product_review(
    product_id: str,
    review_data: ReviewCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    Add a review to a product.
    
    - Authenticated users only
    """
    # Check if product exists
    existing = await product_service.get_product_by_id(product_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    product = await product_service.add_review(
        product_id=product_id,
        user_id=current_user["_id"],
        user_name=current_user["name"],
        rating=review_data.rating,
        comment=review_data.comment
    )
    
    return _format_product_response(product)


# ============ Category Endpoints ============

@router.post("/category/create", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    category_data: CategoryCreate,
    current_user: dict = Depends(get_admin_user)
):
    """
    Create a new category.
    
    - Admin only
    """
    category = await product_service.create_category(
        name=category_data.name,
        description=category_data.description,
        image=category_data.image
    )
    
    return CategoryResponse(
        id=category["_id"],
        name=category["name"],
        description=category.get("description"),
        image=category.get("image"),
        product_count=0
    )


@router.get("/categories/list", response_model=List[CategoryResponse])
async def list_categories():
    """
    List all categories.
    
    - Public endpoint
    """
    categories = await product_service.get_categories()
    
    return [
        CategoryResponse(
            id=cat["_id"],
            name=cat["name"],
            description=cat.get("description"),
            image=cat.get("image"),
            product_count=cat.get("product_count", 0)
        )
        for cat in categories
    ]


# ============ Helper Functions ============

def _format_product_response(product: dict) -> ProductResponse:
    """Format product document to response schema"""
    ar_config = None
    if product.get("ar_config"):
        ar_config = ARConfigResponse(
            scale=product["ar_config"].get("scale", 1.0),
            rotation=product["ar_config"].get("rotation", [0, 0, 0]),
            offset=product["ar_config"].get("offset", [0, 0, 0]),
            wrist_diameter=product["ar_config"].get("wrist_diameter", 0.0)
        )
    
    return ProductResponse(
        id=product["_id"],
        name=product["name"],
        description=product["description"],
        price=product["price"],
        category=product["category"],
        material=product["material"],
        sizes=product.get("sizes", []),
        images=product.get("images", []),
        model_3d=product.get("model_3d"),
        ar_enabled=product.get("ar_enabled", False),
        ar_config=ar_config,
        visibility=product.get("visibility", True),
        featured=product.get("featured", False),
        stock=product.get("stock", 0),
        reviews=product.get("reviews", []),
        avg_rating=product.get("avg_rating", 0.0),
        created_at=product["created_at"]
    )
