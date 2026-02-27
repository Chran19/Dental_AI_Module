"""
Module 1 — Clinical Input API Route
Endpoint: POST /api/clinical-input/validate
Reference: Module_1_Clinical_Input_Processing.md §7
"""

from __future__ import annotations

import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import ValidationError

from app.schemas.clinical_input import (
    ClinicalInputRequest,
    ClinicalInputResponse,
    Module1Output,
    ValidationErrorItem,
    ValidationErrorResponse,
)
from app.services.clinical_input_service import ClinicalInputService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/clinical-input", tags=["Clinical Input (Module 1)"])

# ─── Dependency: Service instance ────────────────────────────────────────────

def get_clinical_input_service() -> ClinicalInputService:
    return ClinicalInputService()


# ─── Dependency: Authenticated doctor ID ─────────────────────────────────────
# TODO: Replace with real JWT auth dependency (AUTH module FR-01)

async def get_current_doctor_id(request: Request) -> uuid.UUID:
    """
    Placeholder for JWT authentication.
    In production, this extracts doctor_id from the Bearer token.
    For development, returns a static UUID.
    """
    # Check for Authorization header
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        # TODO: Decode JWT and extract doctor_id
        # For now, return a dev placeholder
        pass

    # Development fallback
    return uuid.UUID("d0c1b2a3-e4f5-6789-0abc-de1234567890")


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
        output: Module1Output = service.process(
            request=payload,
            doctor_id=doctor_id,
        )

        # TODO: Persist to ClinicalCases table (§9 DB Mapping)
        # await persist_clinical_case(output)

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
