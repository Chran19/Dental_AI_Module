"""
Module 1 — Clinical Input API Route
Endpoint: POST /api/clinical-input/validate
Reference: Module_1_Clinical_Input_Processing.md §7
"""

from __future__ import annotations

import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.config import settings
from app.dependencies import get_current_doctor_id
from app.schemas.clinical_input import (
    ClinicalInputRequest,
    ClinicalInputResponse,
    Module1Output,
    ValidationErrorItem,
    ValidationErrorResponse,
)
from app.services.clinical_input_service import ClinicalInputService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/clinical-input", tags=["Clinical Input (Module 1)"])

# ─── Dependency: Service instance ────────────────────────────────────────────

def get_clinical_input_service() -> ClinicalInputService:
    return ClinicalInputService()


# ─── Dependency: Authenticated doctor ID ─────────────────────────────────────
# Imported from app.dependencies


# ═════════════════════════════════════════════════════════════════════════════════
# POST /api/clinical-input/validate
# ═════════════════════════════════════════════════════════════════════════════════

@router.post(
    "/validate",
    response_model=ClinicalInputResponse,
    status_code=status.HTTP_200_OK,
    summary="Validate and structure clinical input",
    description=(
        "Accepts raw clinical input from the doctor, validates all fields "
        "(§4.1), runs cross-field validation (§4.2), applies sanitization "
        "(§4.3), computes flags (§5.3), and returns the structured M1 JSON "
        "contract consumed by all downstream modules."
    ),
    responses={
        200: {
            "description": "Clinical input validated and structured successfully.",
            "model": ClinicalInputResponse,
        },
        401: {"description": "Session expired or invalid token."},
        413: {"description": "Request payload too large (> 1MB)."},
        422: {
            "description": "Validation errors in input fields.",
            "model": ValidationErrorResponse,
        },
        429: {"description": "Rate limit exceeded."},
        500: {"description": "Internal server error."},
    },
)
async def validate_clinical_input(
    payload: ClinicalInputRequest,
    db: AsyncSession = Depends(get_db),
    doctor_id: uuid.UUID = Depends(get_current_doctor_id),
    service: ClinicalInputService = Depends(get_clinical_input_service),
) -> ClinicalInputResponse:
    """
    Module 1 main endpoint.

    **Processing Pipeline:**
    1. Pydantic validates the incoming JSON (field types, ranges, enums).
    2. Service layer sanitizes text, computes flags, generates warnings.
    3. Returns the structured M1 JSON ready for Module 2 (Risk Engine).

    **Error Handling (§10):**
    - Missing/invalid fields → 422 with per-field error array.
    - Expired JWT → 401 redirect to login.
    - Oversized payload → 413.
    """
    try:
        # Run the M1 processing pipeline
        output: Module1Output = await service.process(
            request=payload,
            doctor_id=doctor_id,
            db=db
        )

        logger.info(
            "M1 clinical input processed | case_id=%s patient_id=%s doctor_id=%s",
            output.case_id,
            output.patient_id,
            doctor_id,
        )

        return ClinicalInputResponse(
            status="success",
            data=output,
            message="Clinical input validated and structured successfully.",
        )

    except ValueError as e:
        # Sanitization or cross-field validation errors
        logger.warning("M1 validation error: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "status": "error",
                "errors": [{"field": "general", "message": str(e)}],
            },
        )

    except Exception as e:
        logger.exception("M1 internal error during clinical input processing")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": "Internal server error."},
        )


# ═════════════════════════════════════════════════════════════════════════════════
# GET /api/clinical-input/patient/{patient_id}
# ═════════════════════════════════════════════════════════════════════════════════

@router.get(
    "/patient/{patient_id}",
    status_code=status.HTTP_200_OK,
    summary="Get all assessments for a patient",
    description="Retrieves all clinical assessments (cases) for a specific patient.",
)
async def get_patient_assessments(
    patient_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    doctor_id: uuid.UUID = Depends(get_current_doctor_id),
):
    """
    Retrieve all clinical assessments for a patient authorized to the current doctor.
    
    **Authorization:**
    - Doctor can only view assessments they created or for patients in their care.
    """
    try:
        from sqlalchemy import select
        from app.models.db_models import ClinicalCase
        
        # Query for all assessments for this patient created by this doctor
        stmt = select(ClinicalCase).where(
            (ClinicalCase.patient_id == patient_id) &
            (ClinicalCase.doctor_id == doctor_id)
        ).order_by(ClinicalCase.created_at.desc())
        
        result = await db.execute(stmt)
        assessments = result.scalars().all()
        
        logger.info(
            "Retrieved %d assessments for patient_id=%s doctor_id=%s",
            len(assessments),
            patient_id,
            doctor_id,
        )
        
        return {
            "status": "success",
            "data": [
                {
                    "id": str(a.id),
                    "patient_id": str(a.patient_id),
                    "doctor_id": str(a.doctor_id),
                    "clinical_input_json": a.clinical_input_json,
                    "chief_complaint": a.chief_complaint,
                    "urgency_flag": a.urgency_flag,
                    "status": a.status,
                    "created_at": a.created_at.isoformat(),
                    "updated_at": a.updated_at.isoformat(),
                }
                for a in assessments
            ],
            "count": len(assessments),
        }
        
    except Exception as e:
        logger.exception("Error retrieving patient assessments")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": "Internal server error."},
        )


# ═════════════════════════════════════════════════════════════════════════════════
# GET /api/clinical-input/{assessment_id}
# ═════════════════════════════════════════════════════════════════════════════════

@router.get(
    "/{assessment_id}",
    status_code=status.HTTP_200_OK,
    summary="Get a specific clinical assessment",
    description="Retrieves detailed information about a specific clinical assessment.",
)
async def get_assessment(
    assessment_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    doctor_id: uuid.UUID = Depends(get_current_doctor_id),
):
    """
    Retrieve a specific clinical assessment by ID.
    
    **Authorization:**
    - Doctor can only view assessments they created.
    """
    try:
        from sqlalchemy import select
        from app.models.db_models import ClinicalCase
        
        # Query for the specific assessment
        stmt = select(ClinicalCase).where(
            (ClinicalCase.id == assessment_id) &
            (ClinicalCase.doctor_id == doctor_id)
        )
        
        result = await db.execute(stmt)
        assessment = result.scalar_one_or_none()
        
        if not assessment:
            logger.warning(
                "Assessment not found or unauthorized: assessment_id=%s doctor_id=%s",
                assessment_id,
                doctor_id,
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"message": "Assessment not found."},
            )
        
        logger.info(
            "Retrieved assessment: assessment_id=%s doctor_id=%s",
            assessment_id,
            doctor_id,
        )
        
        return {
            "status": "success",
            "data": {
                "id": str(assessment.id),
                "patient_id": str(assessment.patient_id),
                "doctor_id": str(assessment.doctor_id),
                "clinical_input_json": assessment.clinical_input_json,
                "chief_complaint": assessment.chief_complaint,
                "urgency_flag": assessment.urgency_flag,
                "input_valid": assessment.input_valid,
                "status": assessment.status,
                "risk_assessment_json": assessment.risk_assessment_json,
                "risk_level": assessment.risk_level,
                "created_at": assessment.created_at.isoformat(),
                "updated_at": assessment.updated_at.isoformat(),
            },
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error retrieving assessment")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": "Internal server error."},
        )
