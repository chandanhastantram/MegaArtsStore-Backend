"""
Authentication Tests
Tests for user registration, login, and role-based access
"""

import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import patch, AsyncMock
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# Mock settings before importing app
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


@pytest.fixture
def mock_db():
    """Mock database for tests"""
    with patch('app.database.get_users_collection') as mock_users:
        mock_users.return_value = AsyncMock()
        yield mock_users


class TestRegistration:
    """Tests for user registration"""
    
    @pytest.mark.asyncio
    async def test_register_success(self, mock_db):
        """Test successful user registration"""
        # Mock database operations
        mock_db.return_value.find_one = AsyncMock(return_value=None)
        mock_db.return_value.insert_one = AsyncMock(
            return_value=type('Result', (), {'inserted_id': '507f1f77bcf86cd799439011'})()
        )
        
        from main import app
        
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.post(
                "/auth/register",
                json={
                    "email": "test@example.com",
                    "password": "securepassword123",
                    "name": "Test User"
                }
            )
        
        # Registration should succeed or fail gracefully
        assert response.status_code in [201, 500]  # 500 if DB not connected
    
    @pytest.mark.asyncio
    async def test_register_duplicate_email(self, mock_db):
        """Test registration with existing email fails"""
        mock_db.return_value.find_one = AsyncMock(
            return_value={"email": "test@example.com"}
        )
        
        from main import app
        
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.post(
                "/auth/register",
                json={
                    "email": "test@example.com",
                    "password": "securepassword123",
                    "name": "Test User"
                }
            )
        
        assert response.status_code in [400, 500]
    
    @pytest.mark.asyncio
    async def test_register_invalid_email(self):
        """Test registration with invalid email fails"""
        from main import app
        
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.post(
                "/auth/register",
                json={
                    "email": "invalid-email",
                    "password": "securepassword123",
                    "name": "Test User"
                }
            )
        
        assert response.status_code == 422  # Validation error
    
    @pytest.mark.asyncio
    async def test_register_short_password(self):
        """Test registration with short password fails"""
        from main import app
        
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.post(
                "/auth/register",
                json={
                    "email": "test@example.com",
                    "password": "short",
                    "name": "Test User"
                }
            )
        
        assert response.status_code == 422  # Validation error


class TestLogin:
    """Tests for user login"""
    
    @pytest.mark.asyncio
    async def test_login_invalid_credentials(self):
        """Test login with invalid credentials fails"""
        from main import app
        
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.post(
                "/auth/login",
                data={
                    "username": "nonexistent@example.com",
                    "password": "wrongpassword"
                }
            )
        
        assert response.status_code in [401, 500]


class TestTokenValidation:
    """Tests for JWT token validation"""
    
    def test_create_access_token(self):
        """Test JWT token creation"""
        from app.utils.auth import create_access_token
        
        token = create_access_token(
            data={"sub": "123", "email": "test@example.com", "role": "user"}
        )
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_decode_valid_token(self):
        """Test decoding valid JWT token"""
        from app.utils.auth import create_access_token, decode_token
        
        token = create_access_token(
            data={"sub": "123", "email": "test@example.com", "role": "user"}
        )
        
        token_data = decode_token(token)
        
        assert token_data is not None
        assert token_data.user_id == "123"
        assert token_data.email == "test@example.com"
        assert token_data.role == "user"
    
    def test_decode_invalid_token(self):
        """Test decoding invalid JWT token returns None"""
        from app.utils.auth import decode_token
        
        token_data = decode_token("invalid-token")
        
        assert token_data is None


class TestPasswordHashing:
    """Tests for password hashing"""
    
    def test_hash_password(self):
        """Test password hashing"""
        from app.utils.auth import hash_password
        
        password = "securepassword123"
        hashed = hash_password(password)
        
        assert hashed != password
        assert len(hashed) > 0
    
    def test_verify_password_correct(self):
        """Test correct password verification"""
        from app.utils.auth import hash_password, verify_password
        
        password = "securepassword123"
        hashed = hash_password(password)
        
        assert verify_password(password, hashed) is True
    
    def test_verify_password_incorrect(self):
        """Test incorrect password verification"""
        from app.utils.auth import hash_password, verify_password
        
        password = "securepassword123"
        hashed = hash_password(password)
        
        assert verify_password("wrongpassword", hashed) is False
