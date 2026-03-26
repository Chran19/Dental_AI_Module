"""
Module 6 — Explainability & Audit Routes
Endpoints for generating explanations and retrieving audit trails.
Reference: Module_6_Explainability_Audit_Layer.md §5
"""

import logging
from fastapi import APIRouter, HTTPException, status
from typing import Optional

from app.schemas.explainability import ExplanationReport, AuditTrail
from app.schemas.clinical_input import Module1Output
from app.schemas.risk_engine import Module2Output
from app.schemas.diagnosis import Module3Output
from app.schemas.investigation import Module4Output
from app.schemas.treatment import Module5Output
from app.services.explainability_service import ExplainabilityService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/explainability", tags=["Module 6: Explainability"])


@router.post("/generate", response_model=ExplanationReport)
async def generate_explanation(
    m1: Optional[Module1Output] = None,
    m2: Optional[Module2Output] = None,
    m3: Optional[Module3Output] = None,
    m4: Optional[Module4Output] = None,
    m5: Optional[Module5Output] = None,
) -> ExplanationReport:
    """
    Generate a comprehensive human-readable explanation for a case.

    This endpoint takes outputs from modules M1–M5 and produces:
    - Natural language summary
    - Risk alerts and rules triggered
    - Diagnosis breakdown with scoring
    - Investigation justifications
    - Treatment recommendations and contraindication warnings
    - Audit trail metadata

    **Input:** Any combination of M1–M5 outputs  
    **Output:** ExplanationReport with narrative, traces, and clinical summary

    **Example Response:**
    ```json
    {
        "case_id": "550e8400-e29b-41d4-a716-446655440000",
        "summary": "Based on the clinical presentation, the leading diagnosis is Irreversible Pulpitis (confidence: 85%). Imaging recommended: Periapical. We recommend Root Canal...",
        "m3_scoring_trace": [
            {
                "diagnosis_code": "DX-01",
                "diagnosis_name": "Irreversible Pulpitis",
                "confidence": 85.0
            }
        ],
        "clinical_summary": "Patient: 35 years old, Male. Chief complaint: Spontaneous tooth pain...",
        "generated_at": "2026-03-20T10:30:45.123Z"
    }
    ```
    """
    try:
        logger.info(f"Generating explanation for case with M3: {m3 is not None}")

        result = ExplainabilityService.generate_explanation(
            m1_output=m1,
            m2_output=m2,
            m3_output=m3,
            m4_output=m4,
            m5_output=m5,
        )

        logger.info(f"Explanation generated: {result.case_id}")
        return result

    except Exception as e:
        logger.error(f"Error generating explanation: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate explanation: {str(e)}",
        )


@router.get("/audit/{case_id}", response_model=AuditTrail)
async def get_case_audit_trail(case_id: str) -> AuditTrail:
    """
    Retrieve the audit trail for a previously analyzed case.

    An audit trail records every step of the case analysis, including:
    - Module execution order and timing
    - Rules triggered
    - Decision points
    - Any errors or warnings

    **Path Parameters:**
    - `case_id`: Unique case identifier (UUID)

    **Returns:** Complete audit trail with timestamps and module actions

    **Note:** In production, this would query CaseHistory and AuditLog tables.
    Currently, it builds a sample trail for demonstration.
    """
    try:
        logger.info(f"Retrieving audit trail for case: {case_id}")

        # In production, would query database:
        # case = db.query(CaseHistory).filter(CaseHistory.case_id == case_id).first()
        # if not case:
        #     raise HTTPException(status_code=404, detail="Case not found")
        # audit_entries = db.query(AuditLog).filter(AuditLog.case_id == case_id).all()

        # For now, build demonstrative audit trail
        trail = ExplainabilityService.build_audit_trail(
            m1_id=case_id, m2_id=case_id, m3_id=case_id
        )

        logger.info(f"Audit trail retrieved: {len(trail.entries)} entries")
        return trail

    except Exception as e:
        logger.error(f"Error retrieving audit trail: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve audit trail: {str(e)}",
        )


@router.get("/health")
async def health() -> dict:
    """Health check endpoint for Module 6."""
    return {
        "status": "healthy",
        "module": "M6 - Explainability",
        "endpoints": ["/api/explain/generate", "/api/explain/audit/{case_id}"],
    }
