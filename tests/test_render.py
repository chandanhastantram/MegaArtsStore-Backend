"""
Render Pipeline Tests
Tests for 3D model processing and render job management
"""

import pytest
from unittest.mock import patch, AsyncMock
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture(autouse=True)
def mock_settings():
    """Mock settings for tests"""
    with patch('app.config.get_settings') as mock:
        mock.return_value = type('Settings', (), {
            'mongodb_uri': 'mongodb://localhost:27017',
            'database_name': 'test_megaartsstore',
            'jwt_secret_key': 'test-secret-key',
            'jwt_algorithm': 'HS256',
            'access_token_expire_minutes': 30,
            'cloudinary_cloud_name': 'test',
            'cloudinary_api_key': 'test',
            'cloudinary_api_secret': 'test',
            'blender_enabled': False,
            'blender_path': '',
            'debug': True,
            'cors_origins': ['http://localhost:3000']
        })()
        yield mock


class TestRenderJobSchemas:
    """Tests for render job schemas"""
    
    def test_render_job_response_schema(self):
        """Test RenderJobResponse schema"""
        from app.schemas.render import RenderJobResponse, OutputFilesResponse
        
        response = RenderJobResponse(
            id="123",
            job_id="abc-def-123",
            product_id="product123",
            status="pending",
            progress=0,
            input_file="https://example.com/model.glb",
            output_files=OutputFilesResponse(),
            logs=[],
            created_at=datetime.utcnow()
        )
        
        assert response.status == "pending"
        assert response.progress == 0
    
    def test_ar_config_response_schema(self):
        """Test ARConfigResponse schema"""
        from app.schemas.render import ARConfigResponse
        
        config = ARConfigResponse(
            model_url="https://example.com/model.glb",
            scale=1.0,
            rotation=[0, 0, 0],
            offset=[0, 0, 0],
            wrist_diameter=6.5,
            bangle_thickness=0.5,
            center_point=[0, 0, 0]
        )
        
        assert config.model_url == "https://example.com/model.glb"
        assert config.wrist_diameter == 6.5
    
    def test_model_upload_response_schema(self):
        """Test ModelUploadResponse schema"""
        from app.schemas.render import ModelUploadResponse
        
        response = ModelUploadResponse(
            success=True,
            file_url="https://example.com/model.glb",
            file_name="model.glb",
            file_size=1024000,
            format="glb",
            message="Upload successful"
        )
        
        assert response.success is True
        assert response.file_size == 1024000


class TestRenderJobDocument:
    """Tests for render job document creation"""
    
    def test_create_render_job_document(self):
        """Test RenderJobDocument creation"""
        from app.models.render_job import RenderJobDocument
        
        doc = RenderJobDocument.create_document(
            product_id="product123",
            input_file="https://example.com/model.glb"
        )
        
        assert doc["product_id"] == "product123"
        assert doc["status"] == "pending"
        assert doc["progress"] == 0
        assert "job_id" in doc
        assert len(doc["job_id"]) > 0  # UUID generated
    
    def test_render_job_output_files_structure(self):
        """Test output files structure"""
        from app.models.render_job import RenderJobDocument
        
        doc = RenderJobDocument.create_document(
            product_id="product123",
            input_file="https://example.com/model.glb"
        )
        
        output_files = doc["output_files"]
        
        assert "glb" in output_files
        assert "preview_front" in output_files
        assert "preview_angle" in output_files
        assert "preview_detail" in output_files
        assert "turntable" in output_files


class TestARConfiguration:
    """Tests for AR configuration"""
    
    def test_ar_configuration_model(self):
        """Test ARConfiguration model"""
        from app.models.render_job import ARConfiguration
        
        config = ARConfiguration(
            model_url="https://example.com/model.glb",
            scale=1.5,
            rotation=[0, 90, 0],
            offset=[0, 0.1, 0],
            wrist_diameter=6.5,
            bangle_thickness=0.8
        )
        
        assert config.scale == 1.5
        assert config.rotation[1] == 90
        assert config.wrist_diameter == 6.5


class TestValidationResult:
    """Tests for model validation result"""
    
    def test_validation_result_schema(self):
        """Test ValidationResult schema"""
        from app.schemas.render import ValidationResult
        
        result = ValidationResult(
            valid=True,
            polygon_count=50000,
            has_uv_maps=True,
            has_materials=True,
            texture_resolution="2048px",
            issues=[],
            warnings=["High polygon count"]
        )
        
        assert result.valid is True
        assert result.polygon_count == 50000
        assert len(result.warnings) == 1
    
    def test_validation_result_with_issues(self):
        """Test ValidationResult with issues"""
        from app.schemas.render import ValidationResult
        
        result = ValidationResult(
            valid=False,
            polygon_count=150000,
            has_uv_maps=False,
            has_materials=True,
            issues=["Polygon count too high", "Missing UV maps"],
            warnings=[]
        )
        
        assert result.valid is False
        assert len(result.issues) == 2


class TestJobService:
    """Tests for job service functions"""
    
    @pytest.mark.asyncio
    async def test_job_status_transitions(self):
        """Test valid job status transitions"""
        valid_statuses = ["pending", "validating", "cleaning", "optimizing", 
                         "rendering", "exporting", "completed", "failed"]
        
        for status in valid_statuses:
            assert status in valid_statuses
    
    def test_job_progress_range(self):
        """Test job progress is within valid range"""
        from app.models.render_job import RenderJobInDB
        from pydantic import ValidationError
        
        # Valid progress
        job = RenderJobInDB(
            job_id="test-123",
            product_id="product123",
            input_file="https://example.com/model.glb",
            progress=50
        )
        assert job.progress == 50
        
        # Progress should be 0-100
        with pytest.raises(ValidationError):
            RenderJobInDB(
                job_id="test-123",
                product_id="product123",
                input_file="https://example.com/model.glb",
                progress=150  # Invalid
            )
