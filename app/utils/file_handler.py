import os
import uuid
import aiofiles
from pathlib import Path
from fastapi import UploadFile, HTTPException
from app.core.config import get_settings
import logging

logger = logging.getLogger(__name__)
settings = get_settings()

def validate_file_extension(filename: str) -> bool:
    """Check if file extension is allowed"""
    ext = Path(filename).suffix.lower()
    return ext in settings.ALLOWED_EXTENSIONS

def validate_file_size(file_size: int) -> bool:
    """Check if file size is within limit"""
    return file_size <= settings.MAX_FILE_SIZE

def generate_unique_filename(original_filename: str) -> str:
    """Generate unique filename while preserving extension"""
    ext = Path(original_filename).suffix.lower()
    unique_name = f"{uuid.uuid4()}{ext}"
    return unique_name

async def save_upload_file(upload_file: UploadFile, job_id: int) -> tuple[str, str]:
    """
    Save uploaded CV file to disk
    
    Args:
        upload_file: The uploaded file
        job_id: ID of the job posting
        
    Returns:
        Tuple of (file_path, original_filename)
    """
    # Validate extension
    if not validate_file_extension(upload_file.filename):
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Allowed: {', '.join(settings.ALLOWED_EXTENSIONS)}"
        )
    
    # Create job-specific directory
    job_folder = Path(settings.UPLOAD_FOLDER) / "cvs" / str(job_id)
    job_folder.mkdir(parents=True, exist_ok=True)
    
    # Generate unique filename
    unique_filename = generate_unique_filename(upload_file.filename)
    file_path = job_folder / unique_filename
    
    try:
        # Save file asynchronously
        async with aiofiles.open(file_path, 'wb') as f:
            content = await upload_file.read()
            
            # Validate size
            if not validate_file_size(len(content)):
                raise HTTPException(
                    status_code=400,
                    detail=f"File too large. Max size: {settings.MAX_FILE_SIZE / 1024 / 1024}MB"
                )
            
            await f.write(content)
        
        logger.info(f"✅ File saved: {file_path}")
        return str(file_path), upload_file.filename
        
    except Exception as e:
        logger.error(f"❌ Failed to save file: {e}")
        # Clean up partial file if exists
        if file_path.exists():
            file_path.unlink()
        raise HTTPException(status_code=500, detail="Failed to save file")

def delete_cv_file(file_path: str) -> bool:
    """Delete CV file from disk"""
    try:
        path = Path(file_path)
        if path.exists():
            path.unlink()
            logger.info(f"🗑️ File deleted: {file_path}")
            return True
        return False
    except Exception as e:
        logger.error(f"❌ Failed to delete file: {e}")
        return False

def get_file_size_mb(file_path: str) -> float:
    """Get file size in MB"""
    try:
        size_bytes = Path(file_path).stat().st_size
        return round(size_bytes / (1024 * 1024), 2)
    except:
        return 0.0
