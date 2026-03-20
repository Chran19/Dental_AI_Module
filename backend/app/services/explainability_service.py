"""
Module 6 — Explainability Service
Generates human-readable explanations from rule traces and module outputs.
Uses template-based Natural Language Generation (NLG).
Reference: Module_6_Explainability_Audit_Layer.md §4
"""

import logging
from typing import Optional, List
from datetime import datetime
from uuid import uuid4

from app.schemas.clinical_input import Module1Output
from app.schemas.risk_engine import Module2Output
from app.schemas.diagnosis import Module3Output
from app.schemas.investigation import Module4Output
from app.schemas.treatment import Module5Output
from app.schemas.explainability import (
    ExplanationReport,
    AuditTrail,
    AuditTrailEntry,
    RuleTrace,
    DiagnosisScoreBreakdown,
)

logger = logging.getLogger(__name__)


class ExplainabilityService:
    """
    Generates natural language explanations and audit trails.
    Consumes outputs from all modules M1–M5 and produces human-readable report.
    """

    # Templates for NLG
    TEMPLATES = {
        "diagnosis_header": "Based on the clinical presentation, the leading diagnosis is {diagnosis_name} "
        "(confidence: {confidence}%).",
        "risk_alert": "Clinical Alert: {risk_name} detected. Severity: {severity}. "
        "Recommendation: {recommendation}",
        "treatment_recommend": "We recommend {treatment} because it is the standard protocol for {condition}.",
        "alternative_treatment": "Alternative: {treatment} may be considered if {condition}.",
        "contraindication": "⚠️ CAUTION: {treatment} is contraindicated due to {condition} ({severity}). "
        "{recommendation}",
        "imaging_rationale": "Imaging recommended: {imaging_list}. Rationale: {justification}",
        "labs_rationale": "Laboratory tests recommended: {lab_list}. Rationale: {justification}",
        "summary_closing": "This case requires prompt {urgency} attention. "
        "Follow-up recommended in {followup_days} days.",
    }

    @staticmethod
    def generate_explanation(
        m1_output: Optional[Module1Output] = None,
        m2_output: Optional[Module2Output] = None,
        m3_output: Optional[Module3Output] = None,
        m4_output: Optional[Module4Output] = None,
        m5_output: Optional[Module5Output] = None,
    ) -> ExplanationReport:
        """
        Generate comprehensive human-readable explanation from module outputs.

        Args:
            m1_output: Clinical input data
            m2_output: Risk assessment results
            m3_output: Differential diagnosis results
            m4_output: Investigation recommendations
            m5_output: Treatment suggestions

        Returns:
            ExplanationReport with narrative, traces, and clinical summary
        """
        case_id = str(uuid4())

        # Initialize components
        summary_lines = []
        m2_traces = []
        m3_breakdown = []
        contraindication_warnings = []
        m4_imaging_text = ""
        m5_treatment_text = ""

        # ─────────────────────────────────────────────────────────────────────────
        # M3: Diagnosis explanation (primary focus)
        # ─────────────────────────────────────────────────────────────────────────

        if m3_output and hasattr(m3_output, "differentials") and m3_output.differentials:
            top_dx = m3_output.differentials[0]

            # Main diagnosis statement
            summary_lines.append(
                ExplainabilityService.TEMPLATES["diagnosis_header"].format(
                    diagnosis_name=top_dx.name,
                    confidence=int(top_dx.confidence_pct),
                )
            )

            # Build diagnosis scoring breakdown
            for dx in m3_output.differentials[:3]:  # Top 3
                contributing = []

                m3_breakdown.append(
                    DiagnosisScoreBreakdown(
                        diagnosis_code=dx.code,
                        diagnosis_name=dx.name,
                        raw_score=getattr(dx, "raw_score", 0.0),
                        weighted_score=dx.confidence_pct,
                        contributing_factors=contributing,
                        confidence=dx.confidence_pct,
                    )
                )

        # ─────────────────────────────────────────────────────────────────────────
        # M2: Risk alerts
        # ─────────────────────────────────────────────────────────────────────────

        if m2_output and hasattr(m2_output, "alerts") and m2_output.alerts:
            risk_statements = []
            for risk in m2_output.alerts[:2]:  # Top 2 risks
                risk_text = ExplainabilityService.TEMPLATES["risk_alert"].format(
                    risk_name=risk.message,
                    severity=risk.severity.value,
                    recommendation=risk.detail or "Refer to specialist",
                )
                risk_statements.append(risk_text)

                # Add as rule trace
                m2_traces.append(
                    RuleTrace(
                        rule_id=risk.rule_id,
                        rule_name=risk.message,
                        inputs={"symptoms": getattr(m1_output, "symptoms", [])},
                        conditions_met=True,
                        firing_score=None,
                        output=risk.detail or risk.message,
                    )
                )

            if risk_statements:
                summary_lines.append(" ".join(risk_statements))

        # ─────────────────────────────────────────────────────────────────────────
        # M4: Investigation recommendations
        # ─────────────────────────────────────────────────────────────────────────

        if m4_output:
            imaging_types = []
            lab_types = []

            if hasattr(m4_output, "imaging_recommendations"):
                imaging_types = [r.imaging_type for r in m4_output.imaging_recommendations]

            if hasattr(m4_output, "lab_recommendations"):
                lab_types = [r.test_type for r in m4_output.lab_recommendations]

            if imaging_types or lab_types:
                imaging_str = ", ".join(str(img) for img in imaging_types) if imaging_types else "None"
                labs_str = ", ".join(str(lab) for lab in lab_types) if lab_types else "None"

                m4_text = ""
                if imaging_types:
                    m4_text += ExplainabilityService.TEMPLATES["imaging_rationale"].format(
                        imaging_list=imaging_str,
                        justification=getattr(m4_output, "summary", "Clinical assessment"),
                    )
                if lab_types:
                    m4_text += " " + ExplainabilityService.TEMPLATES["labs_rationale"].format(
                        lab_list=labs_str,
                        justification="Systemic status evaluation",
                    )

                m4_imaging_text = m4_text

        # ─────────────────────────────────────────────────────────────────────────
        # M5: Treatment recommendations & contraindications
        # ─────────────────────────────────────────────────────────────────────────

        if m5_output:
            if hasattr(m5_output, "primary_treatment") and m5_output.primary_treatment:
                primary = m5_output.primary_treatment
                top_dx_name = top_dx.name if m3_output and hasattr(m3_output, "differentials") and m3_output.differentials else "the clinical diagnosis"
                m5_treatment_text = ExplainabilityService.TEMPLATES["treatment_recommend"].format(
                    treatment=primary.treatment_type.value,
                    condition=top_dx_name,
                )

            # Contraindications
            if hasattr(m5_output, "contraindication_alerts") and m5_output.contraindication_alerts:
                for contra in m5_output.contraindication_alerts:
                    warning = ExplainabilityService.TEMPLATES["contraindication"].format(
                        treatment=contra.treatment_type.value,
                        condition=contra.conflicting_condition,
                        severity=contra.severity.value,
                        recommendation=contra.clinical_recommendation,
                    )
                    contraindication_warnings.append(warning)

        # ─────────────────────────────────────────────────────────────────────────
        # Assemble final narrative
        # ─────────────────────────────────────────────────────────────────────────

        full_summary = " ".join(summary_lines)
        if m4_imaging_text:
            full_summary += " " + m4_imaging_text
        if m5_treatment_text:
            full_summary += " " + m5_treatment_text
        if contraindication_warnings:
            full_summary += " " + " ".join(contraindication_warnings)

        # Clinical summary for clinician
        clinical_summary = ExplainabilityService._build_clinical_summary(
            m1_output, m3_output, m5_output
        )

        return ExplanationReport(
            case_id=case_id,
            summary=full_summary if full_summary else "Case analysis incomplete.",
            m2_rules_triggered=m2_traces,
            m3_scoring_trace=m3_breakdown,
            m4_imaging_justification=m4_imaging_text,
            m5_treatment_justification=m5_treatment_text,
            m5_contraindication_warnings=contraindication_warnings,
            clinical_summary=clinical_summary,
            evidence_references=[
                "Endodontic diagnostic guidelines (AAE 2013)",
                "Radiographic interpretation standards",
            ],
            module_versions={
                "M1": "1.0",
                "M2": "1.0",
                "M3": "1.0",
                "M4": "1.0",
                "M5": "1.0",
                "M6": "1.0",
            },
        )

    @staticmethod
    def _build_clinical_summary(
        m1_output: Optional[Module1Output],
        m3_output: Optional[Module3Output],
        m5_output: Optional[Module5Output],
    ) -> str:
        """Build human-friendly clinical narrative."""
        lines = []

        # Patient demographics
        if m1_output:
            age_str = f"{m1_output.age} years old" if hasattr(m1_output, "age") else "Patient"
            gender_str = (
                f"{m1_output.gender.value}" if hasattr(m1_output, "gender") else "unknown gender"
            )
            lines.append(f"Patient: {age_str}, {gender_str}.")

            if hasattr(m1_output, "chief_complaint"):
                lines.append(f"Chief complaint: {m1_output.chief_complaint}.")

        # Diagnosis
        if m3_output and hasattr(m3_output, "differentials") and m3_output.differentials:
            top_dx = m3_output.differentials[0]
            lines.append(
                f"Primary diagnosis: {top_dx.name} "
                f"({int(top_dx.confidence_pct)}% confidence)."
            )

        # Treatment plan
        if m5_output and hasattr(m5_output, "primary_treatment"):
            treatment = m5_output.primary_treatment
            followup = getattr(treatment, "follow_up_days", 7)
            lines.append(
                f"Recommended treatment: {treatment.treatment_type.value}. "
                f"Follow-up in {followup} days."
            )

        return " ".join(lines) if lines else "Case analysis in progress."

    @staticmethod
    def build_audit_trail(m1_id: str, m2_id: str, m3_id: str) -> AuditTrail:
        """
        Build audit trail from case IDs.
        In production, would retrieve from database.
        """
        entries = [
            AuditTrailEntry(
                timestamp=datetime.utcnow(),
                module_name="M1",
                action_type="Clinical_Input_Processed",
                detail="Patient clinical data captured and validated.",
                metadata={"case_id": m1_id},
            ),
            AuditTrailEntry(
                timestamp=datetime.utcnow(),
                module_name="M2",
                action_type="Risk_Assessment_Completed",
                detail="Risk factors evaluated against systemic history.",
                metadata={"case_id": m2_id},
            ),
            AuditTrailEntry(
                timestamp=datetime.utcnow(),
                module_name="M3",
                action_type="Diagnosis_Generated",
                detail="Differential diagnosis computed via rule engine.",
                metadata={"case_id": m3_id},
            ),
        ]

        return AuditTrail(case_id=str(uuid4()), entries=entries)
