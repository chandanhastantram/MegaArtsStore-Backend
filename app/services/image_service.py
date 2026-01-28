"""
Image Service
Image optimization and processing for product images
"""

import io
from typing import Tuple, Optional
from PIL import Image
import cloudinary
import cloudinary.uploader
from fastapi import UploadFile

from app.config import get_settings


# Configure Cloudinary
def _configure_cloudinary():
    settings = get_settings()
    cloudinary.config(
        cloud_name=settings.cloudinary_cloud_name,
        api_key=settings.cloudinary_api_key,
        api_secret=settings.cloudinary_api_secret
    )


async def optimize_and_upload_image(
    file: UploadFile,
    folder: str = "megaartsstore/products",
    max_size: Tuple[int, int] = (1200, 1200),
    quality: int = 85,
    format: str = "webp"
) -> dict:
    """
    Optimize and upload a product image.
    
    Args:
        file: Uploaded image file
        folder: Cloudinary folder
        max_size: Maximum dimensions (width, height)
        quality: JPEG/WebP quality (1-100)
        format: Output format (webp, jpg, png)
    
    Returns:
        Upload result with optimized URL
    """
    _configure_cloudinary()
    
    # Read and optimize image
    contents = await file.read()
    img = Image.open(io.BytesIO(contents))
    
    # Convert to RGB if necessary (for WebP/JPEG)
    if img.mode in ('RGBA', 'P') and format in ('jpg', 'jpeg'):
        # Create white background for transparency
        background = Image.new('RGB', img.size, (255, 255, 255))
        if img.mode == 'RGBA':
            background.paste(img, mask=img.split()[3])
        else:
            background.paste(img)
        img = background
    elif img.mode != 'RGB' and format in ('jpg', 'jpeg'):
        img = img.convert('RGB')
    
    # Resize if larger than max_size
    original_size = img.size
    img.thumbnail(max_size, Image.Resampling.LANCZOS)
    
    # Save to buffer
    buffer = io.BytesIO()
    
    if format == 'webp':
        img.save(buffer, format='WEBP', quality=quality, method=6)
    elif format in ('jpg', 'jpeg'):
        img.save(buffer, format='JPEG', quality=quality, optimize=True)
    else:
        img.save(buffer, format='PNG', optimize=True)
    
    buffer.seek(0)
    
    # Upload to Cloudinary
    result = cloudinary.uploader.upload(
        buffer,
        folder=folder,
        format=format,
        resource_type="image"
    )
    
    return {
        "url": result["secure_url"],
        "public_id": result["public_id"],
        "format": format,
        "width": img.size[0],
        "height": img.size[1],
        "original_size": original_size,
        "file_size": result.get("bytes", 0)
    }


async def generate_thumbnails(
    image_url: str,
    sizes: list = None
) -> dict:
    """
    Generate multiple thumbnail sizes using Cloudinary transformations.
    
    Args:
        image_url: Original image URL
        sizes: List of (width, height) tuples
    
    Returns:
        Dictionary of size names to URLs
    """
    if sizes is None:
        sizes = [
            ("thumb", 150, 150),
            ("small", 300, 300),
            ("medium", 600, 600),
            ("large", 1200, 1200)
        ]
    
    # Use Cloudinary URL transformations
    thumbnails = {}
    
    for name, width, height in sizes:
        # Cloudinary URL transformation
        # Replace /upload/ with /upload/c_fill,w_WIDTH,h_HEIGHT,q_auto,f_auto/
        if "/upload/" in image_url:
            transformation = f"c_fill,w_{width},h_{height},q_auto,f_auto"
            thumb_url = image_url.replace("/upload/", f"/upload/{transformation}/")
            thumbnails[name] = thumb_url
    
    return thumbnails


async def delete_image(public_id: str) -> bool:
    """
    Delete an image from Cloudinary.
    
    Args:
        public_id: Cloudinary public ID
    
    Returns:
        True if deleted successfully
    """
    _configure_cloudinary()
    
    try:
        result = cloudinary.uploader.destroy(public_id)
        return result.get("result") == "ok"
    except Exception:
        return False


def get_optimized_url(
    base_url: str,
    width: int = None,
    height: int = None,
    quality: str = "auto",
    format: str = "auto"
) -> str:
    """
    Get optimized Cloudinary URL with transformations.
    
    Args:
        base_url: Original Cloudinary URL
        width: Desired width
        height: Desired height
        quality: Quality setting (auto, low, eco, good, best)
        format: Output format (auto, webp, jpg)
    
    Returns:
        Transformed URL
    """
    if "/upload/" not in base_url:
        return base_url
    
    transformations = [f"q_{quality}", f"f_{format}"]
    
    if width:
        transformations.append(f"w_{width}")
    
    if height:
        transformations.append(f"h_{height}")
    
    if width or height:
        transformations.append("c_fill")
    
    transformation_str = ",".join(transformations)
    
    return base_url.replace("/upload/", f"/upload/{transformation_str}/")
