"""
Queue Schema - Patient queue management schemas
"""

from datetime import datetime
from typing import Optional
import uuid
from pydantic import BaseModel, Field


class QueueItemCreate(BaseModel):
    """Create a new queue entry when patient checks in"""
    patient_id: uuid.UUID = Field(..., description="Patient UUID")
    notes: Optional[str] = Field(None, max_length=500)


class QueueItemUpdate(BaseModel):
    """Update queue item status"""
    status: str = Field(..., description="Queue status: Waiting, In_Consultation, Completed, Cancelled")
    assigned_doctor_id: Optional[uuid.UUID] = None
    notes: Optional[str] = None


class QueueItemResponse(BaseModel):
    """Queue item response model"""
    id: uuid.UUID
    patient_id: uuid.UUID
    status: str
    check_in_time: Optional[datetime] = None
    consultation_start_time: Optional[datetime] = None
    consultation_end_time: Optional[datetime] = None
    assigned_doctor_id: Optional[uuid.UUID] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class QueueListResponse(BaseModel):
    """Queue list with patient details"""
    id: uuid.UUID
    patient_id: uuid.UUID
    patient_name: str
    patient_phone: Optional[str] = None
    status: str
    priority: str = "NORMAL"  # Default to NORMAL; can be enhanced to derive from diagnosis
    check_in_time: Optional[datetime] = None
    assigned_doctor_id: Optional[uuid.UUID] = None
    doctor_name: Optional[str] = None
    position_in_queue: int
    estimated_wait_time: Optional[int] = None  # in minutes
    created_at: datetime
    reason_of_visit: Optional[str] = None  # Added to match frontend expectations
    notes: Optional[str] = None  # Added to match frontend expectations

    class Config:
        from_attributes = True
