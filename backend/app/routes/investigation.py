"""
Module 4 — Investigation & Imaging Recommendation API Route
Endpoint: POST /api/investigation/recommend
Accepts diagnosis information → returns ranked investigation recommendations.
"""

from __future__ import annotations

import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.schemas.investigation import (
    InvestigationRequest,
    InvestigationResponse,
    Module4Output,
)
from app.services.investigation_service import InvestigationService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/investigation", tags=["Investigation (Module 4)"])


# ─── Dependencies ────────────────────────────────────────────────────────────────

def get_investigation_service() -> InvestigationService:
    """Dependency: Investigation Service instance"""
    return InvestigationService()


async def get_current_doctor_id(request: Request) -> uuid.UUID:
    """
    Placeholder for JWT authentication.
    TODO: Replace with real JWT auth dependency (AUTH module).
    """
    return uuid.UUID("d0c1b2a3-e4f5-6789-0abc-de1234567890")


# ═════════════════════════════════════════════════════════════════════════════════
# POST /api/investigation/recommend
# ═════════════════════════════════════════════════════════════════════════════════

@router.post(
    "/recommend",
    response_model=InvestigationResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate investigation recommendations from diagnosis",
    description=(
        "Accepts Module 4 investigation request (diagnosis code + optional M2 risk data). "
        "Returns ranked investigation recommendations (imaging modalities + lab tests) "
        "with urgency levels and clinical justifications. "
        "Includes risk-based amplification logic."
    ),
    responses={
        200: {"description": "Investigation recommendations generated successfully."},
        400: {"description": "Invalid diagnosis code or request format."},
        422: {"description": "Validation error in request payload."},
        500: {"description": "Internal server error during recommendation generation."},
    },
)
async def recommend_investigation(
    payload: InvestigationRequest,
    doctor_id: uuid.UUID = Depends(get_current_doctor_id),
    service: InvestigationService = Depends(get_investigation_service),
) -> InvestigationResponse:
    """
    Module 4 main endpoint: Generate investigation recommendations.

    **Input:**
    - Diagnosis code (e.g., "DX-01")
    - Optional M2 risk factors (for amplification)

    **Pipeline:**
    1. Look up investigation profile for diagnosis
    2. Build imaging and lab recommendations
    3. Apply M2 risk amplification rules
    4. Rank by urgency
    5. Return consolidated recommendations

    **Risk Amplification Examples:**
    - High bone loss → Add CBCT imaging
    - Systemic infection → Escalate urgency to EMERGENCY
    - Immunocompromised → Add baseline blood work

    **Response:**
    Imaging recommendations, lab test recommendations, overall urgency, clinical summary.
    """
    try:
        # Call service to generate recommendations
        output: Module4Output = service.recommend(payload)

        logger.info(
            "M4 investigation | case_id=%s top_dx=%s imaging=%d labs=%d urgency=%s",
            output.case_id,
            output.referenced_diagnosis_code,
            output.summary.total_imaging_count,
            output.summary.total_lab_count,
            output.summary.overall_urgency.value,
        )

        return InvestigationResponse(
            status="success",
            data=output,
            message=f"Investigation recommendations generated for {payload.top_diagnosis_name}",
        )

    except ValueError as e:
        logger.error(
            "M4 validation error | case_id=%s error=%s",
            payload.case_id,
            str(e),
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid investigation request: {str(e)}",
        )

    except Exception as e:
        logger.error(
            "M4 investigation service error | case_id=%s error=%s",
            payload.case_id,
            str(e),
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Investigation recommendation failed: {str(e)}",
        )


# ═════════════════════════════════════════════════════════════════════════════════
# GET /api/investigation/profiles/{diagnosis_code}
# ═════════════════════════════════════════════════════════════════════════════════

@router.get(
    "/profiles/{diagnosis_code}",
    status_code=status.HTTP_200_OK,
    summary="Get investigation profile for a diagnosis",
    description="Retrieve the standard investigation profile for a given diagnosis code.",
    responses={
        200: {"description": "Investigation profile returned."},
        404: {"description": "Diagnosis code not found in profiles."},
    },
)
async def get_investigation_profile(
    diagnosis_code: str,
) -> dict:
    """
    Retrieve investigation profile details for a diagnosis code.

    This endpoint returns the base investigation recommendations without
    any risk amplification (i.e., the profile data as stored).

    **Example:**
    GET /api/investigation/profiles/DX-01
    """
    from app.services.investigation_profiles import INVESTIGATION_PROFILES

    profile = INVESTIGATION_PROFILES.get(diagnosis_code)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No investigation profile found for diagnosis code: {diagnosis_code}",
        )

    return {
        "diagnosis_code": diagnosis_code,
        "diagnosis_name": profile.get("diagnosis_name", "Unknown"),
        "imaging": [str(img) for img in profile.get("imaging", [])],
        "labs": [str(lab) for lab in profile.get("labs", [])],
        "urgency": profile.get("urgency", "Routine").value if hasattr(profile.get("urgency"), "value") else str(profile.get("urgency")),
        "justification": profile.get("justification", ""),
    }
