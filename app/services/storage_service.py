"""
Cloudinary Storage Service
Handles file uploads to Cloudinary
"""

import cloudinary
import cloudinary.uploader
from cloudinary.utils import cloudinary_url
from fastapi import UploadFile, HTTPException, status
from typing import Optional, Dict
import os

from app.config import get_settings


def init_cloudinary():
    """Initialize Cloudinary with credentials from settings"""
    settings = get_settings()
    
    cloudinary.config(
        cloud_name=settings.cloudinary_cloud_name,
        api_key=settings.cloudinary_api_key,
        api_secret=settings.cloudinary_api_secret,
        secure=True
    )


async def upload_image(
    file: UploadFile,
    folder: str = "megaartsstore/images",
    transformation: Optional[Dict] = None
) -> Dict:
    """
    Upload an image to Cloudinary.
    
    Args:
        file: FastAPI UploadFile object
        folder: Cloudinary folder path
        transformation: Optional image transformations
    
    Returns:
        Dict with url, public_id, format, width, height
    """
    init_cloudinary()
    
    # Validate file type
    allowed_types = ["image/jpeg", "image/png", "image/webp", "image/gif"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid image type. Allowed: {', '.join(allowed_types)}"
        )
    
    try:
        # Read file contents
        contents = await file.read()
        
        # Default transformation for product images
        if transformation is None:
            transformation = {
                "quality": "auto:good",
                "fetch_format": "auto"
            }
        
        # Upload to Cloudinary
        result = cloudinary.uploader.upload(
            contents,
            folder=folder,
            resource_type="image",
            transformation=transformation
        )
        
        return {
            "url": result["secure_url"],
            "public_id": result["public_id"],
            "format": result["format"],
            "width": result.get("width"),
            "height": result.get("height")
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload image: {str(e)}"
        )


async def upload_3d_model(
    file: UploadFile,
    folder: str = "megaartsstore/models"
) -> Dict:
    """
    Upload a 3D model file to Cloudinary.
    
    Args:
        file: FastAPI UploadFile object (.blend, .fbx, .obj, .glb)
        folder: Cloudinary folder path
    
    Returns:
        Dict with url, public_id, format, size
    """
    init_cloudinary()
    
    # Get file extension
    filename = file.filename or "model"
    ext = os.path.splitext(filename)[1].lower()
    
    # Validate file type
    allowed_extensions = [".blend", ".fbx", ".obj", ".glb", ".gltf"]
    if ext not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid 3D model format. Allowed: {', '.join(allowed_extensions)}"
        )
    
    try:
        # Read file contents
        contents = await file.read()
        file_size = len(contents)
        
        # Upload to Cloudinary as raw file
        result = cloudinary.uploader.upload(
            contents,
            folder=folder,
            resource_type="raw",
            public_id=os.path.splitext(filename)[0],
            use_filename=True,
            unique_filename=True
        )
        
        return {
            "url": result["secure_url"],
            "public_id": result["public_id"],
            "format": ext.replace(".", ""),
            "size": file_size,
            "original_filename": filename
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload 3D model: {str(e)}"
        )


async def upload_video(
    file: UploadFile,
    folder: str = "megaartsstore/videos"
) -> Dict:
    """
    Upload a video file to Cloudinary.
    
    Args:
        file: FastAPI UploadFile object
        folder: Cloudinary folder path
    
    Returns:
        Dict with url, public_id, duration, format
    """
    init_cloudinary()
    
    # Validate file type
    allowed_types = ["video/mp4", "video/webm", "video/quicktime"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid video type. Allowed: {', '.join(allowed_types)}"
        )
    
    try:
        contents = await file.read()
        
        result = cloudinary.uploader.upload(
            contents,
            folder=folder,
            resource_type="video",
            eager=[{"quality": "auto", "fetch_format": "mp4"}]
        )
        
        return {
            "url": result["secure_url"],
            "public_id": result["public_id"],
            "format": result["format"],
            "duration": result.get("duration"),
            "width": result.get("width"),
            "height": result.get("height")
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload video: {str(e)}"
        )


def delete_file(public_id: str, resource_type: str = "image") -> bool:
    """
    Delete a file from Cloudinary.
    
    Args:
        public_id: Cloudinary public ID
        resource_type: 'image', 'video', or 'raw'
    
    Returns:
        True if deleted successfully
    """
    init_cloudinary()
    
    try:
        result = cloudinary.uploader.destroy(
            public_id,
            resource_type=resource_type
        )
        return result.get("result") == "ok"
    except Exception:
        return False


def get_optimized_url(
    public_id: str,
    width: int = None,
    height: int = None,
    quality: str = "auto"
) -> str:
    """
    Get optimized image URL with transformations.
    
    Args:
        public_id: Cloudinary public ID
        width: Target width
        height: Target height
        quality: Quality setting ('auto', 'auto:good', 'auto:best')
    
    Returns:
        Optimized image URL
    """
    init_cloudinary()
    
    transformation = {"quality": quality, "fetch_format": "auto"}
    
    if width:
        transformation["width"] = width
    if height:
        transformation["height"] = height
    if width or height:
        transformation["crop"] = "limit"
    
    url, _ = cloudinary_url(public_id, **transformation)
    return url
