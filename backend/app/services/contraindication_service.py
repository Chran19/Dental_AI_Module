"""
Module 5 — Contraindication Service
Checks treatment options against patient medical history for conflicts.
Identifies situations where certain treatments should be avoided or modified.

Examples:
    - Bisphosphonates + Extraction → High osteonecrosis risk
    - Blood disorder + Extraction → High bleeding risk
    - Active infection + Implant → Contraindicated
    - Radiation history + Surgery → Complex healing
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Optional

from app.models.enums import (
    ContraindicationSeverity,
    SystemicCondition,
    TreatmentType,
)

logger = logging.getLogger(__name__)


# ═════════════════════════════════════════════════════════════════════════════════
#  DATA STRUCTURES
# ═════════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class Contraindication:
    """
    A single contraindication for a treatment.
    """

    treatment_type: TreatmentType
    conflicting_condition: str  # e.g., "Bisphosphonate therapy", "Active infection"
    severity: ContraindicationSeverity
    clinical_recommendation: str  # What to do instead


# ═════════════════════════════════════════════════════════════════════════════════
#  CONTRAINDICATION MATRIX
#  Maps (SystemicCondition, TreatmentType) → (Severity, Recommendation)
# ═════════════════════════════════════════════════════════════════════════════════

CONTRAINDICATION_MATRIX = {
    # ─────────────────────────────────────────────────────────────────────────────
    # EXTRACTION-RELATED CONTRAINDICATIONS
    # ─────────────────────────────────────────────────────────────────────────────

    (SystemicCondition.BLOOD_DISORDER, TreatmentType.EXTRACTION): (
        ContraindicationSeverity.SEVERE,
        "Contact hematologist for coagulation assessment before extraction. "
        "May require FFP or transfusion. Consider conservative management.",
    ),

    (SystemicCondition.OSTEOPOROSIS, TreatmentType.EXTRACTION): (
        ContraindicationSeverity.SEVERE,
        "High risk of alveolar bone resorption. Use bone-sparing techniques. "
        "Consider preservation with root canal instead.",
    ),

    (SystemicCondition.DIABETES_TYPE2, TreatmentType.EXTRACTION): (
        ContraindicationSeverity.MODERATE,
        "Increased healing time and infection risk. Optimize diabetes control first. "
        "Close monitoring recommended.",
    ),

    # ─────────────────────────────────────────────────────────────────────────────
    # IMPLANT-RELATED CONTRAINDICATIONS
    # ─────────────────────────────────────────────────────────────────────────────

    (SystemicCondition.DIABETES_TYPE2, TreatmentType.IMPLANT_PLACEMENT): (
        ContraindicationSeverity.SEVERE,
        "Poor osseointegration and implant failure risk. Optimize HbA1c <7% first. "
        "Defer implant placement until control achieved.",
    ),

    # ─────────────────────────────────────────────────────────────────────────────
    # ANTIBIOTIC-RELATED CONTRAINDICATIONS
    # ─────────────────────────────────────────────────────────────────────────────

    (SystemicCondition.KIDNEY_DISEASE, TreatmentType.ANTIBIOTICS): (
        ContraindicationSeverity.MODERATE,
        "Adjust antibiotic selection and dosing based on GFR. "
        "Consider nephrology consultation.",
    ),

    (SystemicCondition.LIVER_DISEASE, TreatmentType.ANTIBIOTICS): (
        ContraindicationSeverity.MODERATE,
        "Avoid hepatotoxic antibiotics. Monitor liver function. "
        "Consider alternatives like clindamycin.",
    ),

    # ─────────────────────────────────────────────────────────────────────────────
    # SURGICAL PROCEDURE CONTRAINDICATIONS
    # ─────────────────────────────────────────────────────────────────────────────

    (SystemicCondition.HYPERTENSION, TreatmentType.PERIODONTAL_SURGERY): (
        ContraindicationSeverity.MODERATE,
        "Increased bleeding risk. Optimize BP control first. "
        "Consider rescheduling.",
    ),

    (SystemicCondition.BLOOD_DISORDER, TreatmentType.PERIODONTAL_SURGERY): (
        ContraindicationSeverity.SEVERE,
        "Contact hematologist. May need coagulation support. "
        "Hemostat agents recommended.",
    ),
}


# ═════════════════════════════════════════════════════════════════════════════════
#  CONTRAINDICATION SERVICE
# ═════════════════════════════════════════════════════════════════════════════════

class ContraindicationService:
    """
    Checks treatment options against patient medical history.
    Identifies contraindications and returns severity + recommendations.
    """

    @staticmethod
    def check_contraindications(
        systemic_conditions: list[SystemicCondition],
        treatment_options: list[TreatmentType],
    ) -> list[Contraindication]:
        """
        Cross-reference patient systemic conditions with treatment options.
        Returns list of contraindications found.

        Args:
            systemic_conditions: List of patient's systemic conditions
            treatment_options: List of treatment options to check

        Returns:
            List of Contraindication objects
        """
        contraindications = []

        for treatment in treatment_options:
            for condition in systemic_conditions:
                key = (condition, treatment)

                if key in CONTRAINDICATION_MATRIX:
                    severity, recommendation = CONTRAINDICATION_MATRIX[key]

                    contraindication = Contraindication(
                        treatment_type=treatment,
                        conflicting_condition=condition.value,
                        severity=severity,
                        clinical_recommendation=recommendation,
                    )

                    contraindications.append(contraindication)

                    logger.warning(
                        "Contraindication detected | treatment=%s condition=%s severity=%s",
                        treatment.value,
                        condition.value,
                        severity.value,
                    )

        return contraindications

    @staticmethod
    def filter_contraindicated_treatments(
        systemic_conditions: list[SystemicCondition],
        treatment_options: list[TreatmentType],
    ) -> tuple[list[TreatmentType], list[TreatmentType]]:
        """
        Split treatments into safe and contraindicated options.

        Args:
            systemic_conditions: List of patient's systemic conditions
            treatment_options: List of treatment options to filter

        Returns:
            Tuple of (safe_treatments, contraindicated_treatments)
        """
        contraindications = ContraindicationService.check_contraindications(
            systemic_conditions, treatment_options
        )

        contraindicated_set = {c.treatment_type for c in contraindications}
        safe_treatments = [t for t in treatment_options if t not in contraindicated_set]
        contraindicated_treatments = list(contraindicated_set)

        return safe_treatments, contraindicated_treatments

    @staticmethod
    def has_absolute_contraindications(
        systemic_conditions: list[SystemicCondition],
        treatment_option: TreatmentType,
    ) -> bool:
        """
        Check if treatment has any ABSOLUTE contraindications.

        Args:
            systemic_conditions: List of patient's systemic conditions
            treatment_option: Single treatment to check

        Returns:
            True if any ABSOLUTE contraindication exists
        """
        for condition in systemic_conditions:
            key = (condition, treatment_option)
            if key in CONTRAINDICATION_MATRIX:
                severity, _ = CONTRAINDICATION_MATRIX[key]
                if severity == ContraindicationSeverity.ABSOLUTE:
                    return True

        return False
