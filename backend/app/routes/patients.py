"""
Patient Management Routes
Endpoints for creating and retrieving patient records.
Part of the missing EHR integration.
"""

import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.patient_service import PatientCreate, PatientResponse, PatientService, PatientUpdate

router = APIRouter(prefix="/api/patients", tags=["Patient Management (EHR)"])


# ─── Dependencies ────────────────────────────────────────────────────────────

async def get_patient_service(db: AsyncSession = Depends(get_db)) -> PatientService:
    return PatientService(db)


async def get_current_doctor_id() -> uuid.UUID:
    """Mock auth for development."""
    return uuid.UUID("d0c1b2a3-e4f5-6789-0abc-de1234567890")


# ─── Endpoints ───────────────────────────────────────────────────────────────

@router.post("/", response_model=PatientResponse, status_code=status.HTTP_201_CREATED)
async def create_patient(
    payload: PatientCreate,
    service: PatientService = Depends(get_patient_service),
    doctor_id: uuid.UUID = Depends(get_current_doctor_id),
):
    """Register a new patient."""
    try:
        return await service.create_patient(payload, doctor_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create patient: {str(e)}",
        )


@router.get("/", response_model=List[PatientResponse])
async def list_patients(
    skip: int = 0,
    limit: int = 100,
    service: PatientService = Depends(get_patient_service),
    doctor_id: uuid.UUID = Depends(get_current_doctor_id),
):
    """List all patients for the authenticated doctor."""
    return await service.list_patients(doctor_id, skip, limit)


@router.get("/{patient_id}", response_model=PatientResponse)
async def get_patient_details(
    patient_id: uuid.UUID,
    service: PatientService = Depends(get_patient_service),
):
    """Get a single patient record."""
    patient = await service.get_patient(patient_id)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found",
        )
    return patient


@router.patch("/{patient_id}", response_model=PatientResponse)
async def update_patient(
    patient_id: uuid.UUID,
    payload: PatientUpdate,
    service: PatientService = Depends(get_patient_service),
):
    """Update patient details."""
    patient = await service.update_patient(patient_id, payload)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found",
        )
    return patient
