"""
Module 3 — Pydantic Schemas for Differential Diagnosis Engine
Input  : Module 1 output + Module 2 output (combined)
Output : Top-N ranked differential diagnoses with confidence & justification
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.enums import (
    BoneDensity,
    Gender,
    JawRegion,
    SmokingStatus,
    SwellingGrade,
    Symptom,
    SymptomOnset,
    SystemicCondition,
    ToothMobilityGrade,
    PercussionTest,
    VitalityTest,
    AdjacentTeethStatus,
    UrgencyFlag,
)
from app.schemas.risk_engine import (
    AlertSeverity,
    ComplexityClass,
    ImplantFeasibility,
    RiskLevel,
)


# ═════════════════════════════════════════════════════════════════════════════════
#  M1 INPUT SUB-SCHEMAS  (re-used from risk_engine for self-containment)
# ═════════════════════════════════════════════════════════════════════════════════

class M1Demographics(BaseModel):
    age: int
    gender: Gender
    weight_kg: Optional[float] = None


class M1MedicalHistory(BaseModel):
    systemic_conditions: list[SystemicCondition]
    allergies: list[str] = []
    current_medications: list[str] = []
    bleeding_disorder: bool
    immunocompromised: bool
    smoking_status: SmokingStatus
    bisphosphonate_therapy: bool
    radiation_therapy_head_neck: bool


class M1ChiefComplaint(BaseModel):
    description: str
    symptoms: list[Symptom]
    duration_days: int
    onset: Optional[SymptomOnset] = None


class M1Fever(BaseModel):
    present: bool
    temperature_celsius: Optional[float] = None


class M1ClinicalAssessment(BaseModel):
    pain_level: int
    swelling_grade: SwellingGrade
    fever: M1Fever
    lymphadenopathy: Optional[bool] = None
    tooth_mobility_grade: Optional[ToothMobilityGrade] = None
    percussion_test: Optional[PercussionTest] = None
    vitality_test: Optional[VitalityTest] = None
    probing_depth_mm: Optional[float] = None


class M1SiteAssessment(BaseModel):
    tooth_site: str
    jaw_region: JawRegion
    bone_height_mm: Optional[float] = None
    bone_width_mm: Optional[float] = None
    bone_density: Optional[BoneDensity] = None
    adjacent_teeth_status: Optional[AdjacentTeethStatus] = None
    sinus_proximity_mm: Optional[float] = None
    nerve_proximity_mm: Optional[float] = None


class M1ComputedFlags(BaseModel):
    urgency_flag: UrgencyFlag
    bisphosphonate_risk: bool
    radiation_risk: bool
    age_contraindication: bool
    implant_data_present: bool


class M1ValidationStatus(BaseModel):
    is_valid: bool
    errors: list[str] = []
    warnings: list[str] = []


class M1Data(BaseModel):
    """Module 1 output embedded in M3 request."""
    module: str = "M1_Clinical_Input"
    version: str = "1.0"
    generated_at: datetime
    case_id: UUID
    patient_id: UUID
    doctor_id: UUID
    demographics: M1Demographics
    medical_history: M1MedicalHistory
    chief_complaint: M1ChiefComplaint
    clinical_assessment: M1ClinicalAssessment
    site_assessment: M1SiteAssessment
    clinical_notes: Optional[str] = None
    computed_flags: M1ComputedFlags
    validation_status: M1ValidationStatus


# ═════════════════════════════════════════════════════════════════════════════════
#  M2 INPUT SUB-SCHEMAS (minimal — only fields M3 needs)
# ═════════════════════════════════════════════════════════════════════════════════

class M2RiskAlert(BaseModel):
    rule_id: str
    category: str
    severity: AlertSeverity
    message: str
    detail: Optional[str] = None


class M2InfectionAnalysis(BaseModel):
    pattern: str
    indicators: list[str] = []
    spread_risk: str


class M2RiskSummary(BaseModel):
    overall_risk_level: RiskLevel
    risk_score: int = Field(..., ge=0, le=100)
    immediate_attention_required: bool
    implant_feasibility: ImplantFeasibility
    alert_count: int


class M2SurgicalComplexity(BaseModel):
    score: int = Field(..., ge=0, le=100)
    complexity_class: ComplexityClass
    factors: list[str] = []


class M2Data(BaseModel):
    """Module 2 output embedded in M3 request."""
    module: str = "M2_Risk_Engine"
    version: str = "1.0"
    generated_at: datetime
    case_id: UUID
    patient_id: UUID
    doctor_id: UUID
    risk_summary: M2RiskSummary
    alerts: list[M2RiskAlert] = []
    infection_analysis: Optional[M2InfectionAnalysis] = None
    surgical_complexity: Optional[M2SurgicalComplexity] = None


# ═════════════════════════════════════════════════════════════════════════════════
#  MODULE 3 REQUEST
# ═════════════════════════════════════════════════════════════════════════════════

class DiagnosisRequest(BaseModel):
    """
    Input to the Differential Diagnosis Engine.
    Accepts M1 + M2 outputs together.
    """
    m1: M1Data
    m2: M2Data
    max_results: int = Field(
        3, ge=1, le=10,
        description="Maximum number of differential diagnoses to return (default 3).",
    )


# ═════════════════════════════════════════════════════════════════════════════════
#  MODULE 3 OUTPUT
# ═════════════════════════════════════════════════════════════════════════════════

class SupportingEvidence(BaseModel):
    """A single piece of clinical evidence supporting a diagnosis."""
    finding: str = Field(..., description="Name of the clinical finding")
    value: str = Field(..., description="Observed value")
    weight: str = Field(..., description="How strongly it supports: Strong / Moderate / Weak")


class ContradictingEvidence(BaseModel):
    """A clinical finding that argues against a diagnosis."""
    finding: str
    value: str
    reason: str


class DifferentialDiagnosis(BaseModel):
    """A single ranked differential diagnosis."""
    rank: int = Field(..., ge=1, description="Rank position (1 = most likely)")
    code: str = Field(..., description="Diagnosis code, e.g. DX-03")
    name: str = Field(..., description="Human-readable diagnosis name")
    category: str = Field(..., description="Pulpal / Periapical / Periodontal / Infection / Trauma / Other")
    confidence_pct: float = Field(..., ge=0.0, le=100.0, description="Confidence percentage 0-100")
    description: str = Field(..., description="Brief clinical description")
    supporting_evidence: list[SupportingEvidence] = Field(default_factory=list)
    contradicting_evidence: list[ContradictingEvidence] = Field(default_factory=list)
    justification: str = Field(..., description="2-3 sentence reasoning summary")


class Module3Output(BaseModel):
    """
    Complete Module 3 output JSON contract.
    Consumed by Module 4 (Investigation), Module 5 (Treatment), Module 6 (Explainability).
    """
    module: str = "M3_Differential_Diagnosis"
    version: str = "1.0"
    generated_at: datetime
    case_id: UUID
    patient_id: UUID
    doctor_id: UUID

    differentials: list[DifferentialDiagnosis] = Field(
        ..., description="Top-N ranked differential diagnoses",
    )
    profiles_evaluated: int = Field(0, description="Total diagnosis profiles scored")
    clinical_summary: str = Field(
        ..., description="One-paragraph clinical presentation summary",
    )


# ═════════════════════════════════════════════════════════════════════════════════
#  API RESPONSE ENVELOPE
# ═════════════════════════════════════════════════════════════════════════════════

class DiagnosisResponse(BaseModel):
    """Success response wrapper for POST /api/diagnosis/differential"""
    status: str = "success"
    data: Module3Output
    message: str = "Differential diagnosis completed successfully."


class DiagnosisErrorResponse(BaseModel):
    """Error response wrapper"""
    status: str = "error"
    errors: list[dict]
