"""
Authentication Tests
Test user registration, login, and token validation
"""

import pytest
from httpx import AsyncClient

# ==========================================
# Registration Tests
# ==========================================

@pytest.mark.asyncio
async def test_register_success(client: AsyncClient):
    """
    Test: تسجيل مستخدم جديد بنجاح
    """
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "securepass123",
            "full_name": "New User"
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "newuser"
    assert data["email"] == "newuser@example.com"
    assert "password" not in data  # يجب عدم إرجاع كلمة المرور


@pytest.mark.asyncio
async def test_register_duplicate_username(client: AsyncClient):
    """
    Test: فشل التسجيل عند استخدام اسم مستخدم موجود
    """
    user_data = {
        "username": "testuser",
        "email": "test1@example.com",
        "password": "pass123"
    }
    
    # التسجيل الأول - ناجح
    await client.post("/api/v1/auth/register", json=user_data)
    
    # التسجيل الثاني بنفس الاسم - فاشل
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "username": "testuser",  # نفس الاسم
            "email": "test2@example.com",  # بريد مختلف
            "password": "pass123"
        }
    )
    
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"]


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient):
    """
    Test: فشل التسجيل عند استخدام بريد إلكتروني موجود
    """
    user_data = {
        "username": "user1",
        "email": "same@example.com",
        "password": "pass123"
    }
    
    await client.post("/api/v1/auth/register", json=user_data)
    
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "username": "user2",
            "email": "same@example.com",  # نفس البريد
            "password": "pass123"
        }
    )
    
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"]


@pytest.mark.asyncio
async def test_register_invalid_email(client: AsyncClient):
    """
    Test: فشل التسجيل عند إدخال بريد إلكتروني غير صالح
    """
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "username": "testuser",
            "email": "invalid-email",  # بريد غير صالح
            "password": "pass123"
        }
    )
    
    assert response.status_code == 422  # Validation error


# ==========================================
# Login Tests
# ==========================================

@pytest.mark.asyncio
async def test_login_success(client: AsyncClient):
    """
    Test: تسجيل دخول ناجح
    """
    # التسجيل أولاً
    await client.post(
        "/api/v1/auth/register",
        json={
            "username": "loginuser",
            "email": "login@example.com",
            "password": "loginpass123"
        }
    )
    
    # تسجيل الدخول
    response = await client.post(
        "/api/v1/auth/login",
        data={
            "username": "loginuser",
            "password": "loginpass123"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient):
    """
    Test: فشل تسجيل الدخول عند كلمة مرور خاطئة
    """
    await client.post(
        "/api/v1/auth/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "correctpass"
        }
    )
    
    response = await client.post(
        "/api/v1/auth/login",
        data={
            "username": "testuser",
            "password": "wrongpass"  # كلمة مرور خاطئة
        }
    )
    
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_login_nonexistent_user(client: AsyncClient):
    """
    Test: فشل تسجيل الدخول لمستخدم غير موجود
    """
    response = await client.post(
        "/api/v1/auth/login",
        data={
            "username": "nonexistent",
            "password": "anypass"
        }
    )
    
    assert response.status_code == 401


# ==========================================
# Get Current User Tests
# ==========================================

@pytest.mark.asyncio
async def test_get_current_user(authenticated_client):
    """
    Test: الحصول على معلومات المستخدم الحالي
    """
    client, user_data = authenticated_client
    
    response = await client.get("/api/v1/auth/me")
    
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == user_data["username"]
    assert data["email"] == user_data["email"]


@pytest.mark.asyncio
async def test_get_current_user_no_token(client: AsyncClient):
    """
    Test: فشل الحصول على المعلومات بدون token
    """
    response = await client.get("/api/v1/auth/me")
    
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user_invalid_token(client: AsyncClient):
    """
    Test: فشل الحصول على المعلومات مع token غير صالح
    """
    client.headers.update({"Authorization": "Bearer invalid_token_here"})
    
    response = await client.get("/api/v1/auth/me")
    
    assert response.status_code == 401
