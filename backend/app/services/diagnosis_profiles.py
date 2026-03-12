"""
Module 3 — Dental Diagnosis Profile Library
Each profile defines a condition with weighted symptom matches,
expected clinical findings, onset patterns, and risk modifiers.

Profiles are pure data — no logic. The scoring engine in
diagnosis_service.py consumes these.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from app.models.enums import (
    PercussionTest,
    SwellingGrade,
    Symptom,
    SymptomOnset,
    ToothMobilityGrade,
    VitalityTest,
)


# ═════════════════════════════════════════════════════════════════════════════════
#  DATA STRUCTURES
# ═════════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class FindingExpectation:
    """Expected range / value for a clinical finding."""
    vitality: Optional[VitalityTest] = None
    percussion_positive: bool = False           # True = expects positive
    mobility_min: Optional[ToothMobilityGrade] = None  # minimum expected grade
    swelling_expected: Optional[SwellingGrade] = None   # minimum expected grade
    fever_expected: bool = False
    lymphadenopathy_expected: bool = False
    probing_depth_min_mm: Optional[float] = None
    pain_level_min: int = 0                     # minimum VAS expected


@dataclass(frozen=True)
class DiagnosisProfile:
    """
    A single dental condition profile used for differential diagnosis scoring.
    """
    code: str               # e.g. "DX-01"
    name: str               # human-readable name
    category: str            # Pulpal, Periapical, Periodontal, Infection, Trauma, Other

    # Symptom weights: symptom → weight (0.0-1.0). Higher = more indicative.
    symptom_weights: dict[Symptom, float] = field(default_factory=dict)

    # Expected clinical findings
    findings: FindingExpectation = field(default_factory=FindingExpectation)

    # Onset / duration patterns
    typical_onset: list[SymptomOnset] = field(default_factory=list)
    duration_range_days: tuple[int, int] = (0, 365)  # min, max typical

    # Contradicting findings (reduce confidence if present)
    contradicting_symptoms: list[Symptom] = field(default_factory=list)
    contradicting_vitality: Optional[VitalityTest] = None

    # Base weight — some conditions are more common
    base_prevalence: float = 0.5  # 0.0-1.0, higher = more common

    # Brief description for the justification output
    description: str = ""


# ═════════════════════════════════════════════════════════════════════════════════
#  PROFILE LIBRARY
# ═════════════════════════════════════════════════════════════════════════════════

DIAGNOSIS_PROFILES: list[DiagnosisProfile] = [

    # ── DX-01: Irreversible Pulpitis ─────────────────────────────────────────
    DiagnosisProfile(
        code="DX-01",
        name="Irreversible Pulpitis",
        category="Pulpal",
        symptom_weights={
            Symptom.TOOTHACHE: 0.9,
            Symptom.SPONTANEOUS_PAIN: 0.95,
            Symptom.THERMAL_SENSITIVITY_HOT: 0.8,
            Symptom.THERMAL_SENSITIVITY_COLD: 0.5,
            Symptom.PAIN_ON_BITING: 0.4,
            Symptom.REFERRED_PAIN: 0.5,
            Symptom.DIFFICULTY_CHEWING: 0.3,
        },
        findings=FindingExpectation(
            vitality=VitalityTest.VITAL,
            percussion_positive=True,
            pain_level_min=5,
        ),
        typical_onset=[SymptomOnset.SUDDEN, SymptomOnset.INTERMITTENT],
        duration_range_days=(0, 14),
        contradicting_symptoms=[Symptom.FISTULA_SINUS_TRACT, Symptom.GUM_RECESSION],
        contradicting_vitality=VitalityTest.NON_VITAL,
        base_prevalence=0.7,
        description=(
            "Inflammation of the dental pulp that is irreversible. "
            "Characterised by spontaneous, lingering pain often worsened by heat."
        ),
    ),

    # ── DX-02: Pulp Necrosis ────────────────────────────────────────────────
    DiagnosisProfile(
        code="DX-02",
        name="Pulp Necrosis",
        category="Pulpal",
        symptom_weights={
            Symptom.TOOTHACHE: 0.5,
            Symptom.TOOTH_DISCOLORATION: 0.85,
            Symptom.PAIN_ON_BITING: 0.4,
            Symptom.FISTULA_SINUS_TRACT: 0.6,
        },
        findings=FindingExpectation(
            vitality=VitalityTest.NON_VITAL,
            percussion_positive=True,
            pain_level_min=0,
        ),
        typical_onset=[SymptomOnset.GRADUAL],
        duration_range_days=(7, 365),
        contradicting_symptoms=[Symptom.SPONTANEOUS_PAIN, Symptom.THERMAL_SENSITIVITY_HOT],
        contradicting_vitality=VitalityTest.VITAL,
        base_prevalence=0.5,
        description=(
            "Death of the dental pulp. Tooth is non-vital, may have "
            "discoloration, and is often asymptomatic until periapical pathology develops."
        ),
    ),

    # ── DX-03: Acute Periapical Abscess ─────────────────────────────────────
    DiagnosisProfile(
        code="DX-03",
        name="Acute Periapical Abscess",
        category="Periapical",
        symptom_weights={
            Symptom.TOOTHACHE: 0.9,
            Symptom.SPONTANEOUS_PAIN: 0.8,
            Symptom.SWELLING_LOCALIZED: 0.9,
            Symptom.PUS_DISCHARGE: 0.85,
            Symptom.PAIN_ON_BITING: 0.7,
            Symptom.DIFFICULTY_CHEWING: 0.5,
        },
        findings=FindingExpectation(
            vitality=VitalityTest.NON_VITAL,
            percussion_positive=True,
            mobility_min=ToothMobilityGrade.GRADE_1,
            swelling_expected=SwellingGrade.MODERATE,
            fever_expected=True,
            lymphadenopathy_expected=True,
            pain_level_min=6,
        ),
        typical_onset=[SymptomOnset.SUDDEN],
        duration_range_days=(0, 7),
        contradicting_vitality=VitalityTest.VITAL,
        base_prevalence=0.65,
        description=(
            "Acute bacterial infection at the tooth apex. Presents with severe pain, "
            "localised swelling, pus, and systemic signs (fever, lymphadenopathy)."
        ),
    ),

    # ── DX-04: Chronic Periapical Abscess ───────────────────────────────────
    DiagnosisProfile(
        code="DX-04",
        name="Chronic Periapical Abscess",
        category="Periapical",
        symptom_weights={
            Symptom.FISTULA_SINUS_TRACT: 0.95,
            Symptom.TOOTHACHE: 0.3,
            Symptom.BAD_BREATH: 0.4,
            Symptom.PUS_DISCHARGE: 0.7,
            Symptom.TOOTH_DISCOLORATION: 0.4,
        },
        findings=FindingExpectation(
            vitality=VitalityTest.NON_VITAL,
            percussion_positive=False,
            pain_level_min=0,
        ),
        typical_onset=[SymptomOnset.GRADUAL],
        duration_range_days=(14, 365),
        contradicting_symptoms=[Symptom.SPONTANEOUS_PAIN, Symptom.SWELLING_DIFFUSE],
        contradicting_vitality=VitalityTest.VITAL,
        base_prevalence=0.5,
        description=(
            "Long-standing periapical infection with a draining fistula/sinus tract. "
            "Usually low-grade symptoms; requires endodontic or surgical treatment."
        ),
    ),

    # ── DX-05: Periodontal Abscess ──────────────────────────────────────────
    DiagnosisProfile(
        code="DX-05",
        name="Periodontal Abscess",
        category="Periodontal",
        symptom_weights={
            Symptom.SWELLING_LOCALIZED: 0.9,
            Symptom.GUM_BLEEDING: 0.8,
            Symptom.PUS_DISCHARGE: 0.8,
            Symptom.TOOTHACHE: 0.6,
            Symptom.PAIN_ON_BITING: 0.5,
            Symptom.TOOTH_MOBILITY: 0.7,
            Symptom.BAD_BREATH: 0.5,
        },
        findings=FindingExpectation(
            vitality=VitalityTest.VITAL,
            percussion_positive=True,
            mobility_min=ToothMobilityGrade.GRADE_1,
            swelling_expected=SwellingGrade.MODERATE,
            probing_depth_min_mm=5.0,
            pain_level_min=4,
        ),
        typical_onset=[SymptomOnset.SUDDEN, SymptomOnset.GRADUAL],
        duration_range_days=(0, 14),
        contradicting_vitality=VitalityTest.NON_VITAL,
        base_prevalence=0.6,
        description=(
            "Acute infection originating from the periodontal pocket. "
            "Tooth is vital, deep probing depth, gum swelling, bleeding, and pus."
        ),
    ),

    # ── DX-06: Cellulitis / Fascial Space Infection ────────────────────────
    DiagnosisProfile(
        code="DX-06",
        name="Cellulitis / Fascial Space Infection",
        category="Infection",
        symptom_weights={
            Symptom.SWELLING_DIFFUSE: 0.95,
            Symptom.SWELLING_EXTRAORAL: 0.9,
            Symptom.TOOTHACHE: 0.6,
            Symptom.DIFFICULTY_CHEWING: 0.7,
            Symptom.LIMITED_MOUTH_OPENING: 0.85,
            Symptom.PUS_DISCHARGE: 0.5,
        },
        findings=FindingExpectation(
            percussion_positive=True,
            swelling_expected=SwellingGrade.SEVERE,
            fever_expected=True,
            lymphadenopathy_expected=True,
            pain_level_min=7,
        ),
        typical_onset=[SymptomOnset.SUDDEN],
        duration_range_days=(0, 5),
        contradicting_symptoms=[Symptom.GUM_RECESSION, Symptom.FISTULA_SINUS_TRACT],
        base_prevalence=0.3,
        description=(
            "Severe spreading soft-tissue infection involving fascial spaces. "
            "Requires urgent IV antibiotics and possible surgical drainage."
        ),
    ),

    # ── DX-07: Reversible Pulpitis ──────────────────────────────────────────
    DiagnosisProfile(
        code="DX-07",
        name="Reversible Pulpitis",
        category="Pulpal",
        symptom_weights={
            Symptom.THERMAL_SENSITIVITY_COLD: 0.9,
            Symptom.TOOTHACHE: 0.5,
            Symptom.PAIN_ON_BITING: 0.3,
        },
        findings=FindingExpectation(
            vitality=VitalityTest.VITAL,
            percussion_positive=False,
            pain_level_min=2,
        ),
        typical_onset=[SymptomOnset.INTERMITTENT],
        duration_range_days=(0, 30),
        contradicting_symptoms=[
            Symptom.SPONTANEOUS_PAIN,
            Symptom.SWELLING_LOCALIZED,
            Symptom.PUS_DISCHARGE,
            Symptom.FISTULA_SINUS_TRACT,
        ],
        contradicting_vitality=VitalityTest.NON_VITAL,
        base_prevalence=0.75,
        description=(
            "Mild, reversible inflammation of the pulp. Sharp pain with cold stimulus "
            "that resolves when stimulus is removed. Treatable conservatively."
        ),
    ),

    # ── DX-08: Cracked Tooth Syndrome ───────────────────────────────────────
    DiagnosisProfile(
        code="DX-08",
        name="Cracked Tooth Syndrome",
        category="Trauma",
        symptom_weights={
            Symptom.PAIN_ON_BITING: 0.95,
            Symptom.TOOTHACHE: 0.6,
            Symptom.THERMAL_SENSITIVITY_COLD: 0.5,
            Symptom.FRACTURED_TOOTH: 0.9,
        },
        findings=FindingExpectation(
            vitality=VitalityTest.VITAL,
            percussion_positive=True,
            pain_level_min=3,
        ),
        typical_onset=[SymptomOnset.SUDDEN, SymptomOnset.INTERMITTENT],
        duration_range_days=(0, 60),
        contradicting_symptoms=[
            Symptom.PUS_DISCHARGE,
            Symptom.SWELLING_DIFFUSE,
            Symptom.FISTULA_SINUS_TRACT,
        ],
        contradicting_vitality=VitalityTest.NON_VITAL,
        base_prevalence=0.45,
        description=(
            "Incomplete fracture of a vital tooth. Sharp, erratic pain on biting "
            "that is difficult to localise. Diagnosis confirmed by bite test or transillumination."
        ),
    ),

    # ── DX-09: Pericoronitis ────────────────────────────────────────────────
    DiagnosisProfile(
        code="DX-09",
        name="Pericoronitis",
        category="Infection",
        symptom_weights={
            Symptom.TOOTHACHE: 0.7,
            Symptom.SWELLING_LOCALIZED: 0.85,
            Symptom.DIFFICULTY_CHEWING: 0.7,
            Symptom.LIMITED_MOUTH_OPENING: 0.8,
            Symptom.GUM_BLEEDING: 0.5,
            Symptom.PUS_DISCHARGE: 0.6,
            Symptom.BAD_BREATH: 0.5,
        },
        findings=FindingExpectation(
            vitality=VitalityTest.VITAL,
            swelling_expected=SwellingGrade.MODERATE,
            fever_expected=True,
            lymphadenopathy_expected=True,
            pain_level_min=5,
        ),
        typical_onset=[SymptomOnset.GRADUAL],
        duration_range_days=(1, 14),
        contradicting_symptoms=[
            Symptom.TOOTH_DISCOLORATION,
            Symptom.FISTULA_SINUS_TRACT,
        ],
        base_prevalence=0.5,
        description=(
            "Infection of soft tissue around a partially erupted tooth (usually third molar). "
            "Presents with localised pain, swelling, trismus, and possible systemic signs."
        ),
    ),

    # ── DX-10: Traumatic Occlusion ──────────────────────────────────────────
    DiagnosisProfile(
        code="DX-10",
        name="Traumatic Occlusion",
        category="Trauma",
        symptom_weights={
            Symptom.PAIN_ON_BITING: 0.9,
            Symptom.TOOTHACHE: 0.5,
            Symptom.JAW_PAIN: 0.6,
            Symptom.TOOTH_MOBILITY: 0.7,
            Symptom.DIFFICULTY_CHEWING: 0.5,
        },
        findings=FindingExpectation(
            vitality=VitalityTest.VITAL,
            percussion_positive=True,
            mobility_min=ToothMobilityGrade.GRADE_1,
            pain_level_min=3,
        ),
        typical_onset=[SymptomOnset.GRADUAL],
        duration_range_days=(7, 90),
        contradicting_symptoms=[
            Symptom.PUS_DISCHARGE,
            Symptom.SWELLING_DIFFUSE,
            Symptom.FISTULA_SINUS_TRACT,
            Symptom.SPONTANEOUS_PAIN,
        ],
        contradicting_vitality=VitalityTest.NON_VITAL,
        base_prevalence=0.4,
        description=(
            "Occlusal overload causing pain, mobility, and possible widened PDL space. "
            "Tooth is vital. Managed by occlusal adjustment."
        ),
    ),

    # ── DX-11: Periapical Cyst ──────────────────────────────────────────────
    DiagnosisProfile(
        code="DX-11",
        name="Periapical Cyst",
        category="Periapical",
        symptom_weights={
            Symptom.TOOTHACHE: 0.3,
            Symptom.SWELLING_LOCALIZED: 0.6,
            Symptom.TOOTH_DISCOLORATION: 0.5,
            Symptom.FISTULA_SINUS_TRACT: 0.4,
            Symptom.NUMBNESS_TINGLING: 0.4,
        },
        findings=FindingExpectation(
            vitality=VitalityTest.NON_VITAL,
            percussion_positive=False,
            pain_level_min=0,
        ),
        typical_onset=[SymptomOnset.GRADUAL],
        duration_range_days=(30, 365),
        contradicting_symptoms=[Symptom.SPONTANEOUS_PAIN, Symptom.GUM_BLEEDING],
        contradicting_vitality=VitalityTest.VITAL,
        base_prevalence=0.35,
        description=(
            "Epithelial-lined cyst at the tooth apex arising from chronic periapical pathology. "
            "Often discovered incidentally on radiograph. Requires surgical enucleation or extraction."
        ),
    ),

    # ── DX-12: Acute Necrotizing Ulcerative Gingivitis (ANUG) ──────────────
    DiagnosisProfile(
        code="DX-12",
        name="Acute Necrotizing Ulcerative Gingivitis (ANUG)",
        category="Periodontal",
        symptom_weights={
            Symptom.GUM_BLEEDING: 0.95,
            Symptom.BAD_BREATH: 0.9,
            Symptom.ULCERATION: 0.85,
            Symptom.TOOTHACHE: 0.5,
            Symptom.SWELLING_LOCALIZED: 0.4,
        },
        findings=FindingExpectation(
            vitality=VitalityTest.VITAL,
            fever_expected=True,
            lymphadenopathy_expected=True,
            pain_level_min=5,
        ),
        typical_onset=[SymptomOnset.SUDDEN],
        duration_range_days=(0, 14),
        contradicting_symptoms=[
            Symptom.TOOTH_DISCOLORATION,
            Symptom.FISTULA_SINUS_TRACT,
        ],
        base_prevalence=0.25,
        description=(
            "Acute, painful infection of the gingiva with necrosis of interdental papillae. "
            "Presents with punched-out ulcers, bleeding, halitosis, and possible fever. "
            "Associated with immunosuppression, stress, and smoking."
        ),
    ),

    # ── DX-13: TMJ Disorder ────────────────────────────────────────────────
    DiagnosisProfile(
        code="DX-13",
        name="Temporomandibular Joint Disorder",
        category="Other",
        symptom_weights={
            Symptom.JAW_PAIN: 0.95,
            Symptom.JAW_CLICKING: 0.9,
            Symptom.LIMITED_MOUTH_OPENING: 0.8,
            Symptom.REFERRED_PAIN: 0.6,
            Symptom.DIFFICULTY_CHEWING: 0.7,
        },
        findings=FindingExpectation(
            vitality=VitalityTest.VITAL,
            percussion_positive=False,
            pain_level_min=3,
        ),
        typical_onset=[SymptomOnset.GRADUAL, SymptomOnset.INTERMITTENT],
        duration_range_days=(14, 365),
        contradicting_symptoms=[
            Symptom.PUS_DISCHARGE,
            Symptom.SWELLING_LOCALIZED,
            Symptom.GUM_BLEEDING,
            Symptom.FISTULA_SINUS_TRACT,
        ],
        contradicting_vitality=VitalityTest.NON_VITAL,
        base_prevalence=0.4,
        description=(
            "Dysfunction of the temporomandibular joint and associated musculature. "
            "Presents with jaw pain, clicking, limited opening. "
            "Managed with splints, physiotherapy, and analgesics."
        ),
    ),
]


# Quick lookup by code
PROFILE_BY_CODE: dict[str, DiagnosisProfile] = {p.code: p for p in DIAGNOSIS_PROFILES}
