import logging
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.application import Application, ProcessingStatus
from app.models.job import Job
from app.ai.text_extractor import extract_text_from_cv, extract_raw_text_pymupdf
from app.ai.name_extractor import SmartCVExtractor
from app.ai.cv_scorer import calculate_match_score
from app.database import AsyncSessionLocal

logger = logging.getLogger(__name__)

# تهيئة المستخرج بشكل كسول (Lazy Initialization)
cv_extractor = None


async def _process_cv_application(application_id: int, db: AsyncSession):
    global cv_extractor
    """
    Background task to process a single CV application
    
    Steps:
    1. Extract text from CV file
    2. Extract candidate name
    3. Calculate match score against job description
    4. Update application record
    
    Args:
        application_id: ID of the application to process
        db: Database session
    """
    logger.info(f"🚀 Starting processing for Application ID: {application_id}")
    
    try:
        # Fetch application with job details
        result = await db.execute(
            select(Application).where(Application.id == application_id)
        )
        application = result.scalar_one_or_none()
        
        if not application:
            logger.error(f"❌ Application {application_id} not found")
            return
        
        # Update status to PROCESSING
        application.status = ProcessingStatus.PROCESSING
        await db.commit()
        
        # Fetch job description
        result = await db.execute(
            select(Job).where(Job.id == application.job_id)
        )
        job = result.scalar_one_or_none()
        
        if not job:
            raise Exception("Job not found")
        
        # Step 1: Accurate Extraction of Structured Text with Docling
        logger.info(f"📄 Extracting structured match text (Docling): {application.original_filename}")
        extracted_text = extract_text_from_cv(application.cv_file_path)
        
        if not extracted_text or len(extracted_text.strip()) < 50:
            raise Exception("Extracted text from Docling is too short or empty")

        # Step 2: Fast Extraction of Candidate Name & Email with PyMuPDF
        logger.info(f"⚡ Extracting candidate personal details (Hybrid)...")
        if cv_extractor is None:
            cv_extractor = SmartCVExtractor()
            
        pymupdf_raw_text = extract_raw_text_pymupdf(application.cv_file_path)
        
        # Combine texts: PyMuPDF first for clear Name/Email, then Docling for structure
        combined_text = f"{pymupdf_raw_text}\n\n{extracted_text}"
        
        extracted_info = cv_extractor.extract_info(combined_text)
        candidate_name = extracted_info.get("name", "Unknown")
        
        # Step 3: Calculate match score using high-quality Markdown text
        logger.info(f"🎯 Calculating match score...")
        match_score = calculate_match_score(job.description, extracted_text)
        
        # Update application with results
        application.extracted_text = extracted_text
        application.candidate_name = candidate_name
        application.match_score = match_score
        application.status = ProcessingStatus.COMPLETED
        application.processed_at = datetime.utcnow()
        
        await db.commit()
        
        logger.info(
            f"✅ Processing completed for Application {application_id}\n"
            f"   Candidate: {candidate_name}\n"
            f"   Score: {match_score * 100:.2f}%"
        )
        
    except Exception as e:
        logger.error(f"❌ Processing failed for Application {application_id}: {e}")
        
        # Update status to FAILED
        try:
            result = await db.execute(
                select(Application).where(Application.id == application_id)
            )
            application = result.scalar_one_or_none()
            
            if application:
                application.status = ProcessingStatus.FAILED
                application.error_message = str(e)
                application.processed_at = datetime.utcnow()
                await db.commit()
        except Exception as db_error:
            logger.error(f"Failed to update error status: {db_error}")


async def process_cv_application(application_id: int):
    async with AsyncSessionLocal() as db:
        await _process_cv_application(application_id, db)
