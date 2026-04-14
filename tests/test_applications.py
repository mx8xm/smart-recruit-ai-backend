"""
CV Application Tests
Test CV upload, processing, and retrieval
"""

import pytest
from httpx import AsyncClient
from io import BytesIO

# ==========================================
# Helper Functions
# ==========================================

def create_fake_pdf():
    """إنشاء ملف PDF وهمي للاختبار"""
    return BytesIO(b"%PDF-1.4\nFake PDF content for testing")

def create_fake_docx():
    """إنشاء ملف DOCX وهمي للاختبار"""
    return BytesIO(b"PK fake DOCX content")


# ==========================================
# Upload CV Tests
# ==========================================

@pytest.mark.asyncio
async def test_upload_single_cv_success(authenticated_client):
    """
    Test: رفع سيرة ذاتية واحدة بنجاح
    """
    client, _ = authenticated_client
    
    # إنشاء وظيفة
    job_response = await client.post(
        "/api/v1/jobs/",
        json={"title": "Test Job", "description": "Test Description"}
    )
    job_id = job_response.json()["id"]
    
    # رفع سيرة ذاتية
    files = {
        "files": ("test_cv.pdf", create_fake_pdf(), "application/pdf")
    }
    
    response = await client.post(
        f"/api/v1/applications/{job_id}/upload",
        files=files
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["uploaded"] == 1
    assert data["failed"] == 0


@pytest.mark.asyncio
async def test_upload_multiple_cvs(authenticated_client):
    """
    Test: رفع عدة سير ذاتية
    """
    client, _ = authenticated_client
    
    # إنشاء وظيفة
    job_response = await client.post(
        "/api/v1/jobs/",
        json={"title": "Test Job", "description": "Test Description"}
    )
    job_id = job_response.json()["id"]
    
    # رفع 3 سير ذاتية
    files = [
        ("files", ("cv1.pdf", create_fake_pdf(), "application/pdf")),
        ("files", ("cv2.pdf", create_fake_pdf(), "application/pdf")),
        ("files", ("cv3.docx", create_fake_docx(), "application/vnd.openxmlformats-officedocument.wordprocessingml.document"))
    ]
    
    response = await client.post(
        f"/api/v1/applications/{job_id}/upload",
        files=files
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["total_files"] == 3
    assert data["uploaded"] >= 1  # على الأقل واحد نجح


@pytest.mark.asyncio
async def test_upload_cv_invalid_extension(authenticated_client):
    """
    Test: فشل رفع ملف بامتداد غير مسموح
    """
    client, _ = authenticated_client
    
    job_response = await client.post(
        "/api/v1/jobs/",
        json={"title": "Test Job", "description": "Test"}
    )
    job_id = job_response.json()["id"]
    
    # محاولة رفع ملف .txt (غير مسموح)
    files = {
        "files": ("test.txt", BytesIO(b"text file"), "text/plain")
    }
    
    response = await client.post(
        f"/api/v1/applications/{job_id}/upload",
        files=files
    )
    
    # قد يكون 400 أو نجاح مع failed=1
    data = response.json()
    assert data["failed"] >= 1 or response.status_code == 400


@pytest.mark.asyncio
async def test_upload_cv_job_not_found(authenticated_client):
    """
    Test: فشل رفع سيرة ذاتية لوظيفة غير موجودة
    """
    client, _ = authenticated_client
    
    files = {
        "files": ("test.pdf", create_fake_pdf(), "application/pdf")
    }
    
    response = await client.post(
        "/api/v1/applications/99999/upload",
        files=files
    )
    
    assert response.status_code == 404


# ==========================================
# List Applications Tests
# ==========================================

@pytest.mark.asyncio
async def test_list_applications_empty(authenticated_client):
    """
    Test: قائمة فارغة عند عدم رفع سير ذاتية
    """
    client, _ = authenticated_client
    
    job_response = await client.post(
        "/api/v1/jobs/",
        json={"title": "Test", "description": "Test"}
    )
    job_id = job_response.json()["id"]
    
    response = await client.get(f"/api/v1/applications/{job_id}/applications")
    
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_list_applications_with_data(authenticated_client):
    """
    Test: عرض السير الذاتية المرفوعة
    """
    client, _ = authenticated_client
    
    # إنشاء وظيفة
    job_response = await client.post(
        "/api/v1/jobs/",
        json={"title": "Test", "description": "Test"}
    )
    job_id = job_response.json()["id"]
    
    # رفع سيرتين ذاتيتين
    files = [
        ("files", ("cv1.pdf", create_fake_pdf(), "application/pdf")),
        ("files", ("cv2.pdf", create_fake_pdf(), "application/pdf"))
    ]
    
    await client.post(f"/api/v1/applications/{job_id}/upload", files=files)
    
    # الحصول على القائمة
    response = await client.get(f"/api/v1/applications/{job_id}/applications")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1  # على الأقل واحد نجح


# ==========================================
# Get Application Details Tests
# ==========================================

@pytest.mark.asyncio
async def test_get_application_details(authenticated_client):
    """
    Test: الحصول على تفاصيل سيرة ذاتية محددة
    """
    client, _ = authenticated_client
    
    # إنشاء وظيفة ورفع سيرة ذاتية
    job_response = await client.post(
        "/api/v1/jobs/",
        json={"title": "Test", "description": "Test"}
    )
    job_id = job_response.json()["id"]
    
    files = {
        "files": ("test.pdf", create_fake_pdf(), "application/pdf")
    }
    await client.post(f"/api/v1/applications/{job_id}/upload", files=files)
    
    # الحصول على قائمة السير الذاتية
    list_response = await client.get(f"/api/v1/applications/{job_id}/applications")
    applications = list_response.json()
    
    if len(applications) > 0:
        app_id = applications[0]["id"]
        
        # الحصول على التفاصيل
        response = await client.get(f"/api/v1/applications/application/{app_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "original_filename" in data


# ==========================================
# Delete Application Tests
# ==========================================

@pytest.mark.asyncio
async def test_delete_application(authenticated_client):
    """
    Test: حذف سيرة ذاتية
    """
    client, _ = authenticated_client
    
    # إنشاء وظيفة ورفع سيرة ذاتية
    job_response = await client.post(
        "/api/v1/jobs/",
        json={"title": "Test", "description": "Test"}
    )
    job_id = job_response.json()["id"]
    
    files = {
        "files": ("test.pdf", create_fake_pdf(), "application/pdf")
    }
    await client.post(f"/api/v1/applications/{job_id}/upload", files=files)
    
    # الحصول على ID
    list_response = await client.get(f"/api/v1/applications/{job_id}/applications")
    applications = list_response.json()
    
    if len(applications) > 0:
        app_id = applications[0]["id"]
        
        # حذف السيرة الذاتية
        response = await client.delete(f"/api/v1/applications/application/{app_id}")
        
        assert response.status_code == 204
