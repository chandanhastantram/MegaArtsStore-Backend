"""
Tests for Payment Routes
"""

import pytest
from httpx import AsyncClient
from unittest.mock import patch, MagicMock


class TestPaymentRoutes:
    """Test payment endpoints"""
    
    @pytest.mark.asyncio
    async def test_create_payment_requires_auth(self, client: AsyncClient):
        """Test that creating payment requires authentication"""
        response = await client.post("/payment/create", json={"order_id": "ORD-12345678"})
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_create_payment_order_not_found(self, client: AsyncClient, auth_headers: dict):
        """Test payment creation with non-existent order"""
        response = await client.post(
            "/payment/create",
            json={"order_id": "ORD-INVALID"},
            headers=auth_headers
        )
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_verify_payment_invalid_signature(self, client: AsyncClient, auth_headers: dict):
        """Test payment verification with invalid signature"""
        response = await client.post(
            "/payment/verify",
            json={
                "order_id": "ORD-12345678",
                "razorpay_payment_id": "pay_123",
                "razorpay_order_id": "order_123",
                "razorpay_signature": "invalid_signature"
            },
            headers=auth_headers
        )
        assert response.status_code == 400
    
    @pytest.mark.asyncio
    async def test_payment_webhook(self, client: AsyncClient):
        """Test Razorpay webhook handler"""
        payload = {
            "event": "payment.captured",
            "payload": {
                "payment": {
                    "entity": {
                        "id": "pay_123",
                        "notes": {"order_id": "ORD-12345678"}
                    }
                }
            }
        }
        response = await client.post("/payment/webhook", json=payload)
        assert response.status_code == 200
        assert response.json()["status"] == "ok"
    
    @pytest.mark.asyncio
    async def test_refund_requires_admin(self, client: AsyncClient, auth_headers: dict):
        """Test that refund requires admin role"""
        response = await client.post(
            "/payment/refund",
            json={"order_id": "ORD-12345678"},
            headers=auth_headers  # Regular user, not admin
        )
        assert response.status_code == 403
    
    @pytest.mark.asyncio
    async def test_get_payment_status(self, client: AsyncClient, auth_headers: dict):
        """Test getting payment status"""
        # This would need an order to exist
        response = await client.get(
            "/payment/status/ORD-12345678",
            headers=auth_headers
        )
        # Either 404 (order not found) or 200
        assert response.status_code in [200, 404]
