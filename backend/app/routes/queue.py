"""
Queue Management Routes (Receptionist Module)
Endpoints for managing patient queue, check-ins, and status updates
"""

from typing import Annotated, List
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user, CurrentUser
from app.services.queue_service import QueueService
from app.schemas.queue import QueueItemCreate, QueueItemUpdate, QueueItemResponse, QueueListResponse
from app.models.db_models import Patient, User, Queue

router = APIRouter(prefix="/queue", tags=["Queue Management"])


def get_queue_service() -> QueueService:
    """Dependency injection for queue service"""
    return QueueService()


@router.post("/check-in", response_model=QueueItemResponse, status_code=status.HTTP_201_CREATED)
async def check_in_patient(
    payload: QueueItemCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
):
    """
    Check in a patient to the queue.
    Required role: Receptionist or Admin
    """
    # Verify role
    if current_user.role not in ["RECEPTIONIST", "ADMIN"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only receptionists and admins can check in patients",
        )

    # Verify patient exists
    patient = await db.get(Patient, payload.patient_id)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found",
        )

    # Check if patient is already in queue
    existing = await QueueService.get_patient_queue_position(db, payload.patient_id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Patient is already in queue at position {existing}",
        )

    queue_entry = await QueueService.check_in_patient(db, payload.patient_id, payload.notes)
    return queue_entry


@router.get("/active", response_model=List[QueueListResponse])
async def get_active_queue(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
):
    """
    Get all active queue entries (Waiting + In_Consultation).
    Accessible by: Receptionist, Doctor, Admin
    """
    if current_user.role not in ["RECEPTIONIST", "DOCTOR", "ADMIN"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unauthorized access to queue",
        )

    queue_entries = await QueueService.get_active_queue(db)
    
    # Build response with patient and doctor info
    response_list = []
    for idx, entry in enumerate(queue_entries, 1):
        try:
            # Safe extraction of doctor name
            doctor_name = None
            if entry.assigned_doctor_id and entry.doctor:
                doctor_name = entry.doctor.email.split("@")[0] if entry.doctor.email else "Unknown"
            
            response_list.append(
                QueueListResponse(
                    id=entry.id,
                    patient_id=entry.patient_id,
                    patient_name=f"{entry.patient.first_name} {entry.patient.last_name}",
                    patient_phone=entry.patient.contact_phone,
                    status=entry.status,
                    priority="NORMAL",  # TODO: Derive from patient diagnosis/investigation urgency
                    check_in_time=entry.check_in_time,
                    assigned_doctor_id=entry.assigned_doctor_id,
                    doctor_name=doctor_name,
                    position_in_queue=idx,
                    estimated_wait_time=None,
                    created_at=entry.created_at,
                    reason_of_visit=entry.notes,  # Store reason in notes field
                    notes=entry.notes,
                )
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error processing queue entry: {str(e)}",
            )
    return response_list


@router.get("/{queue_id}", response_model=QueueItemResponse)
async def get_queue_item(
    queue_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
):
    """Get a specific queue entry by ID"""
    queue_entry = await QueueService.get_queue_by_id(db, queue_id)
    if not queue_entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Queue entry not found",
        )
    return queue_entry


@router.patch("/{queue_id}", response_model=QueueItemResponse)
async def update_queue_item(
    queue_id: uuid.UUID,
    payload: QueueItemUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
):
    """
    Update queue entry status.
    Doctors can update status to In_Consultation/Completed.
    Receptionists can update notes and cancel entries.
    """
    queue_entry = await QueueService.get_queue_by_id(db, queue_id)
    if not queue_entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Queue entry not found",
        )

    # Role-based permission checks
    if current_user.role == "DOCTOR":
        # Doctors can only update their own queue items or items without assignment
        if (
            queue_entry.assigned_doctor_id
            and queue_entry.assigned_doctor_id != current_user.user_id
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot update queue item assigned to another doctor",
            )
        # Auto-assign doctor if not already assigned
        if not queue_entry.assigned_doctor_id:
            payload.assigned_doctor_id = current_user.user_id

    elif current_user.role not in ["RECEPTIONIST", "ADMIN"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unauthorized to update queue",
        )

    updated_entry = await QueueService.update_queue_status(
        db,
        queue_id,
        payload.status,
        payload.assigned_doctor_id,
        payload.notes,
    )

    if not updated_entry:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update queue entry",
        )

    return updated_entry


@router.delete("/{queue_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_from_queue(
    queue_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
):
    """
    Remove patient from queue (mark as completed).
    Can be called by: Receptionist, Doctor, Admin
    """
    if current_user.role not in ["RECEPTIONIST", "DOCTOR", "ADMIN"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unauthorized to remove from queue",
        )

    success = await QueueService.remove_from_queue(db, queue_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Queue entry not found",
        )


@router.get("/doctor/{doctor_id}", response_model=List[QueueItemResponse])
async def get_doctor_queue(
    doctor_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
):
    """Get queue entries assigned to a specific doctor"""
    # Only the doctor themselves or admin can view their queue
    if (
        current_user.role == "DOCTOR"
        and current_user.user_id != doctor_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot view another doctor's queue",
        )

    queue_entries = await QueueService.get_queue_for_doctor(db, doctor_id)
    return queue_entries


@router.get("/stats/count", response_model=dict)
async def get_queue_stats(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
):
    """Get queue statistics"""
    count = await QueueService.get_queue_count(db)
    return {
        "total_in_queue": count,
        "timestamp": __import__("datetime").datetime.now(__import__("datetime").timezone.utc),
    }
