import pytest
from httpx import AsyncClient
from app.main import app


@pytest.mark.asyncio
async def test_root_endpoint():
    """Test root endpoint"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data


@pytest.mark.asyncio
async def test_health_check():
    """Test health check endpoint"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


@pytest.mark.asyncio
async def test_register_user():
    """Test user registration"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post(
            "/api/v1/auth/register",
            params={
                "username": "testuser",
                "email": "test@example.com",
                "password": "testpassword123"
            }
        )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "token" in data["data"]


@pytest.mark.asyncio
async def test_login():
    """Test user login"""
    # First register a user
    async with AsyncClient(app=app, base_url="http://test") as ac:
        await ac.post(
            "/api/v1/auth/register",
            params={
                "username": "logintest",
                "email": "logintest@example.com",
                "password": "testpass123"
            }
        )

        # Then login
        response = await ac.post(
            "/api/v1/auth/login",
            json={
                "username": "logintest",
                "password": "testpass123"
            }
        )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "token" in data["data"]

