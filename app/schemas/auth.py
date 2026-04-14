from pydantic import BaseModel, EmailStr

class Token(BaseModel):
    """JWT Token Response"""
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    """Token Payload Data"""
    username: str | None = None

class UserLogin(BaseModel):
    """Login Request"""
    username: str
    password: str

class UserRegister(BaseModel):
    """Registration Request"""
    username: str
    email: EmailStr
    password: str
    full_name: str | None = None
