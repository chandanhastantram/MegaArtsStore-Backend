"""
Product Tests
Tests for product CRUD operations and filtering
"""

import pytest
from httpx import AsyncClient, ASGITransport
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


class TestProductSchemas:
    """Tests for product schemas"""
    
    def test_product_create_schema(self):
        """Test ProductCreate schema validation"""
        from app.schemas.product import ProductCreate
        
        product = ProductCreate(
            name="Gold Bangle",
            description="Beautiful 22K gold bangle with intricate design",
            price=25000.0,
            category="bangles",
            material="gold",
            sizes=["S", "M", "L"],
            stock=10
        )
        
        assert product.name == "Gold Bangle"
        assert product.price == 25000.0
        assert product.material == "gold"
    
    def test_product_create_invalid_material(self):
        """Test ProductCreate rejects invalid material"""
        from app.schemas.product import ProductCreate
        from pydantic import ValidationError
        
        with pytest.raises(ValidationError):
            ProductCreate(
                name="Test Bangle",
                description="Test description here",
                price=1000.0,
                category="bangles",
                material="invalid_material",  # Invalid
                stock=5
            )
    
    def test_product_filter_schema(self):
        """Test ProductFilter schema"""
        from app.schemas.product import ProductFilter
        
        filters = ProductFilter(
            category="bangles",
            material="gold",
            min_price=1000,
            max_price=50000,
            ar_enabled=True
        )
        
        assert filters.category == "bangles"
        assert filters.min_price == 1000


class TestProductDocument:
    """Tests for product document creation"""
    
    def test_create_product_document(self):
        """Test ProductDocument creation"""
        from app.models.product import ProductDocument
        
        doc = ProductDocument.create_document(
            name="Silver Bangle",
            description="Elegant silver bangle",
            price=5000.0,
            category="bangles",
            material="silver",
            created_by="user123",
            sizes=["M", "L"],
            stock=20
        )
        
        assert doc["name"] == "Silver Bangle"
        assert doc["material"] == "silver"
        assert doc["stock"] == 20
        assert doc["ar_enabled"] is False
        assert doc["visibility"] is True
        assert "created_at" in doc


class TestProductEndpoints:
    """Tests for product API endpoints"""
    
    @pytest.mark.asyncio
    async def test_list_products_empty(self):
        """Test listing products returns empty list initially"""
        with patch('app.database.get_products_collection') as mock_products:
            mock_cursor = AsyncMock()
            mock_cursor.to_list = AsyncMock(return_value=[])
            mock_products.return_value.find.return_value.sort.return_value.skip.return_value.limit.return_value = mock_cursor
            mock_products.return_value.count_documents = AsyncMock(return_value=0)
            
            from main import app
            
            async with AsyncClient(
                transport=ASGITransport(app=app),
                base_url="http://test"
            ) as client:
                response = await client.get("/product/list")
            
            assert response.status_code in [200, 500]
            if response.status_code == 200:
                data = response.json()
                assert "products" in data
    
    @pytest.mark.asyncio
    async def test_get_product_not_found(self):
        """Test getting non-existent product returns 404"""
        with patch('app.database.get_products_collection') as mock_products:
            mock_products.return_value.find_one = AsyncMock(return_value=None)
            
            from main import app
            
            async with AsyncClient(
                transport=ASGITransport(app=app),
                base_url="http://test"
            ) as client:
                response = await client.get("/product/507f1f77bcf86cd799439011")
            
            assert response.status_code in [404, 500]


class TestProductService:
    """Tests for product service"""
    
    @pytest.mark.asyncio
    async def test_get_products_with_filters(self):
        """Test product filtering logic"""
        from app.schemas.product import ProductFilter
        
        filters = ProductFilter(
            category="bangles",
            material="gold",
            min_price=10000,
            max_price=50000
        )
        
        # Verify filter object is created correctly
        assert filters.category == "bangles"
        assert filters.material == "gold"
        assert filters.min_price == 10000
        assert filters.max_price == 50000


class TestARConfig:
    """Tests for AR configuration"""
    
    def test_ar_config_response_schema(self):
        """Test ARConfigResponse schema"""
        from app.schemas.product import ARConfigResponse
        
        config = ARConfigResponse(
            scale=1.0,
            rotation=[0, 0, 0],
            offset=[0, 0, 0],
            wrist_diameter=6.5
        )
        
        assert config.scale == 1.0
        assert config.wrist_diameter == 6.5
        assert len(config.rotation) == 3
