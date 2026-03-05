"""
Module 2 — Rule-Based Risk Engine Service
Deterministic clinical safety layer: evaluates bone, systemic, infection,
and surgical complexity rules against Module 1 output.

All rules are pure functions — no LLM, no ML. 100% reproducible.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Optional

from app.models.enums import (
    BoneDensity,
    JawRegion,
    SmokingStatus,
    SwellingGrade,
    Symptom,
    SystemicCondition,
    ToothMobilityGrade,
    VitalityTest,
)
from app.schemas.risk_engine import (
    AlertSeverity,
    BoneRiskDetail,
    ComplexityClass,
    ImplantFeasibility,
    InfectionRiskDetail,
    Module2Output,
    RiskAlert,
    RiskEngineRequest,
    RiskLevel,
    RiskSummary,
    SurgicalComplexityDetail,
    SystemicRiskDetail,
)

logger = logging.getLogger(__name__)


# ═════════════════════════════════════════════════════════════════════════════════
#  CONSTANTS
# ═════════════════════════════════════════════════════════════════════════════════

# Bone thresholds (mm)
MIN_BONE_HEIGHT_IMPLANT = 10.0
MIN_BONE_WIDTH_IMPLANT = 5.0
NERVE_DANGER_ZONE_MM = 2.0
SINUS_CONCERN_ZONE_MM = 8.0

# Systemic risk mappings: condition → (risk_contribution, clinical_note)
SYSTEMIC_RISK_MAP: dict[SystemicCondition, tuple[str, str]] = {
    SystemicCondition.DIABETES_TYPE1: (
        "High",
        "Uncontrolled diabetes impairs wound healing and increases infection risk.",
    ),
    SystemicCondition.DIABETES_TYPE2: (
        "Medium",
        "Type 2 diabetes may delay healing; ensure HbA1c < 7% before elective surgery.",
    ),
    SystemicCondition.HYPERTENSION: (
        "Low",
        "Controlled hypertension — monitor BP before procedures; avoid vasoconstrictors if severe.",
    ),
    SystemicCondition.CARDIOVASCULAR_DISEASE: (
        "High",
        "Cardiovascular disease requires cardiology clearance before sedation/surgery.",
    ),
    SystemicCondition.OSTEOPOROSIS: (
        "Medium",
        "Osteoporosis affects bone quality; check bisphosphonate history.",
    ),
    SystemicCondition.KIDNEY_DISEASE: (
        "High",
        "Renal impairment affects drug metabolism; dose adjustments required.",
    ),
    SystemicCondition.LIVER_DISEASE: (
        "High",
        "Hepatic dysfunction increases bleeding risk and alters drug clearance.",
    ),
    SystemicCondition.HIV_AIDS: (
        "Medium",
        "Immunocompromised status — increased infection risk; check CD4 count.",
    ),
    SystemicCondition.HEPATITIS_B: (
        "Medium",
        "Hepatitis B — cross-infection precautions; check liver function.",
    ),
    SystemicCondition.HEPATITIS_C: (
        "Medium",
        "Hepatitis C — cross-infection precautions; check liver function.",
    ),
    SystemicCondition.BLOOD_DISORDER: (
        "High",
        "Blood disorder — bleeding risk; require CBC and coagulation panel before surgery.",
    ),
    SystemicCondition.AUTOIMMUNE_DISEASE: (
        "Medium",
        "Autoimmune condition — may be on immunosuppressants; delayed healing expected.",
    ),
    SystemicCondition.CANCER_ACTIVE: (
        "Critical",
        "Active cancer — coordinate with oncologist; avoid elective procedures.",
    ),
    SystemicCondition.CANCER_REMISSION: (
        "Low",
        "Cancer in remission — note treatment history; radiation may affect bone.",
    ),
    SystemicCondition.EPILEPSY: (
        "Low",
        "Epilepsy — avoid triggers during treatment; ensure medication compliance.",
    ),
    SystemicCondition.PREGNANCY: (
        "Medium",
        "Pregnancy — avoid elective procedures and certain medications; defer if possible.",
    ),
    SystemicCondition.THYROID_DISORDER: (
        "Low",
        "Thyroid disorder — usually manageable; check if controlled.",
    ),
    SystemicCondition.RHEUMATOID_ARTHRITIS: (
        "Medium",
        "Rheumatoid arthritis — often on immunosuppressants; bone quality may be compromised.",
    ),
    SystemicCondition.ASTHMA: (
        "Low",
        "Asthma — have rescue inhaler available; avoid known triggers.",
    ),
    SystemicCondition.COPD: (
        "Medium",
        "COPD — avoid prolonged supine positions; sedation risk.",
    ),
}


class RiskEngineService:
    """
    Module 2 — Deterministic Rule-Based Risk Engine.

    Processing pipeline:
      1. Evaluate bone adequacy rules (R-01 to R-05)
      2. Evaluate systemic disease risks (R-06 to R-08)
      3. Analyze infection patterns (R-09 to R-12)
      4. Score surgical complexity (R-13 to R-16)
      5. Compute composite risk score and overall level
      6. Build full M2 output JSON
    """

    # ─── PUBLIC API ──────────────────────────────────────────────────────────

    def assess(self, m1: RiskEngineRequest) -> Module2Output:
        """
        Main entry point. Accepts validated Module 1 output,
        returns the complete Module 2 risk assessment.
        """
        alerts: list[RiskAlert] = []
        rule_trace: list[str] = []
        rules_evaluated = 0

        # Step 1 — Bone assessment
        bone_detail, bone_alerts, bone_trace, bone_count = self._assess_bone(m1)
        alerts.extend(bone_alerts)
        rule_trace.extend(bone_trace)
        rules_evaluated += bone_count

        # Step 2 — Systemic risk
        systemic_details, systemic_alerts, systemic_trace, systemic_count = (
            self._assess_systemic(m1)
        )
        alerts.extend(systemic_alerts)
        rule_trace.extend(systemic_trace)
        rules_evaluated += systemic_count

        # Step 3 — Infection pattern
        infection_detail, infection_alerts, infection_trace, infection_count = (
            self._assess_infection(m1)
        )
        alerts.extend(infection_alerts)
        rule_trace.extend(infection_trace)
        rules_evaluated += infection_count

        # Step 4 — Surgical complexity
        complexity_detail, complexity_alerts, complexity_trace, complexity_count = (
            self._assess_surgical_complexity(m1)
        )
        alerts.extend(complexity_alerts)
        rule_trace.extend(complexity_trace)
        rules_evaluated += complexity_count

        # Step 5 — Composite scoring
        risk_score = self._compute_risk_score(
            alerts, bone_detail, systemic_details, infection_detail, complexity_detail
        )
        risk_level = self._score_to_level(risk_score)
        immediate = risk_level in (RiskLevel.HIGH, RiskLevel.CRITICAL)
        feasibility = self._determine_implant_feasibility(
            m1, bone_detail, risk_score
        )

        summary = RiskSummary(
            overall_risk_level=risk_level,
            risk_score=risk_score,
            immediate_attention_required=immediate,
            implant_feasibility=feasibility,
            alert_count=len(alerts),
        )

        now = datetime.now(timezone.utc)

        return Module2Output(
            generated_at=now,
            case_id=m1.case_id,
            patient_id=m1.patient_id,
            doctor_id=m1.doctor_id,
            risk_summary=summary,
            alerts=alerts,
            bone_assessment=bone_detail,
            systemic_risks=systemic_details,
            infection_analysis=infection_detail,
            surgical_complexity=complexity_detail,
            rules_evaluated=rules_evaluated,
            rules_triggered=len(alerts),
            rule_trace=rule_trace,
        )

    # ═════════════════════════════════════════════════════════════════════════
    #  STEP 1: BONE ASSESSMENT (R-01 to R-05)
    # ═════════════════════════════════════════════════════════════════════════

    def _assess_bone(
        self, m1: RiskEngineRequest
    ) -> tuple[Optional[BoneRiskDetail], list[RiskAlert], list[str], int]:
        alerts: list[RiskAlert] = []
        trace: list[str] = []
        rules_count = 0
        site = m1.site_assessment

        if not m1.computed_flags.implant_data_present:
            return None, alerts, trace, rules_count

        height = site.bone_height_mm
        width = site.bone_width_mm
        density = site.bone_density
        height_ok: Optional[bool] = None
        width_ok: Optional[bool] = None
        sinus_aug = False
        nerve_concern = False

        # R-01: Bone height < 10mm
        rules_count += 1
        trace.append("R-01")
        if height is not None:
            height_ok = height >= MIN_BONE_HEIGHT_IMPLANT
            if not height_ok:
                sinus_flag = (
                    site.jaw_region == JawRegion.POSTERIOR_MAXILLA
                )
                sinus_aug = sinus_flag
                alerts.append(RiskAlert(
                    rule_id="R-01",
                    category="Bone",
                    severity=AlertSeverity.WARNING,
                    message=f"Bone height {height}mm is below {MIN_BONE_HEIGHT_IMPLANT}mm threshold.",
                    detail=(
                        "Sinus augmentation may be required."
                        if sinus_flag
                        else "Bone grafting may be required before implant placement."
                    ),
                ))

        # R-02: Bone width < 5mm
        rules_count += 1
        trace.append("R-02")
        if width is not None:
            width_ok = width >= MIN_BONE_WIDTH_IMPLANT
            if not width_ok:
                alerts.append(RiskAlert(
                    rule_id="R-02",
                    category="Bone",
                    severity=AlertSeverity.WARNING,
                    message=f"Bone width {width}mm is below {MIN_BONE_WIDTH_IMPLANT}mm threshold.",
                    detail="Ridge augmentation or narrow-diameter implant may be needed.",
                ))

        # R-03: Poor bone density (D4)
        rules_count += 1
        trace.append("R-03")
        if density == BoneDensity.D4:
            alerts.append(RiskAlert(
                rule_id="R-03",
                category="Bone",
                severity=AlertSeverity.WARNING,
                message="Bone density D4 (very soft) — reduced primary stability expected.",
                detail="Consider under-preparation technique or longer healing period.",
            ))

        # R-04: Nerve proximity < 2mm
        rules_count += 1
        trace.append("R-04")
        if site.nerve_proximity_mm is not None and site.nerve_proximity_mm < NERVE_DANGER_ZONE_MM:
            nerve_concern = True
            alerts.append(RiskAlert(
                rule_id="R-04",
                category="Bone",
                severity=AlertSeverity.CRITICAL,
                message=f"Nerve proximity {site.nerve_proximity_mm}mm — CRITICAL risk of IAN damage.",
                detail="Shorter implant or alternative site strongly recommended.",
            ))

        # R-05: Sinus proximity < 8mm (posterior maxilla)
        rules_count += 1
        trace.append("R-05")
        if (
            site.jaw_region == JawRegion.POSTERIOR_MAXILLA
            and site.sinus_proximity_mm is not None
            and site.sinus_proximity_mm < SINUS_CONCERN_ZONE_MM
        ):
            sinus_aug = True
            alerts.append(RiskAlert(
                rule_id="R-05",
                category="Bone",
                severity=AlertSeverity.WARNING,
                message=f"Sinus floor distance {site.sinus_proximity_mm}mm — sinus lift evaluation needed.",
                detail="Internal or external sinus lift may be required.",
            ))

        bone_detail = BoneRiskDetail(
            bone_height_mm=height,
            bone_width_mm=width,
            bone_density=density.value if density else None,
            height_adequate=height_ok,
            width_adequate=width_ok,
            sinus_augmentation_needed=sinus_aug,
            nerve_proximity_concern=nerve_concern,
        )

        return bone_detail, alerts, trace, rules_count

    # ═════════════════════════════════════════════════════════════════════════
    #  STEP 2: SYSTEMIC DISEASE RISK (R-06 to R-08)
    # ═════════════════════════════════════════════════════════════════════════

    def _assess_systemic(
        self, m1: RiskEngineRequest
    ) -> tuple[list[SystemicRiskDetail], list[RiskAlert], list[str], int]:
        alerts: list[RiskAlert] = []
        trace: list[str] = []
        details: list[SystemicRiskDetail] = []
        rules_count = 0
        hist = m1.medical_history

        # R-06: Systemic conditions mapping
        rules_count += 1
        trace.append("R-06")
        for cond in hist.systemic_conditions:
            if cond == SystemicCondition.NONE:
                continue
            mapping = SYSTEMIC_RISK_MAP.get(cond)
            if mapping:
                risk_contrib, note = mapping
                details.append(SystemicRiskDetail(
                    condition=cond.value,
                    risk_contribution=risk_contrib,
                    note=note,
                ))
                if risk_contrib in ("High", "Critical"):
                    alerts.append(RiskAlert(
                        rule_id="R-06",
                        category="Systemic",
                        severity=(
                            AlertSeverity.CRITICAL
                            if risk_contrib == "Critical"
                            else AlertSeverity.WARNING
                        ),
                        message=f"Systemic risk: {cond.value} — {risk_contrib} impact.",
                        detail=note,
                    ))

        # R-07: Bisphosphonate + implant
        rules_count += 1
        trace.append("R-07")
        if hist.bisphosphonate_therapy and m1.computed_flags.implant_data_present:
            alerts.append(RiskAlert(
                rule_id="R-07",
                category="Systemic",
                severity=AlertSeverity.CRITICAL,
                message="Bisphosphonate therapy with implant planning — HIGH osteonecrosis risk.",
                detail="Drug holiday and specialist referral recommended before implant surgery.",
            ))
            details.append(SystemicRiskDetail(
                condition="Bisphosphonate_Therapy",
                risk_contribution="Critical",
                note="Risk of medication-related osteonecrosis of the jaw (MRONJ).",
            ))

        # R-08: Immunocompromised / bleeding disorder
        rules_count += 1
        trace.append("R-08")
        if hist.immunocompromised:
            alerts.append(RiskAlert(
                rule_id="R-08",
                category="Systemic",
                severity=AlertSeverity.WARNING,
                message="Immunocompromised patient — increased infection and healing risk.",
                detail="Consider prophylactic antibiotics and close post-op monitoring.",
            ))
        if hist.bleeding_disorder:
            alerts.append(RiskAlert(
                rule_id="R-08",
                category="Systemic",
                severity=AlertSeverity.WARNING,
                message="Bleeding disorder present — haemostasis protocol required.",
                detail="Obtain CBC and coagulation panel; coordinate with haematologist if surgical.",
            ))

        return details, alerts, trace, rules_count

    # ═════════════════════════════════════════════════════════════════════════
    #  STEP 3: INFECTION PATTERN DETECTION (R-09 to R-12)
    # ═════════════════════════════════════════════════════════════════════════

    def _assess_infection(
        self, m1: RiskEngineRequest
    ) -> tuple[Optional[InfectionRiskDetail], list[RiskAlert], list[str], int]:
        alerts: list[RiskAlert] = []
        trace: list[str] = []
        rules_count = 0
        ca = m1.clinical_assessment
        symptoms = m1.chief_complaint.symptoms

        # Infection indicator symptoms
        infection_indicators: list[str] = []
        infection_symptoms = {
            Symptom.SWELLING_LOCALIZED,
            Symptom.SWELLING_DIFFUSE,
            Symptom.SWELLING_EXTRAORAL,
            Symptom.PUS_DISCHARGE,
            Symptom.FISTULA_SINUS_TRACT,
            Symptom.GUM_BLEEDING,
        }
        for s in symptoms:
            if s in infection_symptoms:
                infection_indicators.append(s.value)
        if ca.fever.present:
            infection_indicators.append("Fever")
        if ca.lymphadenopathy:
            infection_indicators.append("Lymphadenopathy")

        if not infection_indicators:
            return None, alerts, trace, rules_count

        # R-09: Acute localized infection
        rules_count += 1
        trace.append("R-09")
        has_pus = Symptom.PUS_DISCHARGE in symptoms
        has_local_swelling = Symptom.SWELLING_LOCALIZED in symptoms
        has_diffuse = Symptom.SWELLING_DIFFUSE in symptoms
        has_extraoral = Symptom.SWELLING_EXTRAORAL in symptoms

        # R-10: Spreading infection detection
        rules_count += 1
        trace.append("R-10")
        spreading = (
            (has_diffuse or has_extraoral)
            and ca.fever.present
            and (ca.lymphadenopathy is True)
        )

        # R-11: Chronic infection (fistula/sinus tract)
        rules_count += 1
        trace.append("R-11")
        chronic = Symptom.FISTULA_SINUS_TRACT in symptoms

        # R-12: High fever with infection signs
        rules_count += 1
        trace.append("R-12")
        high_fever = (
            ca.fever.present
            and ca.fever.temperature_celsius is not None
            and ca.fever.temperature_celsius >= 38.5
        )

        # Determine pattern
        if spreading:
            pattern = "Spreading_Infection"
            spread_risk = "High"
            alerts.append(RiskAlert(
                rule_id="R-10",
                category="Infection",
                severity=AlertSeverity.CRITICAL,
                message="Spreading infection detected — diffuse/extraoral swelling with systemic signs.",
                detail="Immediate intervention required. Consider IV antibiotics and incision & drainage.",
            ))
        elif has_pus or (has_local_swelling and ca.fever.present):
            pattern = "Acute_Localized"
            spread_risk = "Medium"
            alerts.append(RiskAlert(
                rule_id="R-09",
                category="Infection",
                severity=AlertSeverity.WARNING,
                message="Acute localized infection — pus/swelling with fever.",
                detail="Antibiotics and drainage may be required. Monitor for spread.",
            ))
        elif chronic:
            pattern = "Chronic_Infection"
            spread_risk = "Low"
            alerts.append(RiskAlert(
                rule_id="R-11",
                category="Infection",
                severity=AlertSeverity.INFO,
                message="Chronic infection indicator — fistula/sinus tract present.",
                detail="Indicates longstanding periapical pathology. Endodontic or surgical treatment needed.",
            ))
        else:
            pattern = "Mild_Indicators"
            spread_risk = "Low"

        if high_fever:
            alerts.append(RiskAlert(
                rule_id="R-12",
                category="Infection",
                severity=AlertSeverity.WARNING,
                message=f"Elevated temperature {ca.fever.temperature_celsius}°C with infection signs.",
                detail="Systemic involvement possible. Rule out cellulitis or abscess.",
            ))

        infection_detail = InfectionRiskDetail(
            pattern=pattern,
            indicators=infection_indicators,
            spread_risk=spread_risk,
        )

        return infection_detail, alerts, trace, rules_count

    # ═════════════════════════════════════════════════════════════════════════
    #  STEP 4: SURGICAL COMPLEXITY SCORING (R-13 to R-16)
    # ═════════════════════════════════════════════════════════════════════════

    def _assess_surgical_complexity(
        self, m1: RiskEngineRequest
    ) -> tuple[Optional[SurgicalComplexityDetail], list[RiskAlert], list[str], int]:
        alerts: list[RiskAlert] = []
        trace: list[str] = []
        rules_count = 0
        factors: list[str] = []
        score = 0

        ca = m1.clinical_assessment
        site = m1.site_assessment
        hist = m1.medical_history
        flags = m1.computed_flags

        # R-13: Pain & swelling severity
        rules_count += 1
        trace.append("R-13")
        if ca.pain_level >= 8:
            score += 15
            factors.append(f"Severe pain (VAS {ca.pain_level}/10)")
        elif ca.pain_level >= 5:
            score += 8
            factors.append(f"Moderate pain (VAS {ca.pain_level}/10)")

        if ca.swelling_grade == SwellingGrade.SEVERE:
            score += 15
            factors.append("Severe swelling")
        elif ca.swelling_grade == SwellingGrade.MODERATE:
            score += 8
            factors.append("Moderate swelling")

        # R-14: Tooth mobility & vitality
        rules_count += 1
        trace.append("R-14")
        if ca.tooth_mobility_grade == ToothMobilityGrade.GRADE_3:
            score += 12
            factors.append("Grade 3 tooth mobility")
        elif ca.tooth_mobility_grade == ToothMobilityGrade.GRADE_2:
            score += 6
            factors.append("Grade 2 tooth mobility")

        if ca.vitality_test == VitalityTest.NON_VITAL:
            score += 8
            factors.append("Non-vital tooth")

        if ca.probing_depth_mm is not None and ca.probing_depth_mm >= 6.0:
            score += 8
            factors.append(f"Deep probing depth ({ca.probing_depth_mm}mm)")

        # R-15: Bone & anatomical factors
        rules_count += 1
        trace.append("R-15")
        if flags.implant_data_present:
            if site.bone_height_mm is not None and site.bone_height_mm < MIN_BONE_HEIGHT_IMPLANT:
                score += 12
                factors.append("Insufficient bone height for implant")
            if site.bone_width_mm is not None and site.bone_width_mm < MIN_BONE_WIDTH_IMPLANT:
                score += 10
                factors.append("Insufficient bone width for implant")
            if site.bone_density == BoneDensity.D4:
                score += 8
                factors.append("Poor bone density (D4)")
            if site.nerve_proximity_mm is not None and site.nerve_proximity_mm < NERVE_DANGER_ZONE_MM:
                score += 15
                factors.append("Critical nerve proximity")

        # R-16: Systemic complicating factors
        rules_count += 1
        trace.append("R-16")
        if hist.bleeding_disorder:
            score += 10
            factors.append("Bleeding disorder")
        if hist.immunocompromised:
            score += 8
            factors.append("Immunocompromised")
        if hist.smoking_status == SmokingStatus.CURRENT_SMOKER:
            score += 5
            factors.append("Active smoker")
        if hist.bisphosphonate_therapy:
            score += 12
            factors.append("Bisphosphonate therapy")
        if hist.radiation_therapy_head_neck:
            score += 12
            factors.append("Head/neck radiation history")
        if flags.age_contraindication:
            score += 10
            factors.append("Age < 18 (growth incomplete)")

        # Cap at 100
        score = min(score, 100)

        # Classify
        if score >= 70:
            cls = ComplexityClass.HIGHLY_COMPLEX
        elif score >= 45:
            cls = ComplexityClass.COMPLEX
        elif score >= 20:
            cls = ComplexityClass.MODERATE
        else:
            cls = ComplexityClass.SIMPLE

        if cls in (ComplexityClass.HIGHLY_COMPLEX, ComplexityClass.COMPLEX):
            alerts.append(RiskAlert(
                rule_id="R-16",
                category="Surgical",
                severity=(
                    AlertSeverity.CRITICAL
                    if cls == ComplexityClass.HIGHLY_COMPLEX
                    else AlertSeverity.WARNING
                ),
                message=f"Surgical complexity: {cls.value} (score {score}/100).",
                detail=f"Contributing factors: {', '.join(factors[:5])}.",
            ))

        detail = SurgicalComplexityDetail(
            score=score,
            complexity_class=cls,
            factors=factors,
        )

        return detail, alerts, trace, rules_count

    # ═════════════════════════════════════════════════════════════════════════
    #  STEP 5: COMPOSITE RISK SCORE
    # ═════════════════════════════════════════════════════════════════════════

    def _compute_risk_score(
        self,
        alerts: list[RiskAlert],
        bone: Optional[BoneRiskDetail],
        systemic: list[SystemicRiskDetail],
        infection: Optional[InfectionRiskDetail],
        complexity: Optional[SurgicalComplexityDetail],
    ) -> int:
        """
        Composite score (0-100) weighted across all domains:
          - Alert severity points
          - Complexity score contribution
          - Infection spread risk contribution
        """
        score = 0

        # Severity-based points from alerts
        for a in alerts:
            if a.severity == AlertSeverity.CRITICAL:
                score += 12
            elif a.severity == AlertSeverity.WARNING:
                score += 6
            else:
                score += 2

        # Complexity contribution (40% weight)
        if complexity:
            score += int(complexity.score * 0.4)

        # Infection spread risk
        if infection:
            if infection.spread_risk == "High":
                score += 15
            elif infection.spread_risk == "Medium":
                score += 8

        # Systemic high-risk count
        high_systemic = sum(
            1 for s in systemic if s.risk_contribution in ("High", "Critical")
        )
        score += high_systemic * 5

        return min(score, 100)

    @staticmethod
    def _score_to_level(score: int) -> RiskLevel:
        if score >= 75:
            return RiskLevel.CRITICAL
        elif score >= 50:
            return RiskLevel.HIGH
        elif score >= 25:
            return RiskLevel.MEDIUM
        return RiskLevel.LOW

    # ═════════════════════════════════════════════════════════════════════════
    #  IMPLANT FEASIBILITY
    # ═════════════════════════════════════════════════════════════════════════

    def _determine_implant_feasibility(
        self,
        m1: RiskEngineRequest,
        bone: Optional[BoneRiskDetail],
        risk_score: int,
    ) -> ImplantFeasibility:
        if not m1.computed_flags.implant_data_present:
            return ImplantFeasibility.INSUFFICIENT_DATA

        # Absolute contraindications
        if (
            m1.computed_flags.age_contraindication
            or (
                m1.medical_history.bisphosphonate_therapy
                and m1.medical_history.radiation_therapy_head_neck
            )
        ):
            return ImplantFeasibility.NOT_RECOMMENDED

        # Bone inadequacy or high risk
        if bone:
            critical_bone = (
                (bone.height_adequate is False)
                or (bone.width_adequate is False)
                or bone.nerve_proximity_concern
            )
            if critical_bone and risk_score >= 50:
                return ImplantFeasibility.NOT_RECOMMENDED
            if critical_bone or risk_score >= 40:
                return ImplantFeasibility.CONDITIONAL

        if risk_score >= 40:
            return ImplantFeasibility.CONDITIONAL

        return ImplantFeasibility.FEASIBLE
