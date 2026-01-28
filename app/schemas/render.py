"""
Render Job Pydantic Schemas
Request/Response models for 3D rendering endpoints
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# ============ Request Schemas ============

class RenderJobCreate(BaseModel):
    """Schema for creating a render job"""
    product_id: str


class RenderOptionsRequest(BaseModel):
    """Schema for render options"""
    generate_preview: bool = True
    generate_turntable: bool = False
    optimize_for_ar: bool = True
    compression_level: str = Field(default="medium", pattern="^(low|medium|high)$")


# ============ Response Schemas ============

class OutputFilesResponse(BaseModel):
    """Schema for render output files"""
    glb: Optional[str] = None
    preview_front: Optional[str] = None
    preview_angle: Optional[str] = None
    preview_detail: Optional[str] = None
    turntable: Optional[str] = None


class RenderJobResponse(BaseModel):
    """Schema for render job response"""
    id: str
    job_id: str
    product_id: str
    status: str
    progress: int
    input_file: str
    output_files: OutputFilesResponse
    ar_config: Optional[dict] = None
    logs: List[str] = []
    error: Optional[str] = None
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class RenderJobListResponse(BaseModel):
    """Schema for render job list"""
    jobs: List[RenderJobResponse]
    total: int


class ARConfigResponse(BaseModel):
    """Schema for AR configuration response"""
    model_url: str
    scale: float
    rotation: List[float]
    offset: List[float]
    wrist_diameter: float
    bangle_thickness: float = 0.0
    center_point: List[float] = [0, 0, 0]


# ============ Upload Schemas ============

class ModelUploadResponse(BaseModel):
    """Schema for model upload response"""
    success: bool
    file_url: str
    file_name: str
    file_size: int
    format: str
    message: str


class ValidationResult(BaseModel):
    """Schema for model validation result"""
    valid: bool
    polygon_count: int
    has_uv_maps: bool
    has_materials: bool
    texture_resolution: Optional[str] = None
    issues: List[str] = []
    warnings: List[str] = []
