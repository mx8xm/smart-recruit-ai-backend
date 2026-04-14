from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import List, Optional, TYPE_CHECKING

# استخدام TYPE_CHECKING لتجنب Circular Import
if TYPE_CHECKING:
    from app.schemas.application import ApplicationResponse

class JobBase(BaseModel):
    """Base Job Schema"""
    title: str = Field(..., min_length=3, max_length=200)
    description: str = Field(..., min_length=10)

class JobCreate(JobBase):
    """Job Creation Schema"""
    pass

class JobUpdate(BaseModel):
    """Job Update Schema"""
    title: Optional[str] = Field(None, min_length=3, max_length=200)
    description: Optional[str] = Field(None, min_length=10)

class JobResponse(JobBase):
    """Job Response Schema"""
    id: int
    created_by: int
    created_at: datetime
    application_count: int = 0
    
    model_config = ConfigDict(from_attributes=True)

class JobDetail(JobResponse):
    """Job with Applications - استخدام Forward Reference"""
    applications: List["ApplicationResponse"] = Field(default_factory=list)
    
    model_config = ConfigDict(from_attributes=True)
