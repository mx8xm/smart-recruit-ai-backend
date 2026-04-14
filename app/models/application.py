from sqlalchemy import Column, Integer, String, Text, Float, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.database import Base

class ProcessingStatus(str, enum.Enum):
    """CV Processing Status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class Application(Base):
    """CV Application Model"""
    __tablename__ = "applications"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign Keys
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    
    # File Information
    cv_file_path = Column(String(500), nullable=False)
    original_filename = Column(String(255), nullable=False)
    
    # AI Results
    candidate_name = Column(String(200), nullable=True)
    match_score = Column(Float, nullable=True)  # 0.0 to 1.0
    extracted_text = Column(Text, nullable=True)
    
    # Processing Status
    status = Column(
        Enum(ProcessingStatus),
        default=ProcessingStatus.PENDING,
        nullable=False,
        index=True
    )
    error_message = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    processed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    job = relationship("Job", back_populates="applications")
    
    def __repr__(self):
        return f"<Application {self.original_filename} - {self.status}>"
