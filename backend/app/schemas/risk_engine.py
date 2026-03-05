"""
Module 2 — Pydantic Schemas for Rule-Based Risk Engine
Defines the input contract (Module 1 output), risk rules output,
and the M2 JSON response contract.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
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


# ═════════════════════════════════════════════════════════════════════════════════
#  MODULE 2 ENUMS
# ═════════════════════════════════════════════════════════════════════════════════

class RiskLevel(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


class AlertSeverity(str, Enum):
    INFO = "Info"
    WARNING = "Warning"
    CRITICAL = "Critical"


class ComplexityClass(str, Enum):
    SIMPLE = "Simple"
    MODERATE = "Moderate"
    COMPLEX = "Complex"
    HIGHLY_COMPLEX = "Highly_Complex"


class ImplantFeasibility(str, Enum):
    FEASIBLE = "Feasible"
    CONDITIONAL = "Conditional"
    NOT_RECOMMENDED = "Not_Recommended"
    INSUFFICIENT_DATA = "Insufficient_Data"


# ═════════════════════════════════════════════════════════════════════════════════
#  M1 INPUT SUB-SCHEMAS  (re-declared as read-only input contracts)
#  These mirror Module 1 output; kept here so Module 2 is self-contained.
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


# ═════════════════════════════════════════════════════════════════════════════════
#  MODULE 2 INPUT  (= Module 1 full output)
# ═════════════════════════════════════════════════════════════════════════════════

class RiskEngineRequest(BaseModel):
    """
    Accepts the complete Module 1 output JSON as input.
    Can be called directly via API or internally from the pipeline.
    """
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

    class Config:
        json_schema_extra = {
            "example": {
                "module": "M1_Clinical_Input",
                "version": "1.0",
                "generated_at": "2026-03-04T10:30:00Z",
                "case_id": "b1c2d3e4-f5a6-7890-bcde-fa1234567890",
                "patient_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
                "doctor_id": "d0c1b2a3-e4f5-6789-0abc-de1234567890",
                "demographics": {"age": 54, "gender": "Male", "weight_kg": 72.5},
                "medical_history": {
                    "systemic_conditions": ["Diabetes_Type2", "Hypertension"],
                    "allergies": ["Penicillin"],
                    "current_medications": ["Metformin 500mg"],
                    "bleeding_disorder": False,
                    "immunocompromised": False,
                    "smoking_status": "Current_Smoker",
                    "bisphosphonate_therapy": False,
                    "radiation_therapy_head_neck": False,
                },
                "chief_complaint": {
                    "description": "Pain in lower right molar for 3 days",
                    "symptoms": ["Toothache", "Swelling_Localized"],
                    "duration_days": 3,
                    "onset": "Gradual",
                },
                "clinical_assessment": {
                    "pain_level": 7,
                    "swelling_grade": "Moderate",
                    "fever": {"present": True, "temperature_celsius": 38.5},
                    "lymphadenopathy": True,
                    "tooth_mobility_grade": "Grade_1",
                    "percussion_test": "Positive_Severe",
                    "vitality_test": "Non_Vital",
                    "probing_depth_mm": 6.5,
                },
                "site_assessment": {
                    "tooth_site": "36",
                    "jaw_region": "Posterior_Mandible",
                    "bone_height_mm": 8.5,
                    "bone_width_mm": 6.0,
                    "bone_density": "D3",
                    "adjacent_teeth_status": "Healthy",
                    "nerve_proximity_mm": 3.5,
                },
                "clinical_notes": "Patient anxious. Previous failed RCT on #36.",
                "computed_flags": {
                    "urgency_flag": "Medium",
                    "bisphosphonate_risk": False,
                    "radiation_risk": False,
                    "age_contraindication": False,
                    "implant_data_present": True,
                },
                "validation_status": {"is_valid": True, "errors": [], "warnings": []},
            }
        }


# ═════════════════════════════════════════════════════════════════════════════════
#  MODULE 2 OUTPUT SUB-SCHEMAS
# ═════════════════════════════════════════════════════════════════════════════════

class RiskAlert(BaseModel):
    """A single risk alert raised by the engine."""
    rule_id: str = Field(..., description="Unique rule identifier, e.g. R-01")
    category: str = Field(..., description="Rule category: Bone, Systemic, Infection, Surgical")
    severity: AlertSeverity
    message: str = Field(..., description="Human-readable alert message")
    detail: Optional[str] = Field(None, description="Additional clinical context")


class SystemicRiskDetail(BaseModel):
    """Breakdown of systemic disease risk factors."""
    condition: str
    risk_contribution: str = Field(..., description="Low / Medium / High")
    note: str


class InfectionRiskDetail(BaseModel):
    """Infection pattern analysis."""
    pattern: str = Field(..., description="e.g. Acute_Localized, Chronic_Spreading")
    indicators: list[str] = Field(default_factory=list)
    spread_risk: str = Field(..., description="Low / Medium / High")


class BoneRiskDetail(BaseModel):
    """Bone adequacy assessment for implant feasibility."""
    bone_height_mm: Optional[float] = None
    bone_width_mm: Optional[float] = None
    bone_density: Optional[str] = None
    height_adequate: Optional[bool] = None
    width_adequate: Optional[bool] = None
    sinus_augmentation_needed: Optional[bool] = None
    nerve_proximity_concern: Optional[bool] = None


class SurgicalComplexityDetail(BaseModel):
    """Surgical complexity scoring breakdown."""
    score: int = Field(..., ge=0, le=100, description="0-100 complexity score")
    complexity_class: ComplexityClass
    factors: list[str] = Field(default_factory=list, description="Contributing factors")


class RiskSummary(BaseModel):
    """Top-level risk summary."""
    overall_risk_level: RiskLevel
    risk_score: int = Field(..., ge=0, le=100, description="Composite risk score 0-100")
    immediate_attention_required: bool
    implant_feasibility: ImplantFeasibility
    alert_count: int


# ═════════════════════════════════════════════════════════════════════════════════
#  MODULE 2 FULL OUTPUT
# ═════════════════════════════════════════════════════════════════════════════════

class Module2Output(BaseModel):
    """
    Complete Module 2 output JSON contract.
    Consumed by Module 3 (Diagnosis), Module 5 (Treatment), Module 6 (Explainability).
    """
    module: str = "M2_Risk_Engine"
    version: str = "1.0"
    generated_at: datetime
    case_id: UUID
    patient_id: UUID
    doctor_id: UUID

    # ── Summary ──────────────────────────────────────────────────────────────
    risk_summary: RiskSummary

    # ── Detailed Breakdowns ──────────────────────────────────────────────────
    alerts: list[RiskAlert] = Field(default_factory=list)
    bone_assessment: Optional[BoneRiskDetail] = None
    systemic_risks: list[SystemicRiskDetail] = Field(default_factory=list)
    infection_analysis: Optional[InfectionRiskDetail] = None
    surgical_complexity: Optional[SurgicalComplexityDetail] = None

    # ── Rule Trace (for Module 6 Explainability) ─────────────────────────────
    rules_evaluated: int = Field(0, description="Total rules checked")
    rules_triggered: int = Field(0, description="Rules that produced alerts")
    rule_trace: list[str] = Field(
        default_factory=list,
        description="Ordered list of rule IDs evaluated, for explainability",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "module": "M2_Risk_Engine",
                "version": "1.0",
                "generated_at": "2026-03-04T10:30:01Z",
                "case_id": "b1c2d3e4-f5a6-7890-bcde-fa1234567890",
                "patient_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
                "doctor_id": "d0c1b2a3-e4f5-6789-0abc-de1234567890",
                "risk_summary": {
                    "overall_risk_level": "High",
                    "risk_score": 72,
                    "immediate_attention_required": True,
                    "implant_feasibility": "Conditional",
                    "alert_count": 4,
                },
                "alerts": [
                    {
                        "rule_id": "R-01",
                        "category": "Bone",
                        "severity": "Warning",
                        "message": "Bone height 8.5mm < 10mm threshold",
                        "detail": "Sinus augmentation may be required for implant placement.",
                    }
                ],
            }
        }


# ═════════════════════════════════════════════════════════════════════════════════
#  API RESPONSE ENVELOPE
# ═════════════════════════════════════════════════════════════════════════════════

class RiskEngineResponse(BaseModel):
    """Success response wrapper for POST /api/risk-engine/assess"""
    status: str = "success"
    data: Module2Output
    message: str = "Risk assessment completed successfully."


class RiskEngineErrorResponse(BaseModel):
    """Error response wrapper"""
    status: str = "error"
    errors: list[dict]
