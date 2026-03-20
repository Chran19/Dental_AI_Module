"""
Module 6 — Explainability & Audit Schemas
Provides human-readable explanations and audit trails for all AI decisions.
Reference: Module_6_Explainability_Audit_Layer.md
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from app.models.enums import UrgencyFlag
from datetime import datetime


class RuleTrace(BaseModel):
    """Record of a single rule firing during analysis"""
    rule_id: str = Field(..., description="e.g., 'R-01', 'DX-01', 'I-03'")
    rule_name: str = Field(..., description="Human-readable rule name")
    inputs: Dict = Field(default_factory=dict, description="Input data to the rule")
    conditions_met: bool = Field(..., description="Whether rule fired")
    firing_score: Optional[float] = Field(None, description="Confidence score if applicable")
    output: Optional[str] = Field(None, description="Result of rule firing")


class DiagnosisScoreBreakdown(BaseModel):
    """Breakdown of how each diagnosis was scored"""
    diagnosis_code: str
    diagnosis_name: str
    raw_score: float
    weighted_score: float
    contributing_factors: List[str]
    confidence: float


class ExplanationReport(BaseModel):
    """
    Comprehensive human-readable explanation of the AI decision.
    Suitable for display to clinician.
    """
    case_id: str = Field(..., description="Unique case identifier")
    summary: str = Field(..., description="1-2 sentence executive summary")

    # Traces from each module
    m2_rules_triggered: List[RuleTrace] = Field(
        default_factory=list,
        description="Risk rules from M2 that fired"
    )
    m3_scoring_trace: List[DiagnosisScoreBreakdown] = Field(
        default_factory=list,
        description="Diagnosis scoring breakdown from M3"
    )
    m4_imaging_justification: str = Field(
        default="",
        description="Why specific imaging recommended"
    )
    m5_treatment_justification: str = Field(
        default="",
        description="Why specific treatment recommended"
    )
    m5_contraindication_warnings: List[str] = Field(
        default_factory=list,
        description="Any warnings about contraindications"
    )

    # Clinical summary for dentist
    clinical_summary: str = Field(
        ...,
        description="Narrative clinical summary in plain English"
    )

    # Evidence citations
    evidence_references: List[str] = Field(
        default_factory=list,
        description="Citations to clinical evidence or guidelines"
    )

    # Generated explanation metadata
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    module_versions: Dict[str, str] = Field(
        default_factory=dict,
        description="Module versions used (M1, M2, etc.)"
    )


class AuditTrailEntry(BaseModel):
    """Single entry in the audit trail"""
    timestamp: datetime
    module_name: str = Field(..., description="e.g., 'M1', 'M2', 'M3'")
    action_type: str = Field(..., description="e.g., 'Clinical_Input_Processed', 'Diagnosis_Generated'")
    detail: str = Field(default="", description="Human-readable detail")
    metadata: Dict = Field(default_factory=dict, description="Additional structured data")


class AuditTrail(BaseModel):
    """Complete audit trail for a case"""
    case_id: str
    entries: List[AuditTrailEntry] = Field(default_factory=list)
    summary: str = Field(default="", description="High-level summary of case flow")
