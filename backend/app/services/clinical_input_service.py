"""
Module 1 — Clinical Input Processing Service
Core business logic: sanitization, cross-field validation, computed flags, JSON assembly.
Reference: Module_1_Clinical_Input_Processing.md §4–§5
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from app.models.enums import (
    BoneDensity,
    JawRegion,
    SmokingStatus,
    SwellingGrade,
    SystemicCondition,
    UrgencyFlag,
)
from app.schemas.clinical_input import (
    ChiefComplaintOutput,
    ClinicalAssessmentOutput,
    ClinicalInputRequest,
    ComputedFlagsOutput,
    DemographicsOutput,
    FeverOutput,
    MedicalHistoryOutput,
    Module1Output,
    SiteAssessmentOutput,
    ValidationStatusOutput,
)
from app.services.sanitization import sanitize_string, sanitize_string_list


class ClinicalInputService:
    """
    Orchestrates the Module 1 processing pipeline:
      1. Sanitize inputs
      2. Compute flags (cross-field logic §4.2 / §5.3)
      3. Generate warnings
      4. Assemble the structured M1 output JSON
    """

    # ─── PUBLIC API ──────────────────────────────────────────────────────────

    def process(
        self,
        request: ClinicalInputRequest,
        doctor_id: uuid.UUID,
    ) -> Module1Output:
        """
        Main entry point. Accepts a validated ClinicalInputRequest
        and returns the full Module1Output JSON contract.
        """
        # Step 1 — Sanitize free-text fields ──────────────────────────────────
        sanitized = self._sanitize(request)

        # Step 2 — Determine implant data presence ────────────────────────────
        implant_data_present = self._has_implant_data(sanitized)

        # Step 3 — Compute flags (§5.3) ───────────────────────────────────────
        computed_flags = self._compute_flags(sanitized, implant_data_present)

        # Step 4 — Generate warnings ──────────────────────────────────────────
        warnings = self._generate_warnings(sanitized, computed_flags)

        # Step 5 — Assemble output JSON ───────────────────────────────────────
        case_id = uuid.uuid4()
        now = datetime.now(timezone.utc)

        output = Module1Output(
            module="M1_Clinical_Input",
            version="1.0",
            generated_at=now,
            case_id=case_id,
            patient_id=sanitized.patient_id,
            doctor_id=doctor_id,
            demographics=DemographicsOutput(
                age=sanitized.age,
                gender=sanitized.gender,
                weight_kg=sanitized.weight_kg,
            ),
            medical_history=MedicalHistoryOutput(
                systemic_conditions=sanitized.systemic_conditions,
                allergies=sanitized.allergies or [],
                current_medications=sanitized.current_medications or [],
                bleeding_disorder=sanitized.bleeding_disorder,
                immunocompromised=sanitized.immunocompromised,
                smoking_status=sanitized.smoking_status,
                bisphosphonate_therapy=sanitized.bisphosphonate_therapy,
                radiation_therapy_head_neck=sanitized.radiation_therapy_head_neck,
            ),
            chief_complaint=ChiefComplaintOutput(
                description=sanitized.chief_complaint,
                symptoms=sanitized.symptoms,
                duration_days=sanitized.symptom_duration_days,
                onset=sanitized.symptom_onset,
            ),
            clinical_assessment=ClinicalAssessmentOutput(
                pain_level=sanitized.pain_level,
                swelling_grade=sanitized.swelling_grade,
                fever=FeverOutput(
                    present=sanitized.fever_present,
                    temperature_celsius=sanitized.temperature_celsius,
                ),
                lymphadenopathy=sanitized.lymphadenopathy,
                tooth_mobility_grade=sanitized.tooth_mobility_grade,
                percussion_test=sanitized.percussion_test,
                vitality_test=sanitized.vitality_test,
                probing_depth_mm=sanitized.probing_depth_mm,
            ),
            site_assessment=SiteAssessmentOutput(
                tooth_site=sanitized.tooth_site,
                jaw_region=sanitized.jaw_region,
                bone_height_mm=sanitized.bone_height_mm,
                bone_width_mm=sanitized.bone_width_mm,
                bone_density=sanitized.bone_density,
                adjacent_teeth_status=sanitized.adjacent_teeth_status,
                sinus_proximity_mm=sanitized.sinus_proximity_mm,
                nerve_proximity_mm=sanitized.nerve_proximity_mm,
            ),
            clinical_notes=sanitized.clinical_notes,
            computed_flags=computed_flags,
            validation_status=ValidationStatusOutput(
                is_valid=True,
                errors=[],
                warnings=warnings,
            ),
        )

        return output

    # ─── PRIVATE: SANITIZATION ───────────────────────────────────────────────

    def _sanitize(self, req: ClinicalInputRequest) -> ClinicalInputRequest:
        """
        Apply sanitization rules S-01 through S-05 (§4.3).
        Returns a copy of the request with sanitized text fields.
        """
        updates: dict[str, Any] = {}

        # Sanitize chief_complaint (S-01, S-02, S-04)
        updates["chief_complaint"] = sanitize_string(req.chief_complaint)

        # Sanitize clinical_notes (S-01, S-02, S-04)
        updates["clinical_notes"] = sanitize_string(req.clinical_notes)

        # Sanitize allergy strings (S-01, S-04)
        updates["allergies"] = sanitize_string_list(req.allergies)

        # Sanitize medication strings (S-01, S-04)
        updates["current_medications"] = sanitize_string_list(req.current_medications)

        return req.model_copy(update=updates)

    # ─── PRIVATE: IMPLANT DATA CHECK ─────────────────────────────────────────

    @staticmethod
    def _has_implant_data(req: ClinicalInputRequest) -> bool:
        """
        §5.3: implant_data_present = true if any of
        bone_height_mm, bone_width_mm, bone_density is provided.
        """
        return any([
            req.bone_height_mm is not None,
            req.bone_width_mm is not None,
            req.bone_density is not None,
        ])

    # ─── PRIVATE: COMPUTED FLAGS (§5.3) ──────────────────────────────────────

    def _compute_flags(
        self,
        req: ClinicalInputRequest,
        implant_data_present: bool,
    ) -> ComputedFlagsOutput:
        """
        Compute all flags defined in Module 1 §5.3.
        """
        urgency = self._compute_urgency(req)
        bisphosphonate_risk = (
            req.bisphosphonate_therapy and implant_data_present
        )
        radiation_risk = (
            req.radiation_therapy_head_neck and implant_data_present
        )
        age_contraindication = req.age < 18 and implant_data_present

        return ComputedFlagsOutput(
            urgency_flag=urgency,
            bisphosphonate_risk=bisphosphonate_risk,
            radiation_risk=radiation_risk,
            age_contraindication=age_contraindication,
            implant_data_present=implant_data_present,
        )

    @staticmethod
    def _compute_urgency(req: ClinicalInputRequest) -> UrgencyFlag:
        """
        Urgency flag logic (§5.3):
          HIGH   → fever_present AND swelling = Severe AND pain ≥ 8
          MEDIUM → pain ≥ 6 OR swelling ∈ {Moderate, Severe}
          LOW    → all other cases
        """
        # HIGH: all three conditions must be met
        if (
            req.fever_present
            and req.swelling_grade == SwellingGrade.SEVERE
            and req.pain_level >= 8
        ):
            return UrgencyFlag.HIGH

        # MEDIUM: either condition
        if req.pain_level >= 6 or req.swelling_grade in (
            SwellingGrade.MODERATE,
            SwellingGrade.SEVERE,
        ):
            return UrgencyFlag.MEDIUM

        # LOW: default
        return UrgencyFlag.LOW

    # ─── PRIVATE: WARNINGS ───────────────────────────────────────────────────

    def _generate_warnings(
        self,
        req: ClinicalInputRequest,
        flags: ComputedFlagsOutput,
    ) -> list[str]:
        """
        Generate non-blocking clinical warnings based on input data.
        These are informational and do NOT block submission.
        """
        warnings: list[str] = []

        # XV-01: Posterior maxilla + bone height < 10mm
        if (
            req.jaw_region == JawRegion.POSTERIOR_MAXILLA
            and req.bone_height_mm is not None
            and req.bone_height_mm < 10.0
        ):
            warnings.append(
                "Bone height < 10mm in posterior maxilla — "
                "Sinus augmentation may be recommended (forwarded to Risk Engine)."
            )

        # Nerve proximity caution
        if req.nerve_proximity_mm is not None and req.nerve_proximity_mm < 5.0:
            warnings.append(
                f"Nerve proximity {req.nerve_proximity_mm}mm (< 5mm) — "
                "exercise caution during extraction/implant placement."
            )

        # Sinus proximity caution
        if (
            req.jaw_region == JawRegion.POSTERIOR_MAXILLA
            and req.sinus_proximity_mm is not None
            and req.sinus_proximity_mm < 8.0
        ):
            warnings.append(
                f"Sinus floor distance {req.sinus_proximity_mm}mm — "
                "may require sinus lift evaluation."
            )

        # XV-03: Bisphosphonate + implant data
        if flags.bisphosphonate_risk:
            warnings.append(
                "Bisphosphonate therapy with implant data present — "
                "HIGH risk for osteonecrosis (flagged for Risk Engine)."
            )

        # XV-05: Radiation + implant data
        if flags.radiation_risk:
            warnings.append(
                "Head & neck radiation history with implant data present — "
                "risk of osteoradionecrosis (flagged for Risk Engine)."
            )

        # XV-04: Age < 18 + implant data
        if flags.age_contraindication:
            warnings.append(
                "Patient under 18 — implant planning is not recommended. "
                "Jaw growth may be incomplete."
            )

        # Smoking + implant data
        if (
            req.smoking_status == SmokingStatus.CURRENT_SMOKER
            and flags.implant_data_present
        ):
            warnings.append(
                "Active smoker with implant planning data — "
                "increased risk of implant failure."
            )

        # Deep probing depth
        if req.probing_depth_mm is not None and req.probing_depth_mm >= 6.0:
            warnings.append(
                f"Probing depth {req.probing_depth_mm}mm ≥ 6mm — "
                "indicative of advanced periodontal involvement."
            )

        return warnings
