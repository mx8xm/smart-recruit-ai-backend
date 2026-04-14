from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import timedelta
from app.database import get_db
from app.schemas.auth import Token, UserRegister
from app.schemas.user import UserResponse, UserCreate
from app.services.auth_service import authenticate_user, create_user
from app.core.security import create_access_token
from app.core.config import get_settings
from app.api.deps import get_current_active_user
from app.models.user import User

router = APIRouter()
settings = get_settings()

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserRegister,
    db: AsyncSession = Depends(get_db)
):
    """
    Register new HR Admin user
    
    - **username**: Unique username (3-50 chars)
    - **email**: Valid email address
    - **password**: Strong password (min 8 chars)
    - **full_name**: Optional full name
    """
    user_create = UserCreate(
        username=user_data.username,
        email=user_data.email,
        password=user_data.password,
        full_name=user_data.full_name
    )
    
    new_user = await create_user(db, user_create)
    return new_user

@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """
    Login with username and password to get JWT access token
    
    - **username**: Your username
    - **password**: Your password
    
    Returns JWT token for authentication
    """
    user = await authenticate_user(db, form_data.username, form_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current logged-in user information
    """
    return current_user
