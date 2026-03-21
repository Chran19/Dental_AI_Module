"""
Implant Tracker Routes
API for managing dental implant lifecycle.
"""
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_doctor_id
from app.schemas.implants import ImplantCreate, ImplantResponse, ImplantUpdate
from app.services.implant_service import ImplantService

router = APIRouter(prefix="/api/implants", tags=["Implant Tracker"])

@router.post("/", response_model=ImplantResponse, status_code=status.HTTP_201_CREATED)
async def create_plan(
    data: ImplantCreate,
    current_user_id: UUID = Depends(get_current_doctor_id),
    db: AsyncSession = Depends(get_db)
):
    """Start a new implant case/plan."""
    service = ImplantService(db)
    return await service.create_plan(data)

@router.get("/{plan_id}", response_model=ImplantResponse)
async def get_plan(
    plan_id: UUID,
    current_user_id: UUID = Depends(get_current_doctor_id),
    db: AsyncSession = Depends(get_db)
):
    service = ImplantService(db)
    plan = await service.get_plan(plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    return plan

@router.put("/{plan_id}", response_model=ImplantResponse)
async def update_plan(
    plan_id: UUID,
    data: ImplantUpdate,
    current_user_id: UUID = Depends(get_current_doctor_id),
    db: AsyncSession = Depends(get_db)
):
    """
    Update stage, status, or clinical details.
    Example: Move from 'Planning' to 'Surgery_Scheduled'.
    """
    service = ImplantService(db)
    updated = await service.update_plan(plan_id, data)
    if not updated:
        raise HTTPException(status_code=404, detail="Plan not found")
    return updated

@router.get("/patient/{patient_id}", response_model=List[ImplantResponse])
async def list_by_patient(
    patient_id: UUID,
    current_user_id: UUID = Depends(get_current_doctor_id),
    db: AsyncSession = Depends(get_db)
):
    service = ImplantService(db)
    return await service.list_by_patient(patient_id)
