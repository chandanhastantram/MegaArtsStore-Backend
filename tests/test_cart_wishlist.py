"""
Tests for Cart and Wishlist Routes
"""

import pytest
from httpx import AsyncClient


class TestCartRoutes:
    """Test cart endpoints"""
    
    @pytest.mark.asyncio
    async def test_get_cart_requires_auth(self, client: AsyncClient):
        """Test that getting cart requires authentication"""
        response = await client.get("/cart/")
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_get_cart(self, client: AsyncClient, auth_headers: dict):
        """Test getting user's cart"""
        response = await client.get("/cart/", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "items" in data
        assert "subtotal" in data
        assert "item_count" in data
    
    @pytest.mark.asyncio
    async def test_add_to_cart_product_not_found(self, client: AsyncClient, auth_headers: dict):
        """Test adding non-existent product to cart"""
        response = await client.post(
            "/cart/add",
            json={
                "product_id": "507f1f77bcf86cd799439099",
                "size": "2-6",
                "quantity": 1
            },
            headers=auth_headers
        )
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_update_cart_item_not_found(self, client: AsyncClient, auth_headers: dict):
        """Test updating non-existent cart item"""
        response = await client.put(
            "/cart/update/507f1f77bcf86cd799439099/2-6",
            json={"quantity": 2},
            headers=auth_headers
        )
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_remove_from_cart(self, client: AsyncClient, auth_headers: dict):
        """Test removing item from cart"""
        response = await client.delete(
            "/cart/remove/507f1f77bcf86cd799439099/2-6",
            headers=auth_headers
        )
        assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_clear_cart(self, client: AsyncClient, auth_headers: dict):
        """Test clearing cart"""
        response = await client.delete("/cart/clear", headers=auth_headers)
        assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_get_cart_count(self, client: AsyncClient, auth_headers: dict):
        """Test getting cart count"""
        response = await client.get("/cart/count", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "count" in data


class TestWishlistRoutes:
    """Test wishlist endpoints"""
    
    @pytest.mark.asyncio
    async def test_get_wishlist_requires_auth(self, client: AsyncClient):
        """Test that getting wishlist requires authentication"""
        response = await client.get("/wishlist/")
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_get_wishlist(self, client: AsyncClient, auth_headers: dict):
        """Test getting user's wishlist"""
        response = await client.get("/wishlist/", headers=auth_headers)
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    @pytest.mark.asyncio
    async def test_add_to_wishlist_product_not_found(self, client: AsyncClient, auth_headers: dict):
        """Test adding non-existent product to wishlist"""
        response = await client.post(
            "/wishlist/add/507f1f77bcf86cd799439099",
            headers=auth_headers
        )
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_remove_from_wishlist(self, client: AsyncClient, auth_headers: dict):
        """Test removing from wishlist"""
        response = await client.delete(
            "/wishlist/remove/507f1f77bcf86cd799439099",
            headers=auth_headers
        )
        assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_clear_wishlist(self, client: AsyncClient, auth_headers: dict):
        """Test clearing wishlist"""
        response = await client.delete("/wishlist/clear", headers=auth_headers)
        assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_check_in_wishlist(self, client: AsyncClient, auth_headers: dict):
        """Test checking if product is in wishlist"""
        response = await client.get(
            "/wishlist/check/507f1f77bcf86cd799439099",
            headers=auth_headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "in_wishlist" in data
