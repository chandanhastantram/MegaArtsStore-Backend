"""
Render Routes
3D model upload, processing, and AR configuration endpoints
"""

from fastapi import APIRouter, HTTPException, status, Depends, UploadFile, File, BackgroundTasks
from typing import Optional

from app.schemas.render import (
    RenderJobResponse,
    RenderJobListResponse,
    ModelUploadResponse,
    ARConfigResponse,
    OutputFilesResponse
)
from app.services.storage_service import upload_3d_model
from app.services import job_service
from app.services.product_service import get_product_by_id, update_product_3d_model, update_ar_config
from app.middleware.rbac import get_admin_or_subadmin, get_admin_user
from app.utils.auth import get_current_user

router = APIRouter()


@router.post("/upload-model", response_model=ModelUploadResponse)
async def upload_model(
    product_id: str,
    file: UploadFile = File(...),
    current_user: dict = Depends(get_admin_or_subadmin)
):
    """
    Upload a 3D model file for a product.
    
    - Admin and SubAdmin only
    - Supports .blend, .fbx, .obj, .glb, .gltf formats
    - Stores original file in Cloudinary
    """
    # Validate product exists
    product = await get_product_by_id(product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Upload to Cloudinary
    result = await upload_3d_model(file, folder=f"megaartsstore/models/{product_id}")
    
    # Update product with original model URL
    await update_product_3d_model(
        product_id,
        model_url=result["url"],
        original_url=result["url"]
    )
    
    return ModelUploadResponse(
        success=True,
        file_url=result["url"],
        file_name=result["original_filename"],
        file_size=result["size"],
        format=result["format"],
        message="Model uploaded successfully. Use /render/process to start processing."
    )


@router.post("/process", response_model=RenderJobResponse)
async def process_model(
    product_id: str,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_admin_or_subadmin)
):
    """
    Start 3D model processing job.
    
    - Admin and SubAdmin only
    - Creates background job for model cleaning, optimization, and GLB export
    - Returns job ID for status tracking
    """
    # Validate product exists and has model
    product = await get_product_by_id(product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    if not product.get("model_3d"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Product has no 3D model uploaded. Upload a model first."
        )
    
    # Create job
    job = await job_service.create_job(
        product_id=product_id,
        input_file=product["model_3d"]
    )
    
    # Add background task
    background_tasks.add_task(job_service.process_job_background, job["job_id"])
    
    return _format_job_response(job)


@router.get("/status/{job_id}", response_model=RenderJobResponse)
async def get_job_status(
    job_id: str,
    current_user: dict = Depends(get_admin_or_subadmin)
):
    """
    Get render job status.
    
    - Admin and SubAdmin only
    - Returns current progress, status, and logs
    """
    job = await job_service.get_job_by_id(job_id)
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    return _format_job_response(job)


@router.get("/result/{job_id}", response_model=RenderJobResponse)
async def get_job_result(
    job_id: str,
    current_user: dict = Depends(get_admin_or_subadmin)
):
    """
    Get render job results.
    
    - Admin and SubAdmin only
    - Returns output files and AR configuration when complete
    """
    job = await job_service.get_job_by_id(job_id)
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    if job["status"] != "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Job is not completed. Current status: {job['status']}"
        )
    
    # Apply AR config to product if available
    if job.get("ar_config"):
        await update_ar_config(job["product_id"], job["ar_config"])
    
    return _format_job_response(job)


@router.get("/ar-config/{product_id}", response_model=ARConfigResponse)
async def get_ar_config(product_id: str):
    """
    Get AR configuration for a product.
    
    - Public endpoint
    - Returns AR alignment data for WebAR try-on
    """
    product = await get_product_by_id(product_id)
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    if not product.get("ar_enabled"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="AR is not enabled for this product"
        )
    
    if not product.get("model_3d"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No 3D model available for this product"
        )
    
    ar_config = product.get("ar_config", {})
    
    return ARConfigResponse(
        model_url=product["model_3d"],
        scale=ar_config.get("scale", 1.0),
        rotation=ar_config.get("rotation", [0, 0, 0]),
        offset=ar_config.get("offset", [0, 0, 0]),
        wrist_diameter=ar_config.get("wrist_diameter", 0.0),
        bangle_thickness=ar_config.get("bangle_thickness", 0.0),
        center_point=ar_config.get("center_point", [0, 0, 0])
    )


@router.get("/jobs/{product_id}", response_model=RenderJobListResponse)
async def get_product_jobs(
    product_id: str,
    current_user: dict = Depends(get_admin_or_subadmin)
):
    """
    Get all render jobs for a product.
    
    - Admin and SubAdmin only
    - Returns job history with logs
    """
    jobs = await job_service.get_jobs_by_product(product_id)
    
    return RenderJobListResponse(
        jobs=[_format_job_response(j) for j in jobs],
        total=len(jobs)
    )


@router.post("/{product_id}/enable-ar")
async def enable_ar(
    product_id: str,
    current_user: dict = Depends(get_admin_user)
):
    """
    Enable AR try-on for a product.
    
    - Admin only
    - Requires completed render job with AR config
    """
    from app.database import get_products_collection
    from bson import ObjectId
    
    product = await get_product_by_id(product_id)
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    if not product.get("model_3d"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Product has no 3D model"
        )
    
    products_collection = get_products_collection()
    await products_collection.update_one(
        {"_id": ObjectId(product_id)},
        {"$set": {"ar_enabled": True}}
    )
    
    return {"message": "AR enabled for product", "product_id": product_id}


@router.post("/{product_id}/disable-ar")
async def disable_ar(
    product_id: str,
    current_user: dict = Depends(get_admin_user)
):
    """
    Disable AR try-on for a product.
    
    - Admin only
    """
    from app.database import get_products_collection
    from bson import ObjectId
    
    products_collection = get_products_collection()
    result = await products_collection.update_one(
        {"_id": ObjectId(product_id)},
        {"$set": {"ar_enabled": False}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    return {"message": "AR disabled for product", "product_id": product_id}


# ============ Helper Functions ============

def _format_job_response(job: dict) -> RenderJobResponse:
    """Format job document to response schema"""
    output_files = job.get("output_files", {})
    
    return RenderJobResponse(
        id=job["_id"],
        job_id=job["job_id"],
        product_id=job["product_id"],
        status=job["status"],
        progress=job["progress"],
        input_file=job["input_file"],
        output_files=OutputFilesResponse(
            glb=output_files.get("glb"),
            preview_front=output_files.get("preview_front"),
            preview_angle=output_files.get("preview_angle"),
            preview_detail=output_files.get("preview_detail"),
            turntable=output_files.get("turntable")
        ),
        ar_config=job.get("ar_config"),
        logs=job.get("logs", []),
        error=job.get("error"),
        created_at=job["created_at"],
        started_at=job.get("started_at"),
        completed_at=job.get("completed_at")
    )
