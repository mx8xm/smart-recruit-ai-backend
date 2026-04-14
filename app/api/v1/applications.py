from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.database import get_db
from app.schemas.application import ApplicationResponse, ApplicationDetail, BulkUploadResponse
from app.services.cv_service import (
    create_application,
    get_application_by_id,
    get_job_applications,
    delete_application
)
from app.services.job_service import get_job_by_id
from app.utils.file_handler import save_upload_file
from app.api.deps import get_current_active_user
from app.models.user import User
from app.core.config import get_settings
import logging

router = APIRouter()
logger = logging.getLogger(__name__)
settings = get_settings()

@router.post("/{job_id}/upload", response_model=BulkUploadResponse)
async def upload_cvs(
    job_id: int,
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Upload multiple CV files (PDF/DOCX) for a job
    
    - **job_id**: Job posting ID
    - **files**: List of CV files (max 1000 files, max 10MB each)
    
    Files are saved immediately and processed in background
    """
    # Verify job ownership
    job = await get_job_by_id(db, job_id, current_user.id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    # Validate file count
    if len(files) > settings.MAX_FILES_PER_UPLOAD:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Too many files. Max: {settings.MAX_FILES_PER_UPLOAD}"
        )
    
    uploaded_count = 0
    failed_count = 0
    failed_files = []
    from app.utils.background_tasks import process_cv_application
    
    for file in files:
        try:
            # Save file to disk
            file_path, original_filename = await save_upload_file(file, job_id)
            
            # Create application record
            application = await create_application(
                db, job_id, file_path, original_filename
            )
            
            # Schedule background processing
            background_tasks.add_task(
                process_cv_application,
                application.id
            )
            
            uploaded_count += 1
            logger.info(f"✅ Uploaded: {original_filename}")
            
        except Exception as e:
            failed_count += 1
            failed_files.append(file.filename)
            logger.error(f"❌ Failed to upload {file.filename}: {e}")
    
    return BulkUploadResponse(
        total_files=len(files),
        uploaded=uploaded_count,
        failed=failed_count,
        failed_files=failed_files,
        message=f"Successfully uploaded {uploaded_count}/{len(files)} files. Processing started in background."
    )

@router.get("/{job_id}/applications", response_model=List[ApplicationResponse])
async def list_job_applications(
    job_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all applications for a job (sorted by match score)
    """
    applications = await get_job_applications(db, job_id, current_user.id)
    return applications

@router.get("/application/{application_id}", response_model=ApplicationDetail)
async def get_application_details(
    application_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get detailed application information (including full CV text)
    """
    application = await get_application_by_id(db, application_id)
    
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    
    # Verify ownership through job
    job = await get_job_by_id(db, application.job_id, current_user.id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    return application

@router.delete("/application/{application_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_application_record(
    application_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete an application record
    """
    await delete_application(db, application_id, current_user.id)
    return None
