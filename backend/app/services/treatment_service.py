"""
Module 5 — Treatment Recommendation Service
Deterministic treatment planning engine that matches diagnosis codes to treatment protocols
and checks for contraindications based on patient history.

Pipeline:
  1. Extract diagnosis code from M3 output
  2. Look up treatment protocol
  3. Check contraindications against patient systemic conditions
  4. Build medication recommendations
  5. Generate treatment options with alternatives
  6. Return Module 5 output with alerts
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Optional

from app.models.enums import (
    ContraindicationSeverity,
    MedicationType,
    SystemicCondition,
    TreatmentType,
)
from app.schemas.treatment import (
    ContraindicationAlert,
    MedicationRecommendation,
    Module5Output,
    TreatmentOption,
    TreatmentRequest,
    TreatmentSummary,
)
from app.services.contraindication_service import ContraindicationService
from app.services.treatment_profiles import TREATMENT_PROTOCOLS, get_treatment_protocol

logger = logging.getLogger(__name__)


# ═════════════════════════════════════════════════════════════════════════════════
#  MEDICATION MAPPING (maps MedicationType to drug classes)
# ═════════════════════════════════════════════════════════════════════════════════

MEDICATION_CLASS_MAP = {
    MedicationType.ANTIBIOTIC: [
        ("Penicillin V", "500mg"),
        ("Amoxicillin", "500mg"),
        ("Clindamycin", "300mg"),
        ("Metronidazole", "400mg"),
    ],
    MedicationType.ANALGESIC: [
        ("Paracetamol", "500mg"),
        ("Ibuprofen", "400mg"),
        ("Tramadol", "50mg"),
    ],
    MedicationType.ANTI_INFLAMMATORY: [
        ("Ibuprofen", "400mg"),
        ("Naproxen", "250mg"),
        ("Diclofenac", "50mg"),
    ],
    MedicationType.ANTIMICROBIAL_RINSE: [
        ("Chlorhexidine 0.12%", "rinse"),
        ("Povidone-Iodine 1%", "rinse"),
    ],
    MedicationType.ANTIFUNGAL: [
        ("Fluconazole", "150mg"),
        ("Nystatin", "topical"),
    ],
}


class TreatmentService:
    """
    Module 5 — Treatment Recommendation Service.

    Accepts diagnosis and patient history.
    Returns ranked treatment options with contraindication alerts.
    """

    @staticmethod
    def suggest(req: TreatmentRequest) -> Module5Output:
        """
        Generate treatment recommendations from diagnosis and patient history.

        Args:
            req: TreatmentRequest containing diagnosis code and patient data

        Returns:
            Module5Output with ranked treatment options and contraindication alerts

        Raises:
            ValueError: If diagnosis code not found in protocols
        """
        try:
            case_id = req.case_id
            diagnosis_code = req.top_diagnosis_code
            diagnosis_name = req.top_diagnosis_name

            # Fetch treatment protocol for this diagnosis
            protocol = get_treatment_protocol(diagnosis_code)
            if not protocol:
                logger.warning(
                    "M5 | No treatment protocol for %s; using minimal recommendations",
                    diagnosis_code,
                )
                raise ValueError(f"No treatment protocol found for {diagnosis_code}")

            # Parse systemic conditions from string list
            systemic_conditions = TreatmentService._parse_systemic_conditions(
                req.systemic_conditions
            )

            # Build primary treatment option
            primary_treatment = TreatmentService._build_treatment_option(
                protocol.primary_treatment,
                protocol.primary_category,
                protocol.recommended_medications,
                protocol.treatment_notes,
                rank=1,
                success_rate=protocol.success_rate_baseline,
                follow_up_days=protocol.follow_up_days,
            )

            # Build alternative treatments
            alternative_treatments = []
            for rank, (alt_treatment, alt_category) in enumerate(
                protocol.alternative_treatments, start=2
            ):
                alt_option = TreatmentService._build_treatment_option(
                    alt_treatment,
                    alt_category,
                    [],  # Alternatives don't have medications by default
                    "",
                    rank=rank,
                    success_rate=0.75,  # Lower success for alternatives
                    follow_up_days=protocol.follow_up_days,
                )
                alternative_treatments.append(alt_option)

            # Collect all treatments to check for contraindications
            all_treatments = [primary_treatment.treatment_type] + [
                alt.treatment_type for alt in alternative_treatments
            ]

            # Check for contraindications
            contraindication_alerts = TreatmentService._build_contraindication_alerts(
                systemic_conditions, all_treatments
            )

            # Determine feasibility
            feasibility = TreatmentService._assess_feasibility(
                contraindication_alerts, primary_treatment
            )

            # Build summary
            max_severity = TreatmentService._get_max_contraindication_severity(
                contraindication_alerts
            )

            summary = TreatmentSummary(
                primary_treatment_name=primary_treatment.treatment_type.value,
                total_alternatives=len(alternative_treatments),
                medication_count=len(primary_treatment.medications),
                contraindication_count=len(contraindication_alerts),
                highest_contraindication_severity=max_severity,
                overall_feasibility=feasibility,
                clinical_summary=f"Primary: {primary_treatment.treatment_type.value}. "
                f"Alternatives: {len(alternative_treatments)}. "
                f"Alerts: {len(contraindication_alerts)}. "
                f"Feasibility: {feasibility}.",
            )

            # Build reasoning chain
            reasoning = [
                f"Diagnosis: {diagnosis_name} ({diagnosis_code})",
                f"Treatment protocol: Primary={primary_treatment.treatment_type.value}, "
                f"Alternatives={len(alternative_treatments)}",
                f"Patient conditions: {len(systemic_conditions)} identified",
                f"Contraindications: {len(contraindication_alerts)} alerts",
                f"Feasibility assessment: {feasibility}",
            ]

            # Build and return Module 5 output
            output = Module5Output(
                case_id=case_id,
                patient_id=req.patient_id,
                doctor_id=req.doctor_id,
                primary_treatment=primary_treatment,
                alternative_treatments=alternative_treatments,
                contraindication_alerts=contraindication_alerts,
                summary=summary,
                referenced_diagnosis_code=diagnosis_code,
                reasoning_chain=reasoning,
            )

            logger.info(
                "M5 treatment | case_id=%s diagnosis=%s primary=%s alternatives=%d alerts=%d feasibility=%s",
                case_id,
                diagnosis_code,
                primary_treatment.treatment_type.value,
                len(alternative_treatments),
                len(contraindication_alerts),
                feasibility,
            )

            return output

        except ValueError as e:
            logger.error("M5 validation error: %s", str(e))
            raise
        except Exception as e:
            logger.error("M5 treatment service error: %s", str(e), exc_info=True)
            raise

    @staticmethod
    def _parse_systemic_conditions(
        condition_strings: list[str],
    ) -> list[SystemicCondition]:
        """
        Convert string list of conditions to SystemicCondition enums.

        Args:
            condition_strings: List of condition strings

        Returns:
            List of SystemicCondition enums
        """
        conditions = []
        for condition_str in condition_strings:
            try:
                # Try to match the condition string to an enum
                condition = SystemicCondition(condition_str)
                conditions.append(condition)
            except ValueError:
                # Try case-insensitive matching
                for enum_val in SystemicCondition:
                    if enum_val.value.lower() == condition_str.lower():
                        conditions.append(enum_val)
                        break
                else:
                    logger.warning(
                        "Unknown systemic condition: %s; skipping", condition_str
                    )

        return conditions

    @staticmethod
    def _build_treatment_option(
        treatment_type: TreatmentType,
        category: TreatmentType,
        medication_types: list[MedicationType],
        notes: str,
        rank: int,
        success_rate: float,
        follow_up_days: int,
    ) -> TreatmentOption:
        """
        Build a TreatmentOption from protocol data.

        Args:
            treatment_type: Type of treatment
            category: Treatment category
            medication_types: List of medication types to include
            notes: Clinical notes
            rank: Ranking (1=primary, etc.)
            success_rate: Expected success rate
            follow_up_days: Follow-up timing

        Returns:
            TreatmentOption object
        """
        medications = []

        for med_type in medication_types:
            # Get drug class options for this medication type
            drug_options = MEDICATION_CLASS_MAP.get(med_type, [])
            if drug_options:
                drug_class, dosage = drug_options[0]  # Use first option
                med = MedicationRecommendation(
                    medication_type=med_type,
                    drug_class=drug_class,
                    dosage=dosage,
                    frequency="3x daily",
                    duration_days=7,
                    justification=f"Associated with {treatment_type.value} for infection/pain control",
                )
                medications.append(med)

        return TreatmentOption(
            treatment_type=treatment_type,
            category=category,
            description=f"{treatment_type.value} as recommended for treatment plan",
            rank=rank,
            success_rate=success_rate,
            medications=medications,
            follow_up_days=follow_up_days,
            treatment_notes=notes,
        )

    @staticmethod
    def _build_contraindication_alerts(
        systemic_conditions: list[SystemicCondition],
        treatment_options: list[TreatmentType],
    ) -> list[ContraindicationAlert]:
        """
        Check treatments for contraindications against conditions.

        Args:
            systemic_conditions: Patient's conditions
            treatment_options: Treatment options to check

        Returns:
            List of ContraindicationAlert objects
        """
        contraindication_objs = ContraindicationService.check_contraindications(
            systemic_conditions, treatment_options
        )

        alerts = [
            ContraindicationAlert(
                treatment_type=c.treatment_type,
                conflicting_condition=c.conflicting_condition,
                severity=c.severity,
                clinical_recommendation=c.clinical_recommendation,
            )
            for c in contraindication_objs
        ]

        return alerts

    @staticmethod
    def _assess_feasibility(
        alerts: list[ContraindicationAlert],
        primary_treatment: TreatmentOption,
    ) -> str:
        """
        Assess overall treatment feasibility based on contraindications.

        Args:
            alerts: List of contraindication alerts
            primary_treatment: Primary treatment option

        Returns:
            Feasibility assessment ("High", "Moderate", "Low")
        """
        if not alerts:
            return "High"

        # Check if primary treatment has absolute contraindications
        absolute_for_primary = any(
            alert.treatment_type == primary_treatment.treatment_type
            and alert.severity == ContraindicationSeverity.ABSOLUTE
            for alert in alerts
        )

        if absolute_for_primary:
            return "Low"

        # Count severe contraindications
        severe_count = sum(
            1
            for alert in alerts
            if alert.severity in [ContraindicationSeverity.SEVERE, ContraindicationSeverity.MODERATE]
        )

        if severe_count >= 2:
            return "Moderate"
        elif severe_count >= 1:
            return "Moderate"
        else:
            return "High"

    @staticmethod
    def _get_max_contraindication_severity(
        alerts: list[ContraindicationAlert],
    ) -> Optional[ContraindicationSeverity]:
        """
        Get the maximum severity level from alerts.

        Args:
            alerts: List of contraindication alerts

        Returns:
            Maximum severity or None if no alerts
        """
        if not alerts:
            return None

        severity_map = {
            ContraindicationSeverity.MILD: 1,
            ContraindicationSeverity.MODERATE: 2,
            ContraindicationSeverity.SEVERE: 3,
            ContraindicationSeverity.ABSOLUTE: 4,
        }

        max_severity = max(
            (severity_map.get(alert.severity, 0), alert.severity) for alert in alerts
        )[1]

        return max_severity
