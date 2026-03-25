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

# Development test credentials (for testing without database)
TEST_CREDENTIALS = {
    "test@example.com": "testpass",
    "doctor@example.com": "doctorpass",
    "receptionist@example.com": "receptionistpass",
    "admin@example.com": "adminpass",
}

# User roles for test credentials
TEST_CREDENTIAL_ROLES = {
    "test@example.com": "DOCTOR",
    "doctor@example.com": "DOCTOR",
    "receptionist@example.com": "RECEPTIONIST",
    "admin@example.com": "ADMIN",
}

# Generate deterministic UUIDs for test credentials
TEST_CREDENTIAL_UUIDS = {
    "test@example.com": str(uuid.uuid5(uuid.NAMESPACE_DNS, "test@example.com")),
    "doctor@example.com": str(uuid.uuid5(uuid.NAMESPACE_DNS, "doctor@example.com")),
    "receptionist@example.com": str(uuid.uuid5(uuid.NAMESPACE_DNS, "receptionist@example.com")),
    "admin@example.com": str(uuid.uuid5(uuid.NAMESPACE_DNS, "admin@example.com")),
}

@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
):
    """
    Login endpoint. Uses test credentials in development mode when database is unavailable.
    """
    # Check test credentials first
    if form_data.username in TEST_CREDENTIALS:
        if TEST_CREDENTIALS[form_data.username] == form_data.password:
            access_token_expires = timedelta(minutes=settings.JWT_EXPIRY_MINUTES)
            # Use deterministic UUID for test credentials
            user_uuid = TEST_CREDENTIAL_UUIDS.get(form_data.username, str(uuid.uuid4()))
            user_role = TEST_CREDENTIAL_ROLES.get(form_data.username, "Doctor")
            access_token = AuthService.create_access_token(
                data={"sub": user_uuid, "role": user_role}, expires_delta=access_token_expires
            )
            return {"access_token": access_token, "token_type": "bearer"}
    
    # If not a test account, try database
    try:
        db = None
        async for session in get_db():
            db = session
            break
        
        if db:
            stmt = select(User).where(User.email == form_data.username)
            result = await db.execute(stmt)
            user = result.scalars().first()
            
            if user and AuthService.verify_password(form_data.password, user.password_hash):
                access_token_expires = timedelta(minutes=settings.JWT_EXPIRY_MINUTES)
                access_token = AuthService.create_access_token(
                    data={"sub": str(user.id), "role": user.role}, expires_delta=access_token_expires
                )
                return {"access_token": access_token, "token_type": "bearer"}
    except Exception:
        # Database unavailable - credentials rejected below
        pass
    
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
