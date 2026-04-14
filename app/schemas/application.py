from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional
from app.models.application import ProcessingStatus

class ApplicationBase(BaseModel):
    """Base Application Schema"""
    job_id: int

class ApplicationCreate(ApplicationBase):
    """Application Creation Schema"""
    pass

class ApplicationResponse(BaseModel):
    """Application Response Schema"""
    id: int
    job_id: int
    original_filename: str
    candidate_name: Optional[str] = None
    match_score: Optional[float] = None
    status: ProcessingStatus
    error_message: Optional[str] = None
    created_at: datetime
    processed_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)

class ApplicationDetail(ApplicationResponse):
    """Application with Full Text"""
    extracted_text: Optional[str] = None
    cv_file_path: str
    
    model_config = ConfigDict(from_attributes=True)

class BulkUploadResponse(BaseModel):
    """Bulk Upload Response"""
    total_files: int
    uploaded: int
    failed: int
    failed_files: list[str] = []
    message: str
