from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from app.models.application import Application, ProcessingStatus
from app.models.job import Job
import logging

logger = logging.getLogger(__name__)

async def create_application(
    db: AsyncSession,
    job_id: int,
    cv_file_path: str,
    original_filename: str
) -> Application:
    """Create new CV application"""
    
    # Verify job exists
    result = await db.execute(select(Job).where(Job.id == job_id))
    job = result.scalar_one_or_none()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    # Create application
    db_application = Application(
        job_id=job_id,
        cv_file_path=cv_file_path,
        original_filename=original_filename,
        status=ProcessingStatus.PENDING
    )
    
    db.add(db_application)
    await db.commit()
    await db.refresh(db_application)
    
    logger.info(f"✅ Application created: {db_application.id} for job {job_id}")
    return db_application

async def get_application_by_id(
    db: AsyncSession,
    application_id: int
) -> Application | None:
    """Get application by ID"""
    result = await db.execute(
        select(Application).where(Application.id == application_id)
    )
    return result.scalar_one_or_none()

async def get_job_applications(
    db: AsyncSession,
    job_id: int,
    user_id: int
) -> list[Application]:
    """Get all applications for a job (with ownership check)"""
    
    # Verify job ownership
    result = await db.execute(
        select(Job).where(Job.id == job_id, Job.created_by == user_id)
    )
    job = result.scalar_one_or_none()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    # Get applications
    result = await db.execute(
        select(Application)
        .where(Application.job_id == job_id)
        .order_by(Application.match_score.desc().nulls_last())
    )
    
    return result.scalars().all()

async def delete_application(
    db: AsyncSession,
    application_id: int,
    user_id: int
) -> bool:
    """Delete application (with ownership check)"""
    
    # Get application with job
    result = await db.execute(
        select(Application)
        .join(Job)
        .where(
            Application.id == application_id,
            Job.created_by == user_id
        )
    )
    application = result.scalar_one_or_none()
    
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    
    await db.delete(application)
    await db.commit()
    
    logger.info(f"🗑️ Application deleted: {application_id}")
    return True
