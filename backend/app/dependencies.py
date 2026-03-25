"""
Common API Dependencies
"""
import uuid
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import BaseModel

from app.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


class CurrentUser(BaseModel):
    """Current authenticated user info"""
    user_id: uuid.UUID
    role: str


async def get_current_user(token: str = Depends(oauth2_scheme)) -> CurrentUser:
    """
    Validates JWT token and returns the authenticated user's ID and role.
    Supports Doctor, Receptionist, and Admin roles.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        user_id: str = payload.get("sub")
        user_role: str = payload.get("role", "Doctor")
        if user_id is None:
            raise credentials_exception
        return CurrentUser(user_id=uuid.UUID(user_id), role=user_role)
    except (JWTError, ValueError):
        raise credentials_exception


async def get_current_doctor_id(token: str = Depends(oauth2_scheme)) -> uuid.UUID:
    """
    Validates JWT token and returns the authenticated user's ID if role is Doctor or Admin.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        user_id: str = payload.get("sub")
        user_role: str = payload.get("role", "Doctor")
        if user_id is None:
            raise credentials_exception
        if user_role not in ["DOCTOR", "ADMIN"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only doctors and admins can access this resource"
            )
        return uuid.UUID(user_id)
    except (JWTError, ValueError):
        raise credentials_exception
