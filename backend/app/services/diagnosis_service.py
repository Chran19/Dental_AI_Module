"""
Module 3 — Differential Diagnosis Service
Deterministic scoring engine that matches clinical data against
diagnosis profiles and returns ranked differentials with evidence.

Pipeline:
  1. Extract clinical signals from M1 + M2
  2. Score each diagnosis profile
  3. Rank by score, apply M2 risk modifiers
  4. Build evidence chains + justification
  5. Return top-N results
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Optional

from app.models.enums import (
    PercussionTest,
    SwellingGrade,
    Symptom,
    SymptomOnset,
    ToothMobilityGrade,
    VitalityTest,
)
from app.schemas.diagnosis import (
    ContradictingEvidence,
    DiagnosisRequest,
    DifferentialDiagnosis,
    Module3Output,
    SupportingEvidence,
)
from app.services.diagnosis_profiles import (
    DIAGNOSIS_PROFILES,
    DiagnosisProfile,
    FindingExpectation,
)

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════════
#  WEIGHT CONSTANTS FOR SCORING COMPONENTS
# ═══════════════════════════════════════════════════════════════════════════════

W_SYMPTOM = 0.35          # symptom match component weight
W_FINDINGS = 0.30         # clinical findings match weight
W_ONSET_DURATION = 0.10   # onset/duration pattern weight
W_PREVALENCE = 0.10       # base prevalence weight
W_M2_MODIFIER = 0.15      # M2 risk-based modifier weight

CONTRADICTION_PENALTY = 0.15  # per contradicting element


# ═══════════════════════════════════════════════════════════════════════════════
#  SWELLING GRADE ORDER (for comparison)
# ═══════════════════════════════════════════════════════════════════════════════

_SWELLING_ORDER = {
    SwellingGrade.NONE: 0,
    SwellingGrade.MILD: 1,
    SwellingGrade.MODERATE: 2,
    SwellingGrade.SEVERE: 3,
}

_MOBILITY_ORDER = {
    ToothMobilityGrade.NONE: 0,
    ToothMobilityGrade.GRADE_1: 1,
    ToothMobilityGrade.GRADE_2: 2,
    ToothMobilityGrade.GRADE_3: 3,
}


class DiagnosisService:
    """
    Module 3 — Differential Diagnosis Scoring Engine.

    Accepts combined M1 + M2 data, scores every diagnosis profile,
    and returns ranked results with evidence chains.
    """

    # ─── PUBLIC API ──────────────────────────────────────────────────────

    def diagnose(self, req: DiagnosisRequest) -> Module3Output:
        m1 = req.m1
        m2 = req.m2
        max_n = req.max_results

        scored: list[tuple[DiagnosisProfile, float, list[SupportingEvidence], list[ContradictingEvidence]]] = []

        for profile in DIAGNOSIS_PROFILES:
            raw_score, supporting, contradicting = self._score_profile(profile, req)
            if raw_score > 0:
                scored.append((profile, raw_score, supporting, contradicting))

        # Sort descending by score
        scored.sort(key=lambda x: x[1], reverse=True)

        # Normalise scores to percentages (relative to best)
        top = scored[:max_n]
        max_score = top[0][1] if top else 1.0

        differentials: list[DifferentialDiagnosis] = []
        for rank_idx, (profile, score, supporting, contradicting) in enumerate(top, start=1):
            confidence = round(min((score / max_score) * 95, 99.0), 1)
            justification = self._build_justification(profile, supporting, contradicting, confidence)
            differentials.append(DifferentialDiagnosis(
                rank=rank_idx,
                code=profile.code,
                name=profile.name,
                category=profile.category,
                confidence_pct=confidence,
                description=profile.description,
                supporting_evidence=supporting,
                contradicting_evidence=contradicting,
                justification=justification,
            ))

        summary = self._build_clinical_summary(m1, m2, differentials)

        return Module3Output(
            generated_at=datetime.now(timezone.utc),
            case_id=m1.case_id,
            patient_id=m1.patient_id,
            doctor_id=m1.doctor_id,
            differentials=differentials,
            profiles_evaluated=len(DIAGNOSIS_PROFILES),
            clinical_summary=summary,
        )

    # ═══════════════════════════════════════════════════════════════════════
    #  SCORING ENGINE
    # ═══════════════════════════════════════════════════════════════════════

    def _score_profile(
        self,
        profile: DiagnosisProfile,
        req: DiagnosisRequest,
    ) -> tuple[float, list[SupportingEvidence], list[ContradictingEvidence]]:
        """
        Score a single diagnosis profile against the clinical data.
        Returns (raw_score, supporting_evidence, contradicting_evidence).
        """
        supporting: list[SupportingEvidence] = []
        contradicting: list[ContradictingEvidence] = []

        # ── 1. Symptom matching ──────────────────────────────────────────
        symptom_score = self._score_symptoms(profile, req, supporting)

        # ── 2. Clinical findings matching ────────────────────────────────
        findings_score = self._score_findings(profile, req, supporting, contradicting)

        # ── 3. Onset / duration pattern ──────────────────────────────────
        onset_score = self._score_onset_duration(profile, req, supporting)

        # ── 4. Base prevalence ───────────────────────────────────────────
        prevalence_score = profile.base_prevalence

        # ── 5. M2 risk modifier ──────────────────────────────────────────
        m2_modifier = self._score_m2_modifier(profile, req, supporting)

        # ── 6. Contradiction penalty ─────────────────────────────────────
        contradiction_total = self._score_contradictions(profile, req, contradicting)

        # ── Composite score ──────────────────────────────────────────────
        raw = (
            W_SYMPTOM * symptom_score
            + W_FINDINGS * findings_score
            + W_ONSET_DURATION * onset_score
            + W_PREVALENCE * prevalence_score
            + W_M2_MODIFIER * m2_modifier
            - contradiction_total
        )

        return max(raw, 0.0), supporting, contradicting

    # ─── COMPONENT SCORERS ───────────────────────────────────────────────

    def _score_symptoms(
        self,
        profile: DiagnosisProfile,
        req: DiagnosisRequest,
        supporting: list[SupportingEvidence],
    ) -> float:
        """Match patient symptoms against profile weights. Returns 0.0-1.0."""
        if not profile.symptom_weights:
            return 0.0

        patient_symptoms = set(req.m1.chief_complaint.symptoms)
        total_weight = sum(profile.symptom_weights.values())
        matched_weight = 0.0

        for symptom, weight in profile.symptom_weights.items():
            if symptom in patient_symptoms:
                matched_weight += weight
                strength = "Strong" if weight >= 0.7 else ("Moderate" if weight >= 0.4 else "Weak")
                supporting.append(SupportingEvidence(
                    finding=f"Symptom: {symptom.value}",
                    value="Present",
                    weight=strength,
                ))

        return matched_weight / total_weight if total_weight > 0 else 0.0

    def _score_findings(
        self,
        profile: DiagnosisProfile,
        req: DiagnosisRequest,
        supporting: list[SupportingEvidence],
        contradicting: list[ContradictingEvidence],
    ) -> float:
        """Match clinical exam findings. Returns 0.0-1.0."""
        ca = req.m1.clinical_assessment
        exp = profile.findings
        checks = 0
        matches = 0

        # Vitality test
        if exp.vitality is not None:
            checks += 1
            if ca.vitality_test == exp.vitality:
                matches += 1
                supporting.append(SupportingEvidence(
                    finding="Vitality test",
                    value=ca.vitality_test.value if ca.vitality_test else "Not tested",
                    weight="Strong",
                ))
            elif ca.vitality_test is not None and ca.vitality_test != VitalityTest.NOT_TESTED:
                contradicting.append(ContradictingEvidence(
                    finding="Vitality test",
                    value=ca.vitality_test.value,
                    reason=f"Expected {exp.vitality.value}, found {ca.vitality_test.value}",
                ))

        # Percussion
        if exp.percussion_positive:
            checks += 1
            positive = ca.percussion_test in (PercussionTest.POSITIVE_MILD, PercussionTest.POSITIVE_SEVERE)
            if positive:
                matches += 1
                supporting.append(SupportingEvidence(
                    finding="Percussion test",
                    value=ca.percussion_test.value if ca.percussion_test else "N/A",
                    weight="Moderate",
                ))

        # Mobility
        if exp.mobility_min is not None and ca.tooth_mobility_grade is not None:
            checks += 1
            patient_mob = _MOBILITY_ORDER.get(ca.tooth_mobility_grade, 0)
            expected_mob = _MOBILITY_ORDER.get(exp.mobility_min, 0)
            if patient_mob >= expected_mob:
                matches += 1
                supporting.append(SupportingEvidence(
                    finding="Tooth mobility",
                    value=ca.tooth_mobility_grade.value,
                    weight="Moderate",
                ))

        # Swelling
        if exp.swelling_expected is not None:
            checks += 1
            patient_sw = _SWELLING_ORDER.get(ca.swelling_grade, 0)
            expected_sw = _SWELLING_ORDER.get(exp.swelling_expected, 0)
            if patient_sw >= expected_sw:
                matches += 1
                supporting.append(SupportingEvidence(
                    finding="Swelling grade",
                    value=ca.swelling_grade.value,
                    weight="Moderate",
                ))

        # Fever
        if exp.fever_expected:
            checks += 1
            if ca.fever.present:
                matches += 1
                temp = ca.fever.temperature_celsius
                supporting.append(SupportingEvidence(
                    finding="Fever",
                    value=f"{temp}°C" if temp else "Present",
                    weight="Moderate",
                ))

        # Lymphadenopathy
        if exp.lymphadenopathy_expected:
            checks += 1
            if ca.lymphadenopathy:
                matches += 1
                supporting.append(SupportingEvidence(
                    finding="Lymphadenopathy",
                    value="Present",
                    weight="Moderate",
                ))

        # Probing depth
        if exp.probing_depth_min_mm is not None and ca.probing_depth_mm is not None:
            checks += 1
            if ca.probing_depth_mm >= exp.probing_depth_min_mm:
                matches += 1
                supporting.append(SupportingEvidence(
                    finding="Probing depth",
                    value=f"{ca.probing_depth_mm}mm",
                    weight="Strong",
                ))

        # Pain level
        if exp.pain_level_min > 0:
            checks += 1
            if ca.pain_level >= exp.pain_level_min:
                matches += 1
                supporting.append(SupportingEvidence(
                    finding="Pain level",
                    value=f"VAS {ca.pain_level}/10",
                    weight="Moderate" if ca.pain_level < 7 else "Strong",
                ))

        return matches / checks if checks > 0 else 0.5  # neutral if no findings to check

    def _score_onset_duration(
        self,
        profile: DiagnosisProfile,
        req: DiagnosisRequest,
        supporting: list[SupportingEvidence],
    ) -> float:
        """Match onset type and duration range. Returns 0.0-1.0."""
        cc = req.m1.chief_complaint
        score = 0.0
        checks = 0

        # Onset type
        if profile.typical_onset and cc.onset is not None:
            checks += 1
            if cc.onset in profile.typical_onset:
                score += 1.0
                supporting.append(SupportingEvidence(
                    finding="Symptom onset",
                    value=cc.onset.value,
                    weight="Weak",
                ))

        # Duration range
        min_d, max_d = profile.duration_range_days
        checks += 1
        if min_d <= cc.duration_days <= max_d:
            score += 1.0
            supporting.append(SupportingEvidence(
                finding="Duration",
                value=f"{cc.duration_days} days",
                weight="Weak",
            ))

        return score / checks if checks > 0 else 0.5

    def _score_m2_modifier(
        self,
        profile: DiagnosisProfile,
        req: DiagnosisRequest,
        supporting: list[SupportingEvidence],
    ) -> float:
        """
        Boost profiles based on M2 risk findings.
        Infections boost abscess / cellulitis profiles.
        Systemic high risk boosts complex profiles.
        """
        m2 = req.m2
        modifier = 0.5  # neutral baseline

        # Infection analysis boosts infection-related diagnoses
        if m2.infection_analysis:
            infection_codes = {"DX-03", "DX-04", "DX-05", "DX-06", "DX-09", "DX-12"}
            if profile.code in infection_codes:
                if m2.infection_analysis.spread_risk == "High":
                    modifier += 0.4
                    supporting.append(SupportingEvidence(
                        finding="M2: Infection spread risk",
                        value="High",
                        weight="Strong",
                    ))
                elif m2.infection_analysis.spread_risk == "Medium":
                    modifier += 0.2
                    supporting.append(SupportingEvidence(
                        finding="M2: Infection spread risk",
                        value="Medium",
                        weight="Moderate",
                    ))

            # Spreading infection pattern especially boosts cellulitis
            if m2.infection_analysis.pattern == "Spreading_Infection" and profile.code == "DX-06":
                modifier += 0.3
                supporting.append(SupportingEvidence(
                    finding="M2: Spreading infection pattern",
                    value=m2.infection_analysis.pattern,
                    weight="Strong",
                ))

            # Chronic pattern boosts chronic periapical abscess
            if m2.infection_analysis.pattern == "Chronic_Infection" and profile.code == "DX-04":
                modifier += 0.3
                supporting.append(SupportingEvidence(
                    finding="M2: Chronic infection pattern",
                    value=m2.infection_analysis.pattern,
                    weight="Strong",
                ))

        # High surgical complexity boosts severe diagnoses
        if m2.surgical_complexity and m2.surgical_complexity.score >= 45:
            severe_codes = {"DX-03", "DX-06"}
            if profile.code in severe_codes:
                modifier += 0.15

        # Immediate attention required boosts acute conditions
        if m2.risk_summary.immediate_attention_required:
            acute_codes = {"DX-01", "DX-03", "DX-06", "DX-09"}
            if profile.code in acute_codes:
                modifier += 0.1

        return min(modifier, 1.0)

    def _score_contradictions(
        self,
        profile: DiagnosisProfile,
        req: DiagnosisRequest,
        contradicting: list[ContradictingEvidence],
    ) -> float:
        """
        Calculate contradiction penalty. Returns total penalty (0.0+).
        """
        penalty = 0.0
        patient_symptoms = set(req.m1.chief_complaint.symptoms)
        ca = req.m1.clinical_assessment

        # Contradicting symptoms
        for cs in profile.contradicting_symptoms:
            if cs in patient_symptoms:
                penalty += CONTRADICTION_PENALTY
                contradicting.append(ContradictingEvidence(
                    finding=f"Symptom: {cs.value}",
                    value="Present",
                    reason=f"{cs.value} is atypical for {profile.name}",
                ))

        # Contradicting vitality
        if (
            profile.contradicting_vitality is not None
            and ca.vitality_test == profile.contradicting_vitality
        ):
            penalty += CONTRADICTION_PENALTY
            # already added in _score_findings if it mismatch

        return penalty

    # ═══════════════════════════════════════════════════════════════════════
    #  JUSTIFICATION & SUMMARY BUILDERS
    # ═══════════════════════════════════════════════════════════════════════

    def _build_justification(
        self,
        profile: DiagnosisProfile,
        supporting: list[SupportingEvidence],
        contradicting: list[ContradictingEvidence],
        confidence: float,
    ) -> str:
        """Build a 2-3 sentence justification for this diagnosis."""
        strong = [e.finding for e in supporting if e.weight == "Strong"]
        moderate = [e.finding for e in supporting if e.weight == "Moderate"]
        contra = [e.finding for e in contradicting]

        parts: list[str] = []

        if strong:
            parts.append(
                f"{profile.name} is supported by strong indicators: "
                f"{', '.join(strong[:4])}."
            )
        elif moderate:
            parts.append(
                f"{profile.name} is supported by moderate indicators: "
                f"{', '.join(moderate[:4])}."
            )
        else:
            parts.append(f"{profile.name} has limited supporting evidence in the current presentation.")

        if contra:
            parts.append(
                f"However, {', '.join(contra[:3])} {'is' if len(contra) == 1 else 'are'} "
                f"atypical and reduce confidence."
            )

        parts.append(f"Overall confidence: {confidence}%.")

        return " ".join(parts)

    def _build_clinical_summary(
        self,
        m1,
        m2,
        differentials: list[DifferentialDiagnosis],
    ) -> str:
        """Generate a one-paragraph clinical presentation summary."""
        ca = m1.clinical_assessment
        cc = m1.chief_complaint
        site = m1.site_assessment
        demo = m1.demographics

        symptoms_str = ", ".join(s.value.replace("_", " ").lower() for s in cc.symptoms[:5])
        risk_level = m2.risk_summary.overall_risk_level.value

        top_dx = differentials[0].name if differentials else "undetermined condition"

        summary = (
            f"{demo.age}-year-old {demo.gender.value.lower()} presents with "
            f"{cc.description.lower().rstrip('.')} involving tooth {site.tooth_site} "
            f"({site.jaw_region.value.replace('_', ' ').lower()}). "
            f"Key symptoms include {symptoms_str}. "
            f"Pain level is {ca.pain_level}/10 with {ca.swelling_grade.value.lower()} swelling. "
        )

        if ca.fever.present and ca.fever.temperature_celsius:
            summary += f"Fever present at {ca.fever.temperature_celsius}°C. "

        if ca.vitality_test:
            summary += f"Vitality test: {ca.vitality_test.value.replace('_', ' ').lower()}. "

        summary += (
            f"Overall risk level: {risk_level}. "
            f"Most likely diagnosis: {top_dx}."
        )

        return summary
