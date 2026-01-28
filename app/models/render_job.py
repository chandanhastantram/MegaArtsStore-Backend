"""
Render Job Model
MongoDB document structure for 3D rendering jobs
"""

from datetime import datetime
from typing import Optional, List, Dict
import uuid


class RenderJobDocument:
    """Helper class for creating render job documents"""
    
    @staticmethod
    def create_document(
        product_id: str,
        input_file: str,
        job_type: str = "full_render"
    ) -> Dict:
        """
        Create a new render job document.
        
        Args:
            product_id: Associated product ID
            input_file: URL to the uploaded 3D model
            job_type: Type of job (full_render, optimize, thumbnail)
        
        Returns:
            MongoDB document dictionary
        """
        return {
            "job_id": str(uuid.uuid4()),
            "product_id": product_id,
            "input_file": input_file,
            "job_type": job_type,
            "status": "pending",
            "progress": 0,
            "output_files": {},
            "ar_config": None,
            "error": None,
            "logs": [],
            "created_at": datetime.utcnow(),
            "started_at": None,
            "completed_at": None,
        }
    
    @staticmethod
    def get_status_display(status: str) -> str:
        """Get human-readable status"""
        status_map = {
            "pending": "Pending",
            "validating": "Validating Model",
            "cleaning": "Cleaning Geometry",
            "optimizing": "Optimizing Mesh",
            "rendering": "Generating Renders",
            "exporting": "Exporting Files",
            "completed": "Completed",
            "failed": "Failed"
        }
        return status_map.get(status, status.title())
