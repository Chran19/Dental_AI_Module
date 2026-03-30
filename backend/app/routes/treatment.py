"""
Module 5 — Treatment Suggestion API Route
Endpoint: POST /treatment/suggest
Accepts diagnosis + patient history → returns ranked treatment recommendations.
"""

from __future__ import annotations

import logging
import uuid
from typing import List, Any

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.schemas.treatment import (
    TreatmentRequest,
    TreatmentResponse,
    Module5Output,
)
from app.services.treatment_service import TreatmentService
from app.models.db_models import ClinicalCase

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/treatment", tags=["Treatment (Module 5)"])


# ─── Dependencies ────────────────────────────────────────────────────────────────

def get_treatment_service() -> TreatmentService:
    """Dependency: Treatment Service instance"""
    return TreatmentService()


async def get_current_doctor_id(request: Request) -> uuid.UUID:
    """
    Placeholder for JWT authentication.
    TODO: Replace with real JWT auth dependency (AUTH module).
    """
    return uuid.UUID("d0c1b2a3-e4f5-6789-0abc-de1234567890")


# ═════════════════════════════════════════════════════════════════════════════════
# GET /treatment?patient_id={patient_id}
# ═════════════════════════════════════════════════════════════════════════════════

@router.get("/")
async def get_treatments_by_patient(
    patient_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> List[Any]:
    """
    Retrieve all treatment plans (Module 5 outputs) for a patient.
    Returns treatment_json from all ClinicalCases for this patient.
    """
    try:
        query = select(ClinicalCase).where(
            ClinicalCase.patient_id == patient_id,
            ClinicalCase.treatment_json != None,
        )
        result = await db.execute(query)
        cases = result.scalars().all()
        
        treatments = []
        for case in cases:
            if case.treatment_json:
                treatments.append({
                    "case_id": str(case.id),
                    "patient_id": str(case.patient_id),
                    "plan_date": case.created_at.isoformat() if case.created_at else None,
                    **case.treatment_json,  # Spread the treatment data
                })
        
        return treatments
    except Exception as e:
        logger.exception("Failed to retrieve treatment plans for patient %s: %s", patient_id, str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": "Failed to retrieve treatment plans"},
        )


# ═════════════════════════════════════════════════════════════════════════════════
# POST /treatment/suggest
# ═════════════════════════════════════════════════════════════════════════════════

@router.post(
    "/suggest",
    response_model=TreatmentResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate treatment recommendations from diagnosis",
    description=(
        "Accepts Module 5 treatment request (diagnosis code + patient history). "
        "Returns ranked treatment options (primary + alternatives) with medications, "
        "follow-up guidelines, and contraindication alerts. "
        "Incorporates patient medical history for safety checks."
    ),
    responses={
        200: {"description": "Treatment recommendations generated successfully."},
        400: {"description": "Invalid diagnosis code or request format."},
        422: {"description": "Validation error in request payload."},
        500: {"description": "Internal server error during recommendation generation."},
    },
)
async def suggest_treatment(
    payload: TreatmentRequest,
    doctor_id: uuid.UUID = Depends(get_current_doctor_id),
    service: TreatmentService = Depends(get_treatment_service),
) -> TreatmentResponse:
    """
    Module 5 main endpoint: Generate treatment recommendations.

    **Input:**
    - Diagnosis code (e.g., "DX-01")
    - Patient systemic conditions (for contraindication checking)
    - Patient medications and allergies
    - Patient age

    **Pipeline:**
    1. Look up treatment protocol for diagnosis
    2. Build primary + alternative treatment options
    3. Check for contraindications against patient history
    4. Add medication recommendations
    5. Assess overall feasibility
    6. Return consolidated treatment plan

    **Contraindication Checking:**
    - Extraction + Bisphosphonates → SEVERE alert
    - Implant + Active Infection → ABSOLUTE alert
    - Surgery + Uncontrolled Diabetes → SEVERE alert
    - Plus 15+ other clinical interactions

    **Response:**
    Primary treatment, alternative treatments, medications, follow-up schedule,
    contraindication alerts, feasibility assessment.
    """
    try:
        # Call service to generate recommendations
        output: Module5Output = service.suggest(payload)

        logger.info(
            "M5 treatment | case_id=%s diagnosis=%s primary=%s alternatives=%d alerts=%d feasibility=%s",
            output.case_id,
            output.referenced_diagnosis_code,
            output.primary_treatment.treatment_type.value,
            output.summary.total_alternatives,
            output.summary.contraindication_count,
            output.summary.overall_feasibility,
        )

        return TreatmentResponse(
            status="success",
            data=output,
            message=f"Treatment recommendations generated for {payload.top_diagnosis_name}",
        )

    except ValueError as e:
        logger.error(
            "M5 validation error | case_id=%s error=%s",
            payload.case_id,
            str(e),
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid treatment request: {str(e)}",
        )

    except Exception as e:
        logger.error(
            "M5 treatment service error | case_id=%s error=%s",
            payload.case_id,
            str(e),
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Treatment recommendation failed: {str(e)}",
        )


# ═════════════════════════════════════════════════════════════════════════════════
# GET /api/treatment/protocols/{diagnosis_code}
# ═════════════════════════════════════════════════════════════════════════════════

@router.get(
    "/protocols/{diagnosis_code}",
    status_code=status.HTTP_200_OK,
    summary="Get treatment protocol for a diagnosis",
    description="Retrieve the standard treatment protocol for a given diagnosis code.",
    responses={
        200: {"description": "Treatment protocol returned."},
        404: {"description": "Diagnosis code not found in protocols."},
    },
)
async def get_treatment_protocol(
    diagnosis_code: str,
) -> dict:
    """
    Retrieve treatment protocol details for a diagnosis code.

    This endpoint returns the base treatment protocol without any patient-specific
    modifications (i.e., the profile data as stored).

    **Example:**
    GET /api/treatment/protocols/DX-01
    """
    from app.services.treatment_profiles import TREATMENT_PROTOCOLS

    protocol = TREATMENT_PROTOCOLS.get(diagnosis_code)
    if not protocol:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No treatment protocol found for diagnosis code: {diagnosis_code}",
        )

    return {
        "diagnosis_code": protocol.diagnosis_code,
        "diagnosis_name": protocol.diagnosis_name,
        "primary_treatment": protocol.primary_treatment.value,
        "primary_category": protocol.primary_category.value,
        "alternatives": [
            {
                "treatment": alt[0].value,
                "category": alt[1].value,
            }
            for alt in protocol.alternative_treatments
        ],
        "medications": [med.value for med in protocol.recommended_medications],
        "follow_up_days": protocol.follow_up_days,
        "success_rate": protocol.success_rate_baseline,
        "notes": protocol.treatment_notes,
    }
