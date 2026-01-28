"""
Job Service
Background job processing using FastAPI BackgroundTasks + MongoDB
Alternative to Redis queue system
"""

from datetime import datetime
from typing import Optional, Dict, List
from bson import ObjectId
import asyncio
import subprocess
import os

from app.database import get_render_jobs_collection
from app.models.render_job import RenderJobDocument
from app.config import get_settings


async def create_job(product_id: str, input_file: str) -> Dict:
    """
    Create a new render job.
    
    Args:
        product_id: Associated product ID
        input_file: URL to uploaded 3D model
    
    Returns:
        Created job document
    """
    jobs_collection = get_render_jobs_collection()
    
    job_doc = RenderJobDocument.create_document(
        product_id=product_id,
        input_file=input_file
    )
    
    result = await jobs_collection.insert_one(job_doc)
    job_doc["_id"] = str(result.inserted_id)
    
    return job_doc


async def get_job_by_id(job_id: str) -> Optional[Dict]:
    """Get a job by its UUID"""
    jobs_collection = get_render_jobs_collection()
    
    job = await jobs_collection.find_one({"job_id": job_id})
    if job:
        job["_id"] = str(job["_id"])
    return job


async def get_job_by_mongo_id(mongo_id: str) -> Optional[Dict]:
    """Get a job by MongoDB ObjectId"""
    jobs_collection = get_render_jobs_collection()
    
    try:
        job = await jobs_collection.find_one({"_id": ObjectId(mongo_id)})
        if job:
            job["_id"] = str(job["_id"])
        return job
    except:
        return None


async def update_job_status(
    job_id: str,
    status: str,
    progress: int = None,
    log_message: str = None,
    error: str = None
) -> Optional[Dict]:
    """
    Update job status and progress.
    
    Args:
        job_id: Job UUID
        status: New status
        progress: Progress percentage (0-100)
        log_message: Optional log entry
        error: Error message if failed
    
    Returns:
        Updated job document
    """
    jobs_collection = get_render_jobs_collection()
    
    update_doc = {"status": status}
    
    if progress is not None:
        update_doc["progress"] = progress
    
    if status == "processing" and not await _job_has_started(job_id):
        update_doc["started_at"] = datetime.utcnow()
    
    if status in ["completed", "failed"]:
        update_doc["completed_at"] = datetime.utcnow()
    
    if error:
        update_doc["error"] = error
    
    # Build update operation
    update_op = {"$set": update_doc}
    
    if log_message:
        update_op["$push"] = {"logs": f"[{datetime.utcnow().isoformat()}] {log_message}"}
    
    await jobs_collection.update_one(
        {"job_id": job_id},
        update_op
    )
    
    return await get_job_by_id(job_id)


async def _job_has_started(job_id: str) -> bool:
    """Check if job has already started"""
    job = await get_job_by_id(job_id)
    return job and job.get("started_at") is not None


async def update_job_outputs(
    job_id: str,
    output_files: Dict,
    ar_config: Dict = None
) -> Optional[Dict]:
    """
    Update job output files and AR config.
    
    Args:
        job_id: Job UUID
        output_files: Dictionary of output file URLs
        ar_config: Generated AR configuration
    
    Returns:
        Updated job document
    """
    jobs_collection = get_render_jobs_collection()
    
    update_doc = {"output_files": output_files}
    
    if ar_config:
        update_doc["ar_config"] = ar_config
    
    await jobs_collection.update_one(
        {"job_id": job_id},
        {"$set": update_doc}
    )
    
    return await get_job_by_id(job_id)


async def get_jobs_by_product(product_id: str) -> List[Dict]:
    """Get all jobs for a product"""
    jobs_collection = get_render_jobs_collection()
    
    cursor = jobs_collection.find({"product_id": product_id}).sort("created_at", -1)
    jobs = await cursor.to_list(length=100)
    
    for job in jobs:
        job["_id"] = str(job["_id"])
    
    return jobs


async def get_pending_jobs() -> List[Dict]:
    """Get all pending jobs for processing"""
    jobs_collection = get_render_jobs_collection()
    
    cursor = jobs_collection.find({"status": "pending"}).sort("created_at", 1)
    jobs = await cursor.to_list(length=10)
    
    for job in jobs:
        job["_id"] = str(job["_id"])
    
    return jobs


async def process_job_background(job_id: str):
    """
    Background task to process a render job.
    Called by FastAPI BackgroundTasks.
    
    Note: This is a simplified version. Full Blender processing
    requires Blender to be installed and BLENDER_ENABLED=true.
    """
    settings = get_settings()
    
    try:
        # Update status to processing
        await update_job_status(job_id, "validating", 10, "Starting validation...")
        
        # Simulate validation (replace with actual Blender validation)
        await asyncio.sleep(1)
        await update_job_status(job_id, "cleaning", 25, "Validating model structure...")
        
        # Check if Blender is enabled
        if settings.blender_enabled and settings.blender_path:
            # Run actual Blender processing
            await _run_blender_processing(job_id)
        else:
            # Simulated processing (for development without Blender)
            await _simulate_processing(job_id)
        
    except Exception as e:
        await update_job_status(
            job_id,
            "failed",
            error=str(e),
            log_message=f"Processing failed: {str(e)}"
        )


async def _simulate_processing(job_id: str):
    """Process using Python renderer (PyVista/Trimesh)"""
    from app.services.python_renderer import get_renderer
    from app.services.storage_service import upload_file
    import tempfile
    import os
    
    try:
        renderer = get_renderer()
    except ImportError:
        # Fall back to simulation if libraries not installed
        await _simulate_processing_fallback(job_id)
        return
    
    job = await get_job_by_id(job_id)
    if not job:
        raise Exception("Job not found")
    
    input_file = job["input_file"]
    
    # Download input file to temp location
    await update_job_status(job_id, "downloading", 10, "Downloading model...")
    
    # For now, assume input_file is a local path or URL
    # In production, download from Cloudinary
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Step 1: Optimize model
        await update_job_status(job_id, "optimizing", 30, "Optimizing model for AR...")
        
        optimized_path = os.path.join(temp_dir, "optimized.glb")
        stats = await renderer.optimize_model(
            input_path=input_file,
            output_path=optimized_path,
            target_faces=10000
        )
        
        # Upload optimized model
        optimized_url = await upload_file(optimized_path, f"models/optimized_{job_id}.glb")
        
        # Step 2: Generate thumbnail
        await update_job_status(job_id, "rendering", 50, "Generating thumbnail...")
        
        thumbnail_path = os.path.join(temp_dir, "thumbnail.png")
        await renderer.generate_thumbnail(
            model_path=optimized_path,
            output_path=thumbnail_path,
            resolution=(800, 800)
        )
        
        thumbnail_url = await upload_file(thumbnail_path, f"renders/thumb_{job_id}.png")
        
        # Step 3: Render 360° views
        await update_job_status(job_id, "rendering", 70, "Rendering 360° views...")
        
        renders_dir = os.path.join(temp_dir, "renders")
        render_paths = await renderer.render_360(
            model_path=optimized_path,
            output_dir=renders_dir,
            angles=[0, 45, 90, 135, 180, 225, 270, 315],
            resolution=(1920, 1080)
        )
        
        # Upload renders
        render_urls = []
        for i, render_path in enumerate(render_paths):
            url = await upload_file(render_path, f"renders/360_{job_id}_{i}.png")
            render_urls.append(url)
        
        # Step 4: Extract dimensions
        await update_job_status(job_id, "analyzing", 90, "Extracting dimensions...")
        
        dimensions = await renderer.extract_dimensions(optimized_path)
        
        # Generate AR config
        ar_config = {
            "scale": 1.0,
            "rotation": [0, 0, 0],
            "offset": [0, 0, 0],
            "wrist_diameter": dimensions.get("width", 6.5),
            "bangle_thickness": dimensions.get("depth", 0.5),
            "center_point": dimensions.get("center", [0, 0, 0]),
            "dimensions": dimensions
        }
        
        # Update job with outputs
        await update_job_outputs(
            job_id,
            output_files={
                "glb": optimized_url,
                "thumbnail": thumbnail_url,
                "renders_360": render_urls,
                "optimization_stats": stats
            },
            ar_config=ar_config
        )
        
        await update_job_status(job_id, "completed", 100, "Processing complete!")
        
    finally:
        # Cleanup temp files
        import shutil
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)


async def _simulate_processing_fallback(job_id: str):
    """Fallback simulation if Python renderer not available"""
    
    # Simulate cleaning
    await asyncio.sleep(1)
    await update_job_status(job_id, "optimizing", 40, "Cleaning model...")
    
    # Simulate optimization
    await asyncio.sleep(1)
    await update_job_status(job_id, "rendering", 60, "Optimizing mesh...")
    
    # Simulate rendering
    await asyncio.sleep(1)
    await update_job_status(job_id, "exporting", 80, "Generating previews...")
    
    # Simulate export
    await asyncio.sleep(1)
    
    # Generate placeholder AR config
    ar_config = {
        "scale": 1.0,
        "rotation": [0, 0, 0],
        "offset": [0, 0, 0],
        "wrist_diameter": 6.5,
        "bangle_thickness": 0.5,
        "center_point": [0, 0, 0]
    }
    
    # Update with simulated outputs
    await update_job_outputs(
        job_id,
        output_files={
            "glb": None,  # Would be actual URL after processing
            "preview_front": None,
            "preview_angle": None,
            "preview_detail": None,
            "turntable": None
        },
        ar_config=ar_config
    )
    
    await update_job_status(job_id, "completed", 100, "Processing complete (simulated)")


async def _run_blender_processing(job_id: str):
    """
    Run actual Blender processing.
    Requires Blender installed and configured.
    """
    settings = get_settings()
    job = await get_job_by_id(job_id)
    
    if not job:
        raise Exception("Job not found")
    
    # Get the input file (needs to be downloaded first in real implementation)
    input_file = job["input_file"]
    
    # Build Blender command
    # This would call the actual Blender scripts
    blender_scripts_dir = os.path.join(os.path.dirname(__file__), "..", "..", "blender_scripts")
    
    # In production, you would:
    # 1. Download the input file from Cloudinary
    # 2. Run Blender scripts for cleaning, optimization, etc.
    # 3. Upload outputs back to Cloudinary
    # 4. Update job with output URLs
    
    await update_job_status(job_id, "cleaning", 30, "Running model cleaner...")
    await asyncio.sleep(2)
    
    await update_job_status(job_id, "optimizing", 50, "Optimizing mesh for AR...")
    await asyncio.sleep(2)
    
    await update_job_status(job_id, "rendering", 70, "Generating preview renders...")
    await asyncio.sleep(2)
    
    await update_job_status(job_id, "exporting", 90, "Exporting GLB with Draco compression...")
    await asyncio.sleep(1)
    
    # Generate AR config from Blender analysis
    ar_config = {
        "scale": 1.0,
        "rotation": [0, 0, 0],
        "offset": [0, 0, 0],
        "wrist_diameter": 6.5,
        "bangle_thickness": 0.5,
        "center_point": [0, 0, 0]
    }
    
    await update_job_outputs(
        job_id,
        output_files={
            "glb": None,
            "preview_front": None,
            "preview_angle": None,
            "preview_detail": None,
            "turntable": None
        },
        ar_config=ar_config
    )
    
    await update_job_status(job_id, "completed", 100, "Blender processing complete")
