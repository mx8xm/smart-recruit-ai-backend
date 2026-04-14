"""
Job Management Tests
Test job creation, listing, updating, and deletion
"""

import pytest
from httpx import AsyncClient

# ==========================================
# Create Job Tests
# ==========================================

@pytest.mark.asyncio
async def test_create_job_success(authenticated_client):
    """
    Test: إنشاء وظيفة جديدة بنجاح
    """
    client, _ = authenticated_client
    
    job_data = {
        "title": "Senior Python Developer",
        "description": "We need an experienced Python developer with FastAPI knowledge."
    }
    
    response = await client.post("/api/v1/jobs/", json=job_data)
    
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == job_data["title"]
    assert data["description"] == job_data["description"]
    assert "id" in data
    assert "created_at" in data


@pytest.mark.asyncio
async def test_create_job_unauthorized(client: AsyncClient):
    """
    Test: فشل إنشاء وظيفة بدون تسجيل دخول
    """
    response = await client.post(
        "/api/v1/jobs/",
        json={"title": "Test Job", "description": "Test"}
    )
    
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_job_invalid_data(authenticated_client):
    """
    Test: فشل إنشاء وظيفة ببيانات غير صالحة
    """
    client, _ = authenticated_client
    
    # عنوان قصير جداً
    response = await client.post(
        "/api/v1/jobs/",
        json={"title": "AB", "description": "Test description"}
    )
    
    assert response.status_code == 422


# ==========================================
# List Jobs Tests
# ==========================================

@pytest.mark.asyncio
async def test_list_jobs_empty(authenticated_client):
    """
    Test: قائمة فارغة عند عدم وجود وظائف
    """
    client, _ = authenticated_client
    
    response = await client.get("/api/v1/jobs/")
    
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_list_jobs_with_data(authenticated_client):
    """
    Test: عرض الوظائف المنشأة
    """
    client, _ = authenticated_client
    
    # إنشاء 3 وظائف
    for i in range(3):
        await client.post(
            "/api/v1/jobs/",
            json={
                "title": f"Job {i+1}",
                "description": f"Description {i+1}"
            }
        )
    
    # الحصول على القائمة
    response = await client.get("/api/v1/jobs/")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3


# ==========================================
# Get Job Details Tests
# ==========================================

@pytest.mark.asyncio
async def test_get_job_details_success(authenticated_client):
    """
    Test: الحصول على تفاصيل وظيفة محددة
    """
    client, _ = authenticated_client
    
    # إنشاء وظيفة
    create_response = await client.post(
        "/api/v1/jobs/",
        json={"title": "Test Job", "description": "Test Description"}
    )
    job_id = create_response.json()["id"]
    
    # الحصول على التفاصيل
    response = await client.get(f"/api/v1/jobs/{job_id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == job_id
    assert data["title"] == "Test Job"


@pytest.mark.asyncio
async def test_get_job_details_not_found(authenticated_client):
    """
    Test: فشل الحصول على وظيفة غير موجودة
    """
    client, _ = authenticated_client
    
    response = await client.get("/api/v1/jobs/99999")
    
    assert response.status_code == 404


# ==========================================
# Update Job Tests
# ==========================================

@pytest.mark.asyncio
async def test_update_job_success(authenticated_client):
    """
    Test: تحديث وظيفة بنجاح
    """
    client, _ = authenticated_client
    
    # إنشاء وظيفة
    create_response = await client.post(
        "/api/v1/jobs/",
        json={"title": "Original Title", "description": "Original Description"}
    )
    job_id = create_response.json()["id"]
    
    # تحديث الوظيفة
    response = await client.put(
        f"/api/v1/jobs/{job_id}",
        json={"title": "Updated Title"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"
    assert data["description"] == "Original Description"  # لم يتغير


# ==========================================
# Delete Job Tests
# ==========================================

@pytest.mark.asyncio
async def test_delete_job_success(authenticated_client):
    """
    Test: حذف وظيفة بنجاح
    """
    client, _ = authenticated_client
    
    # إنشاء وظيفة
    create_response = await client.post(
        "/api/v1/jobs/",
        json={"title": "To Delete", "description": "Will be deleted"}
    )
    job_id = create_response.json()["id"]
    
    # حذف الوظيفة
    response = await client.delete(f"/api/v1/jobs/{job_id}")
    
    assert response.status_code == 204
    
    # التحقق من الحذف
    get_response = await client.get(f"/api/v1/jobs/{job_id}")
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_delete_job_not_found(authenticated_client):
    """
    Test: فشل حذف وظيفة غير موجودة
    """
    client, _ = authenticated_client
    
    response = await client.delete("/api/v1/jobs/99999")
    
    assert response.status_code == 404


# ==========================================
# Job Statistics Tests
# ==========================================

@pytest.mark.asyncio
async def test_get_job_statistics(authenticated_client):
    """
    Test: الحصول على إحصائيات الوظيفة
    """
    client, _ = authenticated_client
    
    # إنشاء وظيفة
    create_response = await client.post(
        "/api/v1/jobs/",
        json={"title": "Stats Job", "description": "Test statistics"}
    )
    job_id = create_response.json()["id"]
    
    # الحصول على الإحصائيات
    response = await client.get(f"/api/v1/jobs/{job_id}/statistics")
    
    assert response.status_code == 200
    data = response.json()
    assert "total_applications" in data
    assert "completed" in data
    assert "pending" in data
