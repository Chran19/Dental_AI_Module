"""
Module 4 — Investigation Service
Deterministic investigation recommendation engine that matches diagnosis codes
to investigation profiles and applies risk-based amplification.

Pipeline:
  1. Extract diagnosis code from M3 output
  2. Look up investigation profiles
  3. Apply M2 risk amplification (e.g., bone loss → CBCT)
  4. Generate imaging/lab recommendations with urgency levels
  5. Build justifications and return Module 4 output
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import Optional

from app.models.enums import ImagingType, InvestigationUrgency, LabTestType
from app.schemas.investigation import (
    ImagingRecommendation,
    InvestigationRequest,
    InvestigationSummary,
    LabTestRecommendation,
    Module4Output,
)
from app.services.investigation_profiles import INVESTIGATION_PROFILES

logger = logging.getLogger(__name__)


# ═════════════════════════════════════════════════════════════════════════════════
#  RISK AMPLIFICATION RULES
# ═════════════════════════════════════════════════════════════════════════════════

RISK_AMPLIFICATION_RULES = {
    # If M2 detects high bone loss risk, add 3D imaging to standard 2D
    "High_Bone_Loss": {
        "add_imaging": [ImagingType.CBCT],
        "amplify_urgency": InvestigationUrgency.URGENT,
        "reason": "High bone loss detected; 3D imaging recommended for implant planning",
    },
    # If fever/systemic infection, amplify urgency of labs
    "Systemic_Infection": {
        "add_labs": [LabTestType.WBC, LabTestType.CRP],
        "amplify_urgency": InvestigationUrgency.EMERGENCY,
        "reason": "Systemic infection detected; urgent lab work required",
    },
    # If immunocompromised, add specific labs
    "Immunocompromised": {
        "add_labs": [LabTestType.CBC, LabTestType.WBC],
        "amplify_urgency": InvestigationUrgency.URGENT,
        "reason": "Immunocompromised status; baseline hematology required",
    },
}


class InvestigationService:
    """
    Module 4 — Investigation Recommendation Service.

    Accepts diagnosis information and optional M2 risk data.
    Returns ranked investigation recommendations with urgency levels.
    """

    @staticmethod
    def recommend(req: InvestigationRequest) -> Module4Output:
        """
        Generate investigation recommendations from diagnosis and risk profile.

        Args:
            req: InvestigationRequest containing diagnosis code and risk data

        Returns:
            Module4Output with ranking imaging/lab recommendations

        Raises:
            ValueError: If diagnosis code not found in profiles
        """
        try:
            case_id = req.case_id
            diagnosis_code = req.top_diagnosis_code
            diagnosis_name = req.top_diagnosis_name

            # Fetch investigation profile for this diagnosis
            profile = INVESTIGATION_PROFILES.get(diagnosis_code)
            if not profile:
                logger.warning(
                    "M4 | No investigation profile for %s; using minimal investigations",
                    diagnosis_code,
                )
                imaging_recs, lab_recs, max_urgency = [], [], InvestigationUrgency.ROUTINE
                reasoning = [
                    f"Diagnosis code {diagnosis_code} not found in investigation profiles.",
                    "Recommending minimal investigations pending diagnostic confirmation.",
                ]
            else:
                # Build imaging recommendations
                imaging_recs = [
                    ImagingRecommendation(
                        imaging_type=img,
                        justification=profile.get("justification", ""),
                        urgency=profile.get("urgency", InvestigationUrgency.ROUTINE),
                    )
                    for img in profile.get("imaging", [])
                ]

                # Build lab recommendations
                lab_recs = [
                    LabTestRecommendation(
                        test_type=lab,
                        justification=profile.get("justification", ""),
                        urgency=profile.get("urgency", InvestigationUrgency.ROUTINE),
                    )
                    for lab in profile.get("labs", [])
                ]

                # Determine max urgency from profile
                max_urgency = profile.get("urgency", InvestigationUrgency.ROUTINE)

                reasoning = [
                    f"Diagnosis: {diagnosis_name} ({diagnosis_code})",
                    f"Base investigation profile: {len(imaging_recs)} imaging, {len(lab_recs)} labs",
                ]

            # Apply risk amplification from M2 data
            if req.risk_factors:
                imaging_recs, lab_recs, max_urgency = (
                    InvestigationService._apply_risk_amplification(
                        imaging_recs,
                        lab_recs,
                        req.risk_factors,
                        max_urgency,
                        reasoning,
                    )
                )

            # Remove duplicates while preserving order
            imaging_recs = list(
                {(r.imaging_type.value if hasattr(r.imaging_type, 'value') else str(r.imaging_type)): r 
                 for r in imaging_recs}.values()
            )
            lab_recs = list(
                {(r.test_type.value if hasattr(r.test_type, 'value') else str(r.test_type)): r 
                 for r in lab_recs}.values()
            )

            # Build summary
            summary = InvestigationSummary(
                total_imaging_count=len(imaging_recs),
                total_lab_count=len(lab_recs),
                overall_urgency=max_urgency,
                summary_text=f"Based on {diagnosis_name}: recommend {len(imaging_recs)} imaging modalities and {len(lab_recs)} lab tests (Urgency: {max_urgency.value}).",
            )

            reasoning.append(
                f"Final recommendations: {len(imaging_recs)} imaging, {len(lab_recs)} labs, Overall Urgency: {max_urgency.value}"
            )

            # Build and return Module 4 output
            output = Module4Output(
                case_id=case_id,
                patient_id=req.patient_id,
                doctor_id=req.doctor_id,
                imaging_recommendations=imaging_recs,
                lab_recommendations=lab_recs,
                summary=summary,
                referenced_diagnosis_code=diagnosis_code,
                reasoning_chain=reasoning,
            )

            logger.info(
                "M4 investigation | case_id=%s diagnosis=%s imaging=%d labs=%d urgency=%s",
                case_id,
                diagnosis_code,
                len(imaging_recs),
                len(lab_recs),
                max_urgency.value,
            )

            return output

        except Exception as e:
            logger.error("M4 investigation service error: %s", str(e), exc_info=True)
            raise

    @staticmethod
    def _apply_risk_amplification(
        imaging_recs: list[ImagingRecommendation],
        lab_recs: list[LabTestRecommendation],
        risk_factors: list[str],
        current_max_urgency: InvestigationUrgency,
        reasoning: list[str],
    ) -> tuple[list[ImagingRecommendation], list[LabTestRecommendation], InvestigationUrgency]:
        """
        Apply M2 risk amplification logic to investigation recommendations.

        Adjusts urgency and adds additional investigations based on M2 risk factors.

        Args:
            imaging_recs: Current imaging recommendations
            lab_recs: Current lab recommendations
            risk_factors: List of risk factor codes from M2
            current_max_urgency: Current maximum urgency level
            reasoning: Reasoning chain to append to

        Returns:
            Tuple of (updated imaging_recs, updated lab_recs, updated max_urgency)
        """
        max_urgency = current_max_urgency

        for risk_code in risk_factors:
            rule = RISK_AMPLIFICATION_RULES.get(risk_code)
            if not rule:
                continue

            reasoning.append(
                f"Risk amplification: {risk_code} — {rule.get('reason', 'Amplifying urgency')}"
            )

            # Add imaging based on risk
            for img_type in rule.get("add_imaging", []):
                if not any(
                    r.imaging_type == img_type for r in imaging_recs
                ):
                    imaging_recs.append(
                        ImagingRecommendation(
                            imaging_type=img_type,
                            justification=rule.get("reason", ""),
                            urgency=rule.get("amplify_urgency", InvestigationUrgency.URGENT),
                        )
                    )

            # Add labs based on risk
            for lab_type in rule.get("add_labs", []):
                if not any(r.test_type == lab_type for r in lab_recs):
                    lab_recs.append(
                        LabTestRecommendation(
                            test_type=lab_type,
                            justification=rule.get("reason", ""),
                            urgency=rule.get("amplify_urgency", InvestigationUrgency.URGENT),
                        )
                    )

            # Update max urgency
            amplified_urgency = rule.get("amplify_urgency", InvestigationUrgency.ROUTINE)
            if InvestigationService._urgency_rank(amplified_urgency) > InvestigationService._urgency_rank(
                max_urgency
            ):
                max_urgency = amplified_urgency

        return imaging_recs, lab_recs, max_urgency

    @staticmethod
    def _urgency_rank(urgency: InvestigationUrgency) -> int:
        """
        Convert urgency level to numeric rank for comparison.

        Returns:
            Higher number = higher urgency
        """
        rank_map = {
            InvestigationUrgency.ROUTINE: 1,
            InvestigationUrgency.URGENT: 2,
            InvestigationUrgency.EMERGENCY: 3,
        }
        return rank_map.get(urgency, 0)
