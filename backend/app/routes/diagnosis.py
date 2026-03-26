"""
Module 3 — Differential Diagnosis API Route
Endpoint: POST /api/diagnosis/differential
Accepts M1 + M2 output → returns ranked differential diagnoses.
"""

from __future__ import annotations

import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.schemas.diagnosis import (
    DiagnosisRequest,
    DiagnosisResponse,
    Module3Output,
)
from app.services.diagnosis_service import DiagnosisService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/diagnosis", tags=["Differential Diagnosis (Module 3)"])


# ─── Dependencies ────────────────────────────────────────────────────────────

def get_diagnosis_service() -> DiagnosisService:
    return DiagnosisService()


async def get_current_doctor_id(request: Request) -> uuid.UUID:
    """
    Placeholder for JWT authentication.
    TODO: Replace with real JWT auth dependency (AUTH module).
    """
    return uuid.UUID("d0c1b2a3-e4f5-6789-0abc-de1234567890")


# ═════════════════════════════════════════════════════════════════════════════════
# POST /api/diagnosis/differential
# ═════════════════════════════════════════════════════════════════════════════════

@router.post(
    "/differential",
    response_model=DiagnosisResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate differential diagnoses from M1 + M2 data",
    description=(
        "Accepts Module 1 (clinical input) and Module 2 (risk assessment) "
        "outputs. Scores each diagnosis profile against the clinical "
        "presentation and returns ranked differentials with confidence "
        "percentages, supporting/contradicting evidence, and justification."
    ),
    responses={
        200: {"description": "Differential diagnosis completed successfully."},
        401: {"description": "Unauthorized — invalid or expired token."},
        422: {"description": "Validation error in request payload."},
        500: {"description": "Internal server error."},
    },
)
async def differential_diagnosis(
    payload: DiagnosisRequest,
    doctor_id: uuid.UUID = Depends(get_current_doctor_id),
    service: DiagnosisService = Depends(get_diagnosis_service),
) -> DiagnosisResponse:
    """
    Module 3 main endpoint.

    **Pipeline:**
    1. Accept M1 + M2 JSON (validated by Pydantic).
    2. Score all diagnosis profiles against clinical data.
    3. Rank by confidence, attach evidence chains.
    4. Return top-N differentials for downstream modules.
    """
    try:
        output: Module3Output = service.diagnose(payload)

        logger.info(
            "M3 diagnosis | case_id=%s top_dx=%s confidence=%.1f%% profiles=%d",
            output.case_id,
            output.differentials[0].name if output.differentials else "none",
            output.differentials[0].confidence_pct if output.differentials else 0,
            output.profiles_evaluated,
        )

        return DiagnosisResponse(
            status="success",
            data=output,
            message="Differential diagnosis completed successfully.",
        )

    except ValueError as e:
        logger.warning("M3 validation error: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "status": "error",
                "errors": [{"field": "general", "message": str(e)}],
            },
        )

    except Exception as e:
        logger.exception("M3 internal error during diagnosis")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": "Internal server error."},
        )
