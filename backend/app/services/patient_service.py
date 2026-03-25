"""
Patient Service
Handles CRUD operations for patient records.
Reference: SRS §4.2 (Patient Management)
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Optional, List

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.db_models import Patient
from pydantic import BaseModel, Field, EmailStr
from app.models.enums import Gender


# ─── Pydantic Schemas for Patient Management ─────────────────────────────────

class PatientCreate(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    dob: datetime
    gender: Gender
    contact_phone: Optional[str] = Field(None, max_length=20)
    contact_email: Optional[EmailStr] = None
    medical_history: Optional[dict] = None


class PatientResponse(PatientCreate):
    id: uuid.UUID
    doctor_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PatientUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    dob: Optional[datetime] = None
    gender: Optional[Gender] = None
    contact_phone: Optional[str] = None
    contact_email: Optional[EmailStr] = None
    medical_history: Optional[dict] = None


# ─── Service Implementation ──────────────────────────────────────────────────

class PatientService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_patient(self, payload: PatientCreate, doctor_id: uuid.UUID) -> Patient:
        """Create a new patient record."""
        patient = Patient(
            doctor_id=doctor_id,
            first_name=payload.first_name,
            last_name=payload.last_name,
            dob=payload.dob,
            gender=payload.gender.value,  # Enum to string
            contact_phone=payload.contact_phone,
            contact_email=payload.contact_email,
            medical_history=payload.medical_history,
        )
        self.db.add(patient)
        await self.db.commit()
        await self.db.refresh(patient)
        return patient

    async def get_patient(self, patient_id: uuid.UUID) -> Optional[Patient]:
        """Retrieve a patient by ID."""
        result = await self.db.execute(select(Patient).where(Patient.id == patient_id))
        return result.scalars().first()

    async def list_patients(
        self, doctor_id: uuid.UUID = None, skip: int = 0, limit: int = 100
    ) -> List[Patient]:
        """
        List patients.
        If doctor_id is provided: returns only that doctor's patients.
        If doctor_id is None: returns all patients (for receptionists/admins).
        """
        query = select(Patient).offset(skip).limit(limit)
        
        if doctor_id:
            query = query.where(Patient.doctor_id == doctor_id)
        
        query = query.order_by(Patient.last_name, Patient.first_name)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def update_patient(
        self, patient_id: uuid.UUID, payload: PatientUpdate
    ) -> Optional[Patient]:
        """Update patient details."""
        patient = await self.get_patient(patient_id)
        if not patient:
            return None

        update_data = payload.model_dump(exclude_unset=True)
        if "gender" in update_data and update_data["gender"]:
            update_data["gender"] = update_data["gender"].value

        for key, value in update_data.items():
            setattr(patient, key, value)

        patient.updated_at = datetime.now(timezone.utc)
        await self.db.commit()
        await self.db.refresh(patient)
        return patient
