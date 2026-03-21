"""
Implant Management Schemas
"""
from typing import Optional, Dict
from datetime import datetime, date
from uuid import UUID
from enum import Enum

from pydantic import BaseModel, Field

from app.models.enums import ImplantStage

class ImplantPlanStatus(str, Enum):
    DRAFT = "Draft"
    FINAL = "Final"

class ImplantCreate(BaseModel):
    patient_id: UUID
    case_id: Optional[UUID] = None
    tooth_site: str = Field(..., example="11")
    bone_height: Optional[float] = None
    bone_width: Optional[float] = None
    implant_system: Optional[str] = None
    diameter: Optional[float] = None
    length: Optional[float] = None

class ImplantUpdate(BaseModel):
    bone_height: Optional[float] = None
    bone_width: Optional[float] = None
    implant_system: Optional[str] = None
    diameter: Optional[float] = None
    length: Optional[float] = None
    status: Optional[ImplantPlanStatus] = None
    clinical_stage: Optional[ImplantStage] = None
    surgery_date: Optional[date] = None
    restoration_date: Optional[date] = None
    notes: Optional[str] = None

class ImplantResponse(ImplantCreate):
    id: UUID
    clinical_stage: ImplantStage
    status: ImplantPlanStatus
    risk_flags: Optional[Dict] = None
    surgery_date: Optional[date] = None
    restoration_date: Optional[date] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
