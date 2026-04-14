from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime

class UserBase(BaseModel):
    """Base User Schema"""
    username: str
    email: EmailStr
    full_name: str | None = None

class UserCreate(UserBase):
    """User Creation Schema"""
    password: str

class UserResponse(UserBase):
    """User Response Schema"""
    id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class UserInDB(UserBase):
    """User in Database (with hashed password)"""
    id: int
    hashed_password: str
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
