"""
Image Management Schemas
"""
from datetime import datetime
from uuid import UUID
from enum import Enum
from typing import Optional

from pydantic import BaseModel, HttpUrl
from app.models.enums import ImageModality

class ImageResponse(BaseModel):
    id: UUID
    patient_id: UUID
    case_id: Optional[UUID] = None
    modality: str
    file_url: str
    file_type: str
    file_size_mb: float
    notes: Optional[str] = None
    upload_date: datetime

    class Config:
        from_attributes = True

class ImageUpdate(BaseModel):
    modality: Optional[ImageModality] = None
    notes: Optional[str] = None
