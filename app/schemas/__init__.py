from app.schemas.auth import Token, TokenData, UserLogin, UserRegister
from app.schemas.user import UserBase, UserCreate, UserResponse, UserInDB
from app.schemas.application import (
    ApplicationBase,
    ApplicationCreate,
    ApplicationResponse,
    ApplicationDetail,
    BulkUploadResponse
)
from app.schemas.job import JobBase, JobCreate, JobUpdate, JobResponse, JobDetail

# ✅ حل مشكلة Forward Reference
JobDetail.model_rebuild()

__all__ = [
    # Auth
    "Token",
    "TokenData",
    "UserLogin",
    "UserRegister",
    # User
    "UserBase",
    "UserCreate",
    "UserResponse",
    "UserInDB",
    # Job
    "JobBase",
    "JobCreate",
    "JobUpdate",
    "JobResponse",
    "JobDetail",
    # Application
    "ApplicationBase",
    "ApplicationCreate",
    "ApplicationResponse",
    "ApplicationDetail",
    "BulkUploadResponse",
]
