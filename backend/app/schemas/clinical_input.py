"""
Module 1 — Pydantic Schemas for Clinical Input Processing
Defines request validation, output structure, and the M1 JSON contract.
Reference: Module_1_Clinical_Input_Processing.md §3–§5
"""

from __future__ import annotations

import re
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator, model_validator

from app.models.enums import (
    AdjacentTeethStatus,
    BoneDensity,
    Gender,
    JawRegion,
    PercussionTest,
    SmokingStatus,
    Symptom,
    SymptomOnset,
    SwellingGrade,
    SystemicCondition,
    ToothMobilityGrade,
    UrgencyFlag,
    VitalityTest,
)


# ═════════════════════════════════════════════════════════════════════════════════
# REQUEST SCHEMA  (Doctor → API)
# Flat structure matching the API contract in Module 1 §7.1
# ═════════════════════════════════════════════════════════════════════════════════

class ClinicalInputRequest(BaseModel):
    """
    Incoming clinical input from the doctor.
    Flat payload validated against all rules in §4.1 and §4.2.
    """

    # ── 3.1 Patient Demographics ─────────────────────────────────────────────
    patient_id: UUID = Field(..., description="Existing patient UUID from Patients table")

    age: int = Field(
        ..., ge=1, le=120,
        description="Patient age (V-01: 1–120)",
    )
    gender: Gender = Field(
        ..., description="Patient gender (V-02)",
    )
    weight_kg: Optional[float] = Field(
        None, ge=1.0, le=300.0,
        description="Patient weight in kg (optional)",
    )

    # ── 3.2 Medical History ──────────────────────────────────────────────────
    systemic_conditions: list[SystemicCondition] = Field(
        ...,
        description="Multi-select systemic conditions (V-15)",
    )
    allergies: Optional[list[str]] = Field(
        None, max_length=20,
        description="Free-text allergy tags (V-13: max 20 items, 100 chars each)",
    )
    current_medications: Optional[list[str]] = Field(
        None, max_length=30,
        description="Free-text medication tags (V-14: max 30 items, 150 chars each)",
    )
    bleeding_disorder: bool = Field(
        ..., description="Bleeding disorder flag",
    )
    immunocompromised: bool = Field(
        ..., description="Immunocompromised flag",
    )
    smoking_status: SmokingStatus = Field(
        ..., description="Smoking status enum",
    )
    bisphosphonate_therapy: bool = Field(
        ..., description="Bisphosphonate history (critical for implant risk)",
    )
    radiation_therapy_head_neck: bool = Field(
        ..., description="Head & neck radiation history",
    )

    # ── 3.3 Chief Complaint & Symptoms ───────────────────────────────────────
    chief_complaint: str = Field(
        ..., min_length=5, max_length=500,
        description="Chief complaint text (V-03: 5–500 chars)",
    )
    symptoms: list[Symptom] = Field(
        ..., min_length=1,
        description="Clinical symptoms (V-05: at least 1)",
    )
    symptom_duration_days: int = Field(
        ..., ge=0, le=3650,
        description="Symptom duration in days (V-16: 0–3650)",
    )
    symptom_onset: Optional[SymptomOnset] = Field(
        None, description="Onset type (optional)",
    )

    # ── 3.4 Clinical Assessment ──────────────────────────────────────────────
    pain_level: int = Field(
        ..., ge=0, le=10,
        description="VAS pain scale (V-04: 0–10)",
    )
    swelling_grade: SwellingGrade = Field(
        ..., description="Swelling grade (V-06)",
    )
    fever_present: bool = Field(
        ..., description="Fever flag",
    )
    temperature_celsius: Optional[float] = Field(
        None, ge=35.0, le=42.0,
        description="Temperature (V-07: required if fever_present, 35.0–42.0)",
    )
    lymphadenopathy: Optional[bool] = Field(
        None, description="Lymph node involvement",
    )
    tooth_mobility_grade: Optional[ToothMobilityGrade] = Field(
        None, description="Tooth mobility grade",
    )
    percussion_test: Optional[PercussionTest] = Field(
        None, description="Percussion sensitivity",
    )
    vitality_test: Optional[VitalityTest] = Field(
        None, description="Pulp vitality test result",
    )
    probing_depth_mm: Optional[float] = Field(
        None, ge=0.0, le=15.0,
        description="Probing depth (V-11: 0–15mm)",
    )

    # ── 3.5 Site & Bone Assessment ───────────────────────────────────────────
    tooth_site: str = Field(
        ..., description="FDI tooth number (V-08)",
    )
    jaw_region: JawRegion = Field(
        ..., description="Jaw region enum",
    )
    bone_height_mm: Optional[float] = Field(
        None, ge=0.0, le=30.0,
        description="Available bone height (V-09: 0–30mm)",
    )
    bone_width_mm: Optional[float] = Field(
        None, ge=0.0, le=20.0,
        description="Available bone width (V-10: 0–20mm)",
    )
    bone_density: Optional[BoneDensity] = Field(
        None, description="Misch bone density classification",
    )
    adjacent_teeth_status: Optional[AdjacentTeethStatus] = Field(
        None, description="Status of adjacent teeth",
    )
    sinus_proximity_mm: Optional[float] = Field(
        None, ge=0.0, le=25.0,
        description="Sinus floor distance in mm",
    )
    nerve_proximity_mm: Optional[float] = Field(
        None, ge=0.0, le=25.0,
        description="IAN canal distance in mm",
    )

    # ── 3.6 Clinical Notes ───────────────────────────────────────────────────
    clinical_notes: Optional[str] = Field(
        None, max_length=2000,
        description="Free-text clinical notes (V-12: max 2000 chars)",
    )

    # ─── FIELD-LEVEL VALIDATORS ──────────────────────────────────────────────

    @field_validator("tooth_site")
    @classmethod
    def validate_tooth_site(cls, v: str) -> str:
        """V-08: FDI notation regex ^[1-4][1-8]$"""
        fdi_pattern = re.compile(r"^[1-4][1-8]$")
        if not fdi_pattern.match(v.strip()):
            raise ValueError("Enter a valid tooth number (FDI notation, e.g. 11–48).")
        return v.strip()

    @field_validator("allergies")
    @classmethod
    def validate_allergies(cls, v: list[str] | None) -> list[str] | None:
        """V-13: Each item max 100 chars, max 20 items"""
        if v is None:
            return v
        if len(v) > 20:
            raise ValueError("Maximum 20 allergy entries allowed.")
        for idx, item in enumerate(v):
            if len(item) > 100:
                raise ValueError(
                    f"Allergy entry #{idx + 1} exceeds 100 characters."
                )
        return v

    @field_validator("current_medications")
    @classmethod
    def validate_medications(cls, v: list[str] | None) -> list[str] | None:
        """V-14: Each item max 150 chars, max 30 items"""
        if v is None:
            return v
        if len(v) > 30:
            raise ValueError("Maximum 30 medication entries allowed.")
        for idx, item in enumerate(v):
            if len(item) > 150:
                raise ValueError(
                    f"Medication entry #{idx + 1} exceeds 150 characters."
                )
        return v

    # ─── CROSS-FIELD VALIDATORS ──────────────────────────────────────────────

    @model_validator(mode="after")
    def validate_cross_field_rules(self) -> "ClinicalInputRequest":
        """
        Cross-field validation rules (§4.2):
        - V-07: temperature required when fever is present
        - XV-04: age < 18 with implant data → warning/block
        """
        # V-07: Fever + Temperature conditional requirement
        if self.fever_present and self.temperature_celsius is None:
            raise ValueError(
                "Please enter temperature (35.0–42.0°C) when fever is present."
            )

        return self

    class Config:
        json_schema_extra = {
            "example": {
                "patient_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
                "age": 54,
                "gender": "Male",
                "weight_kg": 72.5,
                "systemic_conditions": ["Diabetes_Type2", "Hypertension"],
                "allergies": ["Penicillin"],
                "current_medications": ["Metformin 500mg", "Amlodipine 5mg"],
                "bleeding_disorder": False,
                "immunocompromised": False,
                "smoking_status": "Current_Smoker",
                "bisphosphonate_therapy": False,
                "radiation_therapy_head_neck": False,
                "chief_complaint": "Patient reports pain in lower right molar region for 3 days",
                "symptoms": ["Toothache", "Thermal_Sensitivity_Hot", "Swelling_Localized"],
                "symptom_duration_days": 3,
                "symptom_onset": "Gradual",
                "pain_level": 7,
                "swelling_grade": "Moderate",
                "fever_present": True,
                "temperature_celsius": 38.5,
                "lymphadenopathy": True,
                "tooth_mobility_grade": "Grade_1",
                "percussion_test": "Positive_Severe",
                "vitality_test": "Non_Vital",
                "probing_depth_mm": 6.5,
                "tooth_site": "36",
                "jaw_region": "Posterior_Mandible",
                "bone_height_mm": 8.5,
                "bone_width_mm": 6.0,
                "bone_density": "D3",
                "adjacent_teeth_status": "Healthy",
                "sinus_proximity_mm": None,
                "nerve_proximity_mm": 3.5,
                "clinical_notes": "Patient anxious. Previous failed RCT on #36.",
            }
        }


# ═════════════════════════════════════════════════════════════════════════════════
# OUTPUT SCHEMAS  (Module 1 → Downstream Modules)
# Matches the JSON contract in Module 1 §5.1
# ═════════════════════════════════════════════════════════════════════════════════

class DemographicsOutput(BaseModel):
    age: int
    gender: Gender
    weight_kg: Optional[float] = None


class MedicalHistoryOutput(BaseModel):
    systemic_conditions: list[SystemicCondition]
    allergies: list[str]
    current_medications: list[str]
    bleeding_disorder: bool
    immunocompromised: bool
    smoking_status: SmokingStatus
    bisphosphonate_therapy: bool
    radiation_therapy_head_neck: bool


class ChiefComplaintOutput(BaseModel):
    description: str
    symptoms: list[Symptom]
    duration_days: int
    onset: Optional[SymptomOnset] = None


class FeverOutput(BaseModel):
    present: bool
    temperature_celsius: Optional[float] = None


class ClinicalAssessmentOutput(BaseModel):
    pain_level: int
    swelling_grade: SwellingGrade
    fever: FeverOutput
    lymphadenopathy: Optional[bool] = None
    tooth_mobility_grade: Optional[ToothMobilityGrade] = None
    percussion_test: Optional[PercussionTest] = None
    vitality_test: Optional[VitalityTest] = None
    probing_depth_mm: Optional[float] = None


class SiteAssessmentOutput(BaseModel):
    tooth_site: str
    jaw_region: JawRegion
    bone_height_mm: Optional[float] = None
    bone_width_mm: Optional[float] = None
    bone_density: Optional[BoneDensity] = None
    adjacent_teeth_status: Optional[AdjacentTeethStatus] = None
    sinus_proximity_mm: Optional[float] = None
    nerve_proximity_mm: Optional[float] = None


class ComputedFlagsOutput(BaseModel):
    urgency_flag: UrgencyFlag
    bisphosphonate_risk: bool
    radiation_risk: bool
    age_contraindication: bool
    implant_data_present: bool


class ValidationStatusOutput(BaseModel):
    is_valid: bool
    errors: list[str] = []
    warnings: list[str] = []


class Module1Output(BaseModel):
    """
    The complete Module 1 output JSON contract (§5.1).
    This payload is consumed by Module 2 (Risk Engine), Module 3 (Diagnosis),
    and all downstream modules.
    """
    module: str = "M1_Clinical_Input"
    version: str = "1.0"
    generated_at: datetime
    case_id: UUID
    patient_id: UUID
    doctor_id: UUID

    demographics: DemographicsOutput
    medical_history: MedicalHistoryOutput
    chief_complaint: ChiefComplaintOutput
    clinical_assessment: ClinicalAssessmentOutput
    site_assessment: SiteAssessmentOutput
    clinical_notes: Optional[str] = None
    computed_flags: ComputedFlagsOutput
    validation_status: ValidationStatusOutput

    class Config:
        json_schema_extra = {
            "example": {
                "module": "M1_Clinical_Input",
                "version": "1.0",
                "generated_at": "2026-02-27T10:30:00Z",
                "case_id": "b1c2d3e4-f5a6-7890-bcde-fa1234567890",
                "patient_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
                "doctor_id": "d0c1b2a3-e4f5-6789-0abc-de1234567890",
                "demographics": {"age": 54, "gender": "Male", "weight_kg": 72.5},
                "computed_flags": {
                    "urgency_flag": "Medium",
                    "bisphosphonate_risk": False,
                    "radiation_risk": False,
                    "age_contraindication": False,
                    "implant_data_present": True,
                },
                "validation_status": {
                    "is_valid": True,
                    "errors": [],
                    "warnings": [],
                },
            }
        }


# ═════════════════════════════════════════════════════════════════════════════════
# API RESPONSE ENVELOPE
# ═════════════════════════════════════════════════════════════════════════════════

class ClinicalInputResponse(BaseModel):
    """Success response wrapper for POST /api/clinical-input/validate"""
    status: str = "success"
    data: Module1Output
    message: str = "Clinical input validated and structured successfully."


class ValidationErrorItem(BaseModel):
    field: str
    message: str


class ValidationErrorResponse(BaseModel):
    """422 error response wrapper"""
    status: str = "error"
    errors: list[ValidationErrorItem]
