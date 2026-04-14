from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.database import get_db
from app.schemas.job import JobCreate, JobUpdate, JobResponse, JobDetail
from app.services.job_service import (
    create_job,
    get_user_jobs,
    get_job_by_id,
    get_job_with_applications,
    update_job,
    delete_job,
    get_job_statistics
)
from app.api.deps import get_current_active_user
from app.models.user import User

router = APIRouter()

@router.post("/", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
async def create_new_job(
    job_data: JobCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create new job posting
    
    - **title**: Job title (e.g., "Senior Python Developer")
    - **description**: Full job description for AI matching
    """
    job = await create_job(db, job_data, current_user.id)
    return job

@router.get("/", response_model=List[JobResponse])
async def list_my_jobs(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all jobs created by current user
    """
    jobs = await get_user_jobs(db, current_user.id)
    
    # Add application count to each job
    for job in jobs:
        job.application_count = len(job.applications) if job.applications else 0
    
    return jobs

@router.get("/{job_id}", response_model=JobDetail)
async def get_job_details(
    job_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get job details with all applications (sorted by match score)
    """
    job = await get_job_with_applications(db, job_id, current_user.id)
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    # Add application count
    job.application_count = len(job.applications) if job.applications else 0
    
    return job

@router.put("/{job_id}", response_model=JobResponse)
async def update_job_details(
    job_id: int,
    job_data: JobUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update job title or description
    """
    updated_job = await update_job(db, job_id, current_user.id, job_data)
    updated_job.application_count = len(updated_job.applications) if updated_job.applications else 0
    return updated_job

@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_job_posting(
    job_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete job posting (and all associated applications)
    """
    await delete_job(db, job_id, current_user.id)
    return None

@router.get("/{job_id}/statistics")
async def get_job_stats(
    job_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get job statistics (total applications, status breakdown)
    """
    stats = await get_job_statistics(db, job_id, current_user.id)
    return stats
