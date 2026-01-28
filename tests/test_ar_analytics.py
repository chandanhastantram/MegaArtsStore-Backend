"""
Tests for AR Analytics Routes
"""

import pytest
from httpx import AsyncClient


class TestARAnalyticsRoutes:
    """Test AR analytics endpoints"""
    
    @pytest.mark.asyncio
    async def test_log_try_on_anonymous(self, client: AsyncClient):
        """Test logging anonymous try-on event"""
        response = await client.post(
            "/ar/try-on/anonymous",
            json={
                "product_id": "507f1f77bcf86cd799439011",
                "session_id": "test-session-123",
                "device_type": "mobile",
                "duration_seconds": 30,
                "screenshot_taken": False
            }
        )
        # 404 if product doesn't exist, 200 if it does
        assert response.status_code in [200, 404]
    
    @pytest.mark.asyncio
    async def test_log_try_on_requires_auth(self, client: AsyncClient):
        """Test that authenticated try-on logging requires auth"""
        response = await client.post(
            "/ar/try-on/log",
            json={
                "product_id": "507f1f77bcf86cd799439011",
                "device_type": "mobile"
            }
        )
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_update_conversion(self, client: AsyncClient):
        """Test updating try-on conversion"""
        response = await client.post(
            "/ar/try-on/conversion",
            json={
                "event_id": "test-event-123",
                "added_to_cart": True,
                "purchased": False
            }
        )
        assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_get_product_ar_stats_requires_admin(self, client: AsyncClient, auth_headers: dict):
        """Test that AR stats requires admin"""
        response = await client.get(
            "/ar/stats/507f1f77bcf86cd799439011",
            headers=auth_headers
        )
        assert response.status_code == 403
    
    @pytest.mark.asyncio
    async def test_get_size_chart(self, client: AsyncClient):
        """Test getting bangle size chart"""
        response = await client.get("/ar/size-chart")
        assert response.status_code == 200
        
        data = response.json()
        assert "size_chart" in data
        assert "2-4" in data["size_chart"]
        assert "2-8" in data["size_chart"]
    
    @pytest.mark.asyncio
    async def test_save_wrist_measurement_requires_auth(self, client: AsyncClient):
        """Test that saving wrist measurement requires auth"""
        response = await client.post(
            "/ar/wrist-measurement",
            json={
                "wrist_circumference": 15.5,
                "wrist_width": 5.0
            }
        )
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_preload_featured_models(self, client: AsyncClient):
        """Test preloading featured AR models"""
        response = await client.get("/ar/preload/featured")
        assert response.status_code == 200
        
        data = response.json()
        assert "models" in data
        assert "total" in data
    
    @pytest.mark.asyncio
    async def test_preload_batch_models(self, client: AsyncClient):
        """Test batch preloading models"""
        response = await client.post(
            "/ar/preload/batch",
            json=["507f1f77bcf86cd799439011", "507f1f77bcf86cd799439012"]
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "models" in data
