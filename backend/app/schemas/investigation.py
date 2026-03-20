"""
Module 4 — Pydantic Schemas for Investigation & Imaging Recommendation
Input  : Module 3 output (differential diagnosis)
Output : Recommended imaging modalities, lab tests, urgency level
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.enums import ImagingType, InvestigationUrgency, LabTestType


# ═════════════════════════════════════════════════════════════════════════════════
#  INVESTIGATION RECOMMENDATION SUB-SCHEMAS
# ═════════════════════════════════════════════════════════════════════════════════

class ImagingRecommendation(BaseModel):
    """Single imaging modality recommendation"""

    imaging_type: ImagingType = Field(
        ...,
        description="Type of imaging modality (e.g., CBCT, Periapical)",
    )
    justification: str = Field(
        ...,
        description="Clinical reason for this imaging recommendation",
    )
    urgency: InvestigationUrgency = Field(
        default=InvestigationUrgency.ROUTINE,
        description="Priority level for this imaging",
    )
    estimated_cost_usd: Optional[float] = Field(
        default=None,
        description="Approximate cost in USD (for reference)",
    )

    class Config:
        use_enum_values = False


class LabTestRecommendation(BaseModel):
    """Single lab test recommendation"""

    test_type: LabTestType = Field(
        ...,
        description="Type of lab test (e.g., WBC, CRP, INR)",
    )
    justification: str = Field(
        ...,
        description="Clinical reason for this lab test",
    )
    urgency: InvestigationUrgency = Field(
        default=InvestigationUrgency.ROUTINE,
        description="Priority level for this lab test",
    )
    fasting_required: bool = Field(
        default=False,
        description="Whether fasting is required before test",
    )

    class Config:
        use_enum_values = False


class InvestigationSummary(BaseModel):
    """Overall investigation plan summary"""

    total_imaging_count: int = Field(
        ...,
        description="Total number of imaging modalities recommended",
    )
    total_lab_count: int = Field(
        ...,
        description="Total number of lab tests recommended",
    )
    overall_urgency: InvestigationUrgency = Field(
        ...,
        description="Maximum urgency level among all recommendations",
    )
    estimated_total_cost_usd: Optional[float] = Field(
        default=None,
        description="Approximate total cost for all recommendations",
    )
    summary_text: str = Field(
        ...,
        description="Human-readable summary of investigation plan",
    )

    class Config:
        use_enum_values = False


# ═════════════════════════════════════════════════════════════════════════════════
#  M4 REQUEST & RESPONSE SCHEMAS
# ═════════════════════════════════════════════════════════════════════════════════

class InvestigationRequest(BaseModel):
    """
    Module 4 function call request.
    Wraps Module 3 output for investigation recommendation.
    """

    module: str = Field(
        default="M4_Investigation",
        description="Module identifier",
    )
    version: str = Field(
        default="1.0",
        description="Schema version",
    )
    generated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Timestamp of request generation",
    )
    case_id: str = Field(
        ...,
        description="Unique case identifier",
    )
    patient_id: str = Field(
        ...,
        description="Unique patient identifier",
    )
    doctor_id: str = Field(
        ...,
        description="Unique doctor identifier",
    )

    # M3 output (differential diagnosis)
    top_diagnosis_code: str = Field(
        ...,
        description="Primary diagnosis code (e.g., DX-01)",
    )
    top_diagnosis_name: str = Field(
        ...,
        description="Primary diagnosis name (e.g., Irreversible Pulpitis)",
    )
    confidence_percent: float = Field(
        ...,
        description="Confidence percentage for primary diagnosis",
    )

    # Optional M2 risk data for amplification
    risk_factors: Optional[list[str]] = Field(
        default=None,
        description="List of risk factors from M2 (for urgency amplification)",
    )
    overall_risk_level: Optional[str] = Field(
        default=None,
        description="Overall risk level from M2",
    )

    class Config:
        use_enum_values = False


class Module4Output(BaseModel):
    """
    Module 4 main output schema.
    Contains all investigation recommendations with metadata.
    """

    module: str = Field(
        default="M4_Investigation",
        description="Module identifier",
    )
    version: str = Field(
        default="1.0",
        description="Schema version",
    )
    generated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Timestamp of output generation",
    )
    case_id: str = Field(
        ...,
        description="Unique case identifier (echoed from request)",
    )
    patient_id: str = Field(
        ...,
        description="Unique patient identifier (echoed from request)",
    )
    doctor_id: str = Field(
        ...,
        description="Unique doctor identifier (echoed from request)",
    )

    # Investigation recommendations
    imaging_recommendations: list[ImagingRecommendation] = Field(
        default_factory=list,
        description="Ranked list of imaging modalities to order",
    )
    lab_recommendations: list[LabTestRecommendation] = Field(
        default_factory=list,
        description="Ranked list of lab tests to order",
    )

    # Overall summary
    summary: InvestigationSummary = Field(
        ...,
        description="Aggregated summary of investigation plan",
    )

    # Audit trail
    referenced_diagnosis_code: str = Field(
        ...,
        description="Diagnosis code used to generate recommendations",
    )
    reasoning_chain: Optional[list[str]] = Field(
        default=None,
        description="Step-by-step reasoning for recommendations",
    )

    class Config:
        use_enum_values = False


class InvestigationResponse(BaseModel):
    """
    Wrapper for HTTP response containing Module 4 output.
    """

    status: str = Field(
        default="success",
        description="Operation status",
    )
    data: Module4Output = Field(
        ...,
        description="Module 4 output",
    )
    message: Optional[str] = Field(
        default=None,
        description="Optional status message",
    )

    class Config:
        use_enum_values = False
