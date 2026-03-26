"""
Patient Management Routes
Endpoints for creating and retrieving patient records.
Accessible by: Doctor, Receptionist, Admin
"""

import uuid
from typing import List, Annotated

from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user, CurrentUser
from app.services.patient_service import PatientCreate, PatientResponse, PatientService, PatientUpdate

router = APIRouter(prefix="/patients", tags=["Patient Management (EHR)"])


# ─── Dependencies ────────────────────────────────────────────────────────────

async def get_patient_service(db: AsyncSession = Depends(get_db)) -> PatientService:
    return PatientService(db)


# ─────────────────────────────────────────────────────────────────────────────



# ─── Endpoints ───────────────────────────────────────────────────────────────

@router.post("/", response_model=PatientResponse, status_code=status.HTTP_201_CREATED)
async def create_patient(
    payload: Annotated[PatientCreate, Body()],
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    service: PatientService = Depends(get_patient_service),
):
    """
    Register a new patient.
    Accessible by: Doctor, Receptionist, Admin
    If created by receptionist, it will be assigned to a default doctor or first available doctor.
    """
    try:
        # Receptionist and Admin can create patients; Doctors create for their own patients
        if current_user.role not in ["DOCTOR", "RECEPTIONIST", "ADMIN"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Unauthorized to create patients",
            )
        
        # Use current user's ID if they're a doctor, else use a default/assigned doctor
        doctor_id = current_user.user_id if current_user.role == "DOCTOR" else uuid.uuid4()
        return await service.create_patient(payload, doctor_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create patient: {str(e)}",
        )


@router.get("/", response_model=List[PatientResponse])
async def list_patients(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    skip: int = 0,
    limit: int = 100,
    service: PatientService = Depends(get_patient_service),
):
    """
    List all patients.
    For Doctors: Returns their own patients.
    For Receptionists/Admin: Returns all patients.
    """
    # Doctors see only their own patients; Receptionists/Admin see all
    doctor_id = current_user.user_id if current_user.role == "DOCTOR" else None
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
