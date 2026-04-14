from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status
from app.models.job import Job
from app.models.application import Application
from app.schemas.job import JobCreate, JobUpdate
import logging

logger = logging.getLogger(__name__)


def _normalize_job_text(value: str | None) -> str | None:
    if value is None:
        return None
    return value.replace("\\r\\n", "\n").replace("\\n", "\n")

async def create_job(db: AsyncSession, job_data: JobCreate, user_id: int) -> Job:
    """Create new job posting"""
    db_job = Job(
        title=job_data.title,
        description=_normalize_job_text(job_data.description),
        created_by=user_id
    )
    
    db.add(db_job)
    await db.commit()
    await db.refresh(db_job)
    
    logger.info(f"✅ Job created: {job_data.title} (ID: {db_job.id})")
    return db_job

async def get_user_jobs(db: AsyncSession, user_id: int) -> list[Job]:
    """Get all jobs created by user"""
    result = await db.execute(
        select(Job)
        .options(selectinload(Job.applications))  # أضف هذا السطر هنا
        .where(Job.created_by == user_id)
        .order_by(Job.created_at.desc())
    )
    return result.scalars().all()

async def get_job_by_id(db: AsyncSession, job_id: int, user_id: int) -> Job | None:
    """Get job by ID (with ownership check)"""
    result = await db.execute(
        select(Job).where(Job.id == job_id, Job.created_by == user_id)
    )
    return result.scalar_one_or_none()

async def get_job_with_applications(
    db: AsyncSession, 
    job_id: int, 
    user_id: int
) -> Job | None:
    """Get job with all applications (sorted by score)"""
    result = await db.execute(
        select(Job)
        .options(selectinload(Job.applications))
        .where(Job.id == job_id, Job.created_by == user_id)
    )
    job = result.scalar_one_or_none()
    
    if job and job.applications:
        # Sort applications by match_score descending
        job.applications.sort(
            key=lambda x: x.match_score if x.match_score else 0,
            reverse=True
        )
    
    return job

async def update_job(
    db: AsyncSession,
    job_id: int,
    user_id: int,
    job_data: JobUpdate
) -> Job:
    """Update job details"""
    # نستخدم استعلاماً يتضمن selectinload لضمان جلب الطلبات (Applications)
    # هذا يمنع خطأ MissingGreenlet عند محاولة حساب application_count في الـ Router
    result = await db.execute(
        select(Job)
        .options(selectinload(Job.applications))
        .where(Job.id == job_id, Job.created_by == user_id)
    )
    job = result.scalar_one_or_none()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    # تحديث الحقول إذا كانت موجودة في الطلب
    if job_data.title is not None:
        job.title = job_data.title
    if job_data.description is not None:
        job.description = _normalize_job_text(job_data.description)
    
    await db.commit()
    
    # ملاحظة هامة: refresh قد تمسح البيانات المحملة مسبقاً في بعض الحالات
    # لذا نفضل إعادة التحميل بوضوح إذا واجهت مشاكل
    await db.refresh(job)
    
    # لإعادة تحميل الـ applications بعد الـ refresh لضمان وجودها
    await db.execute(
        select(Job).options(selectinload(Job.applications)).where(Job.id == job.id)
    )

    logger.info(f"✅ Job updated: {job.id}")
    return job

async def delete_job(db: AsyncSession, job_id: int, user_id: int) -> bool:
    """Delete job (and all applications)"""
    job = await get_job_by_id(db, job_id, user_id)
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    await db.delete(job)
    await db.commit()
    
    logger.info(f"🗑️ Job deleted: {job_id}")
    return True

async def get_job_statistics(db: AsyncSession, job_id: int, user_id: int) -> dict:
    """Get job statistics"""
    job = await get_job_by_id(db, job_id, user_id)
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    # Count applications by status
    result = await db.execute(
        select(
            func.count(Application.id).label('total'),
            func.count(Application.id).filter(Application.status == 'completed').label('completed'),
            func.count(Application.id).filter(Application.status == 'pending').label('pending'),
            func.count(Application.id).filter(Application.status == 'processing').label('processing'),
            func.count(Application.id).filter(Application.status == 'failed').label('failed')
        )
        .where(Application.job_id == job_id)
    )
    
    stats = result.first()
    
    return {
        "job_id": job_id,
        "total_applications": stats.total,
        "completed": stats.completed,
        "pending": stats.pending,
        "processing": stats.processing,
        "failed": stats.failed
    }
