"""
Queue Service - Patient queue management logic
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Optional, List

from sqlalchemy import select, update, desc, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models.db_models import Queue, Patient, User
from app.schemas.queue import QueueItemCreate, QueueItemUpdate, QueueItemResponse, QueueListResponse


class QueueService:
    """Service for managing patient queue operations"""

    @staticmethod
    async def check_in_patient(
        db: AsyncSession, patient_id: uuid.UUID, notes: Optional[str] = None
    ) -> Queue:
        """Check in a patient to the queue"""
        queue_entry = Queue(
            patient_id=patient_id,
            status="Waiting",
            check_in_time=datetime.now(timezone.utc),
            notes=notes,
        )
        db.add(queue_entry)
        await db.commit()
        await db.refresh(queue_entry)
        return queue_entry

    @staticmethod
    async def get_active_queue(db: AsyncSession) -> List[Queue]:
        """Get all active queue entries (Waiting and In_Consultation)"""
        stmt = (
            select(Queue)
            .where(Queue.status.in_(["Waiting", "In_Consultation"]))
            .options(
                joinedload(Queue.patient),
                joinedload(Queue.doctor)
            )
            .order_by(Queue.created_at)
        )
        result = await db.execute(stmt)
        return result.unique().scalars().all()

    @staticmethod
    async def get_queue_by_id(db: AsyncSession, queue_id: uuid.UUID) -> Optional[Queue]:
        """Get a single queue entry by ID"""
        stmt = (
            select(Queue)
            .where(Queue.id == queue_id)
            .options(
                joinedload(Queue.patient),
                joinedload(Queue.doctor)
            )
        )
        result = await db.execute(stmt)
        return result.unique().scalars().first()

    @staticmethod
    async def update_queue_status(
        db: AsyncSession,
        queue_id: uuid.UUID,
        status: str,
        assigned_doctor_id: Optional[uuid.UUID] = None,
        notes: Optional[str] = None,
    ) -> Optional[Queue]:
        """Update queue entry status"""
        queue_entry = await QueueService.get_queue_by_id(db, queue_id)
        if not queue_entry:
            return None

        # Update timestamps based on status transitions
        update_data = {
            "status": status,
            "updated_at": datetime.now(timezone.utc),
        }

        if status == "In_Consultation" and not queue_entry.consultation_start_time:
            update_data["consultation_start_time"] = datetime.now(timezone.utc)

        if status == "Completed" and not queue_entry.consultation_end_time:
            update_data["consultation_end_time"] = datetime.now(timezone.utc)

        if assigned_doctor_id:
            update_data["assigned_doctor_id"] = assigned_doctor_id

        if notes is not None:
            update_data["notes"] = notes

        stmt = update(Queue).where(Queue.id == queue_id).values(**update_data)
        await db.execute(stmt)
        await db.commit()

        return await QueueService.get_queue_by_id(db, queue_id)

    @staticmethod
    async def remove_from_queue(db: AsyncSession, queue_id: uuid.UUID) -> bool:
        """Remove a patient from queue (mark as completed or cancelled)"""
        queue_entry = await QueueService.get_queue_by_id(db, queue_id)
        if not queue_entry:
            return False

        stmt = update(Queue).where(Queue.id == queue_id).values(
            status="Completed",
            consultation_end_time=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        await db.execute(stmt)
        await db.commit()
        return True

    @staticmethod
    async def get_queue_for_doctor(
        db: AsyncSession, doctor_id: uuid.UUID
    ) -> List[Queue]:
        """Get queue entries assigned to a specific doctor"""
        stmt = (
            select(Queue)
            .where(
                and_(
                    Queue.assigned_doctor_id == doctor_id,
                    Queue.status.in_(["Waiting", "In_Consultation"]),
                )
            )
            .options(
                joinedload(Queue.patient),
                joinedload(Queue.doctor)
            )
            .order_by(Queue.created_at)
        )
        result = await db.execute(stmt)
        return result.unique().scalars().all()

    @staticmethod
    async def get_queue_count(db: AsyncSession) -> int:
        """Get total number of patients in active queue"""
        stmt = select(Queue).where(
            Queue.status.in_(["Waiting", "In_Consultation"])
        )
        result = await db.execute(stmt)
        return len(result.scalars().all())

    @staticmethod
    async def get_patient_queue_position(
        db: AsyncSession, patient_id: uuid.UUID
    ) -> Optional[int]:
        """Get a patient's position in queue"""
        stmt = (
            select(Queue)
            .where(Queue.status.in_(["Waiting", "In_Consultation"]))
            .order_by(Queue.created_at)
        )
        result = await db.execute(stmt)
        queue_entries = result.scalars().all()

        for idx, entry in enumerate(queue_entries, 1):
            if entry.patient_id == patient_id:
                return idx
        return None
