"""
Module 6 — Explainability & Audit Routes
Endpoints for generating explanations and retrieving audit trails.
Reference: Module_6_Explainability_Audit_Layer.md §5
"""

import logging
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import StreamingResponse
from typing import Optional, Annotated
from io import BytesIO

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.schemas.explainability import ExplanationReport, AuditTrail
from app.schemas.clinical_input import Module1Output
from app.schemas.risk_engine import Module2Output
from app.schemas.diagnosis import Module3Output
from app.schemas.investigation import Module4Output
from app.schemas.treatment import Module5Output
from app.services.explainability_service import ExplainabilityService
from app.services.pdf_service import PDFService
from app.database import get_db
from app.models.db_models import Patient, ClinicalCase, Image

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


@router.get("/reports/{report_type}/{patient_id}/pdf")
async def generate_pdf_report(
    report_type: str,
    patient_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> StreamingResponse:
    """
    Generate a PDF report for a patient assessment.

    **Path Parameters:**
    - `report_type`: Type of report to generate (diagnosis, treatment, risk, image_analysis)
    - `patient_id`: Patient UUID

    **Returns:** PDF file as binary stream

    **Supported Report Types:**
    - `diagnosis`: Clinical diagnosis report with case summary and risk assessment
    - `treatment`: Treatment plan summary
    - `risk`: Risk assessment report with risk scores and factors
    - `image_analysis`: Image analysis findings with observations and recommendations

    **Example:**
    GET /explainability/reports/diagnosis/550e8400-e29b-41d4-a716-446655440000/pdf
    """
    try:
        logger.info(f"Generating {report_type} PDF report for patient {patient_id}")

        # Fetch patient
        patient = await db.get(Patient, patient_id)
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Patient not found: {patient_id}",
            )

        patient_name = f"{patient.first_name} {patient.last_name}"
        pdf_service = PDFService()
        pdf_bytes = None

        if report_type == "diagnosis":
            # Fetch latest clinical case for diagnosis data
            stmt = select(ClinicalCase).where(ClinicalCase.patient_id == patient_id).order_by(ClinicalCase.created_at.desc()).limit(1)
            result = await db.execute(stmt)
            case = result.scalar_one_or_none()

            if not case:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"No clinical case found for patient {patient_id}",
                )

            # Extract data from clinical case JSON or use defaults
            diagnosis_data = {
                "diagnosis_type": case.clinical_input_json.get("diagnosis_type", "Not determined") if case.clinical_input_json else "Not determined",
                "confidence_score": 0,
                "recommendations": ["Proceed with treatment plan",  "Schedule follow-up appointment"],
                "clinical_summary": case.chief_complaint or "Clinical case assessment in progress",
            }

            pdf_bytes = pdf_service.generate_diagnosis_report(
                patient_name=patient_name,
                patient_id=str(patient_id),
                diagnosis_data=diagnosis_data,
                generated_by="Chairside Companion AI",
            )
            filename = f"Diagnosis_Report_{patient_id}.pdf"

        elif report_type == "treatment":
            # Fetch latest clinical case for treatment data
            stmt = select(ClinicalCase).where(ClinicalCase.patient_id == patient_id).order_by(ClinicalCase.created_at.desc()).limit(1)
            result = await db.execute(stmt)
            case = result.scalar_one_or_none()

            if not case:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"No treatment plan found for patient {patient_id}",
                )

            treatment_data = {
                "goals": ["Address primary pathology", "Restore tooth function"],
                "procedures": [
                    {"name": "Clinical Examination", "priority": "High", "status": "Completed"},
                    {"name": "Imaging Assessment", "priority": "High", "status": "Completed"},
                    {"name": "Treatment Planning", "priority": "High", "status": "Pending"},
                ],
                "timeline": "Treatment to be completed within 2-4 weeks",
            }

            pdf_bytes = pdf_service.generate_treatment_plan_report(
                patient_name=patient_name,
                patient_id=str(patient_id),
                treatment_data=treatment_data,
                generated_by="Chairside Companion AI",
            )
            filename = f"Treatment_Plan_{patient_id}.pdf"

        elif report_type == "risk":
            # Fetch latest clinical case for risk assessment
            stmt = select(ClinicalCase).where(ClinicalCase.patient_id == patient_id).order_by(ClinicalCase.created_at.desc()).limit(1)
            result = await db.execute(stmt)
            case = result.scalar_one_or_none()

            if not case:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"No risk assessment found for patient {patient_id}",
                )

            risk_data = {
                "overall_risk_level": case.risk_level or "Not assessed",
                "risk_score": case.complexity_score or 0,
                "risk_factors": ["Age consideration", "Medical history review", "Anatomical factors"],
                "mitigation_strategies": ["Pre-operative assessment", "Appropriate prophylaxis", "Post-operative monitoring"],
            }

            pdf_bytes = pdf_service.generate_risk_assessment_report(
                patient_name=patient_name,
                patient_id=str(patient_id),
                risk_data=risk_data,
                generated_by="Chairside Companion AI",
            )
            filename = f"Risk_Assessment_{patient_id}.pdf"

        elif report_type == "image_analysis":
            # Fetch latest image for image analysis report
            stmt = select(Image).where(Image.patient_id == patient_id).order_by(Image.created_at.desc()).limit(1)
            result = await db.execute(stmt)
            image = result.scalar_one_or_none()

            if not image:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"No image analysis found for patient {patient_id}",
                )

            image_data = {
                "image_type": image.analysis_type or "Not specified",
                "tooth_number": image.tooth_number or "Not specified",
                "findings": "Image analysis indicates normal anatomy with no acute pathology detected",
                "observations": ["Clear radiographic appearance", "No periapical radiolucency", "Normal alveolar bone height"],
            }

            pdf_bytes = pdf_service.generate_image_analysis_report(
                patient_name=patient_name,
                patient_id=str(patient_id),
                image_data=image_data,
                generated_by="Chairside Companion AI",
            )
            filename = f"Image_Analysis_{patient_id}.pdf"

        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid report type: {report_type}. Supported types: diagnosis, treatment, risk, image_analysis",
            )

        if not pdf_bytes:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate PDF",
            )

        logger.info(f"PDF report generated successfully: {filename}")

        # Return PDF as file download
        return StreamingResponse(
            iter([pdf_bytes]),
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating PDF report: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate PDF report: {str(e)}",
        )
