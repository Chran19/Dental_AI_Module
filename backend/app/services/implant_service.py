"""
Implant Service
Handles lifecycle of dental implants from planning to completion.
"""
from typing import List, Optional
from uuid import UUID
from datetime import datetime, timezone

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.db_models import ImplantPlan
from app.schemas.implants import ImplantCreate, ImplantUpdate

class ImplantService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_plan(self, data: ImplantCreate) -> ImplantPlan:
        implant = ImplantPlan(
            patient_id=data.patient_id,
            case_id=data.case_id,
            tooth_site=data.tooth_site,
            bone_height=data.bone_height,
            bone_width=data.bone_width,
            implant_system=data.implant_system,
            diameter=data.diameter,
            length=data.length,
            status="Draft",
            clinical_stage="Planning"
        )
        self.db.add(implant)
        await self.db.commit()
        await self.db.refresh(implant)
        return implant

    async def get_plan(self, plan_id: UUID) -> Optional[ImplantPlan]:
        result = await self.db.execute(select(ImplantPlan).where(ImplantPlan.id == plan_id))
        return result.scalars().first()

    async def list_by_patient(self, patient_id: UUID) -> List[ImplantPlan]:
        result = await self.db.execute(select(ImplantPlan).where(ImplantPlan.patient_id == patient_id))
        return result.scalars().all()

    async def update_plan(self, plan_id: UUID, data: ImplantUpdate) -> Optional[ImplantPlan]:
        implant = await self.get_plan(plan_id)
        if not implant:
            return None
            
        update_data = data.model_dump(exclude_unset=True)
        if not update_data:
            return implant
            
        # Manually apply updates (or use stmt)
        for key, value in update_data.items():
            setattr(implant, key, value)
            
        implant.updated_at = datetime.now(timezone.utc)
        
        await self.db.commit()
        await self.db.refresh(implant)
        return implant
