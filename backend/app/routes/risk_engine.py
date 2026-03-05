"""
Module 2 — Risk Engine API Route
Endpoint: POST /api/risk-engine/assess
Accepts Module 1 output JSON → returns risk assessment.
"""

from __future__ import annotations

import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.schemas.risk_engine import (
    Module2Output,
    RiskEngineRequest,
    RiskEngineResponse,
)
from app.services.risk_engine_service import RiskEngineService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/risk-engine", tags=["Risk Engine (Module 2)"])


# ─── Dependencies ────────────────────────────────────────────────────────────

def get_risk_engine_service() -> RiskEngineService:
    return RiskEngineService()


async def get_current_doctor_id(request: Request) -> uuid.UUID:
    """
    Placeholder for JWT authentication.
    TODO: Replace with real JWT auth dependency (AUTH module).
    """
    return uuid.UUID("d0c1b2a3-e4f5-6789-0abc-de1234567890")


# ═════════════════════════════════════════════════════════════════════════════════
# POST /api/risk-engine/assess
# ═════════════════════════════════════════════════════════════════════════════════

@router.post(
    "/assess",
    response_model=RiskEngineResponse,
    status_code=status.HTTP_200_OK,
    summary="Assess clinical risk from Module 1 output",
    description=(
        "Accepts the complete Module 1 clinical input JSON and runs it "
        "through the deterministic rule-based risk engine. Evaluates bone "
        "adequacy, systemic disease risk, infection patterns, and surgical "
        "complexity. Returns alerts, risk scores, and implant feasibility."
    ),
    responses={
        200: {"description": "Risk assessment completed successfully."},
        401: {"description": "Unauthorized — invalid or expired token."},
        422: {"description": "Validation error in Module 1 payload."},
        500: {"description": "Internal server error."},
    },
)
async def assess_risk(
    payload: RiskEngineRequest,
    doctor_id: uuid.UUID = Depends(get_current_doctor_id),
    service: RiskEngineService = Depends(get_risk_engine_service),
) -> RiskEngineResponse:
    """
    Module 2 main endpoint.

    **Pipeline:**
    1. Accept M1 JSON (validated by Pydantic schema).
    2. Run bone, systemic, infection, and complexity rules.
    3. Compute composite risk score.
    4. Return structured M2 JSON for downstream modules.
    """
    try:
        output: Module2Output = service.assess(payload)

        # TODO: Persist risk_assessment_json to ClinicalCases table
        # await update_clinical_case_risk(output)

        logger.info(
            "M2 risk assessed | case_id=%s risk=%s score=%d alerts=%d",
            output.case_id,
            output.risk_summary.overall_risk_level.value,
            output.risk_summary.risk_score,
            output.risk_summary.alert_count,
        )

        return RiskEngineResponse(
            status="success",
            data=output,
            message="Risk assessment completed successfully.",
        )

    except ValueError as e:
        logger.warning("M2 validation error: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "status": "error",
                "errors": [{"field": "general", "message": str(e)}],
            },
        )

    except Exception as e:
        logger.exception("M2 internal error during risk assessment")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": "Internal server error."},
        )


# ═════════════════════════════════════════════════════════════════════════════════
# POST /api/risk-engine/assess-from-case (Pipeline convenience endpoint)
# ═════════════════════════════════════════════════════════════════════════════════

@router.post(
    "/assess-from-m1",
    response_model=RiskEngineResponse,
    status_code=status.HTTP_200_OK,
    summary="Run full M1 → M2 pipeline in one call",
    description=(
        "Accepts a raw clinical input request (Module 1 format), processes it "
        "through Module 1, then immediately pipes the output to Module 2."
    ),
)
async def assess_from_m1_input(
    payload: RiskEngineRequest,
    doctor_id: uuid.UUID = Depends(get_current_doctor_id),
    service: RiskEngineService = Depends(get_risk_engine_service),
) -> RiskEngineResponse:
    """
    Convenience endpoint: same as /assess but intended for pipeline chaining.
    Frontend can call this after receiving M1 output.
    """
    return await assess_risk(payload, doctor_id, service)
