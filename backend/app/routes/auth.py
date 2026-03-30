"""
Authentication Routes
"""
from datetime import timedelta
from typing import Annotated, Optional
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.services.auth_service import AuthService
from app.models.db_models import User
from app.database import get_db
from app.schemas.auth import Token, UserCreate
from app.config import settings

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Only use database authentication - no hardcoded test credentials

@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
):
    """
    Login endpoint. Authenticates against the database.
    """
    db = None
    async for session in get_db():
        db = session
        break

    if not db:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database connection failed",
        )

    stmt = select(User).where(User.email == form_data.username)
    result = await db.execute(stmt)
    user = result.scalars().first()

    if user and AuthService.verify_password(form_data.password, user.password_hash):
        access_token_expires = timedelta(minutes=settings.JWT_EXPIRY_MINUTES)
        access_token = AuthService.create_access_token(
            data={"sub": str(user.id), "role": user.role}, expires_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer"}

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Bearer"},
    )


@router.post("/signup", response_model=Token)
async def signup(
    user_data: UserCreate,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    # Check if user exists
    stmt = select(User).where(User.email == user_data.email)
    result = await db.execute(stmt)
    if result.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
        
    # Create new user
    hashed_password = AuthService.get_password_hash(user_data.password)
    
    # User model expects: email, password_hash, role
    new_user = User(
        email=user_data.email,
        password_hash=hashed_password,
        role=user_data.role
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    access_token_expires = timedelta(minutes=settings.JWT_EXPIRY_MINUTES)
    access_token = AuthService.create_access_token(
        data={"sub": str(new_user.id), "role": new_user.role}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
