"""
Module 5 — Pydantic Schemas for Treatment Suggestion
Input  : Module 3 output (differential diagnosis) + Module 1 (patient history)
Output : Treatment options with medications, follow-up instructions, contraindications
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.enums import (
    ContraindicationSeverity,
    MedicationType,
    TreatmentCategory,
    TreatmentType,
)


# ═════════════════════════════════════════════════════════════════════════════════
#  MEDICATION RECOMMENDATION SUB-SCHEMAS
# ═════════════════════════════════════════════════════════════════════════════════

class MedicationRecommendation(BaseModel):
    """Single medication recommendation"""

    medication_type: MedicationType = Field(
        ...,
        description="Type of medication (e.g., Antibiotic, Analgesic)",
    )
    drug_class: str = Field(
        ...,
        description="Specific drug class (e.g., Penicillin, NSAID)",
    )
    dosage: str = Field(
        default="Standard",
        description="Dosage instruction (e.g., '500mg')",
    )
    frequency: str = Field(
        default="3x daily",
        description="Frequency of administration",
    )
    duration_days: int = Field(
        default=7,
        description="Duration in days",
    )
    justification: str = Field(
        ...,
        description="Clinical reason for this medication",
    )
    potential_interactions: list[str] = Field(
        default_factory=list,
        description="Known interactions with other medications",
    )

    class Config:
        use_enum_values = False


class TreatmentOption(BaseModel):
    """Single treatment option"""

    treatment_type: TreatmentType = Field(
        ...,
        description="Treatment procedure type",
    )
    category: TreatmentCategory = Field(
        ...,
        description="Treatment category (Surgical, Restorative, etc.)",
    )
    description: str = Field(
        ...,
        description="Human-readable treatment description",
    )
    rank: int = Field(
        ...,
        description="Ranking (1=primary, 2=alternative, 3=tertiary)",
    )
    success_rate: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Expected success rate (0.0-1.0)",
    )
    medications: list[MedicationRecommendation] = Field(
        default_factory=list,
        description="Associated medication recommendations",
    )
    follow_up_days: int = Field(
        default=7,
        description="Recommended follow-up timing in days",
    )
    treatment_notes: str = Field(
        default="",
        description="Additional clinical notes",
    )

    class Config:
        use_enum_values = False


class ContraindicationAlert(BaseModel):
    """Alert for a treatment contraindication"""

    treatment_type: TreatmentType = Field(
        ...,
        description="Treatment that is contraindicated",
    )
    conflicting_condition: str = Field(
        ...,
        description="Patient condition causing contraindication",
    )
    severity: ContraindicationSeverity = Field(
        ...,
        description="Severity level of contraindication",
    )
    clinical_recommendation: str = Field(
        ...,
        description="Clinical guidance for managing this contraindication",
    )

    class Config:
        use_enum_values = False


class TreatmentSummary(BaseModel):
    """Overall treatment plan summary"""

    primary_treatment_name: str = Field(
        ...,
        description="Name of primary treatment recommendation",
    )
    total_alternatives: int = Field(
        ...,
        description="Number of alternative treatments offered",
    )
    medication_count: int = Field(
        ...,
        description="Total number of recommended medications",
    )
    contraindication_count: int = Field(
        ...,
        description="Number of contraindications flagged",
    )
    highest_contraindication_severity: Optional[ContraindicationSeverity] = Field(
        default=None,
        description="Maximum severity level of any contraindication",
    )
    overall_feasibility: str = Field(
        ...,
        description="Assessment of treatment feasibility ('High', 'Moderate', 'Low')",
    )
    clinical_summary: str = Field(
        ...,
        description="Human-readable treatment summary",
    )

    class Config:
        use_enum_values = False


# ═════════════════════════════════════════════════════════════════════════════════
#  M5 REQUEST & RESPONSE SCHEMAS
# ═════════════════════════════════════════════════════════════════════════════════

class TreatmentRequest(BaseModel):
    """
    Module 5 function call request.
    Wraps diagnosis + patient history for treatment recommendation.
    """

    module: str = Field(
        default="M5_Treatment",
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
        description="Primary diagnosis name",
    )
    confidence_percent: float = Field(
        ...,
        description="Confidence percentage for diagnosis",
    )

    # M1 data (patient history)
    systemic_conditions: list[str] = Field(
        default_factory=list,
        description="Patient's systemic conditions affecting treatment",
    )
    current_medications: list[str] = Field(
        default_factory=list,
        description="Patient's current medications (for interaction checking)",
    )
    allergies: list[str] = Field(
        default_factory=list,
        description="Known patient allergies",
    )
    age: int = Field(
        ...,
        ge=0,
        le=150,
        description="Patient age",
    )

    class Config:
        use_enum_values = False


class Module5Output(BaseModel):
    """
    Module 5 main output schema.
    Contains all treatment recommendations with medications and alerts.
    """

    module: str = Field(
        default="M5_Treatment",
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

    # Treatment recommendations
    primary_treatment: TreatmentOption = Field(
        ...,
        description="Primary recommended treatment",
    )
    alternative_treatments: list[TreatmentOption] = Field(
        default_factory=list,
        description="Ranked list of alternative treatments",
    )

    # Contraindication alerts
    contraindication_alerts: list[ContraindicationAlert] = Field(
        default_factory=list,
        description="Any contraindications for recommended treatments",
    )

    # Overall summary
    summary: TreatmentSummary = Field(
        ...,
        description="Aggregated summary of treatment plan",
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


class TreatmentResponse(BaseModel):
    """
    Wrapper for HTTP response containing Module 5 output.
    """

    status: str = Field(
        default="success",
        description="Operation status",
    )
    data: Module5Output = Field(
        ...,
        description="Module 5 output",
    )
    message: Optional[str] = Field(
        default=None,
        description="Optional status message",
    )

    class Config:
        use_enum_values = False
