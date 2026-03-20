"""
Module 5 — Treatment Protocol Library
Maps diagnosis codes to treatment protocols, medications, follow-up guidance.
Pure data structures — consumed by treatment_service.py, no logic.

References:
    - Roadmap §Phase 2, M5
    - Each diagnosis code (DX-01 to DX-13) is mapped to primary + alternative treatments
"""

from __future__ import annotations

from dataclasses import dataclass, field

from app.models.enums import (
    MedicationType,
    TreatmentCategory,
    TreatmentType,
)


# ═════════════════════════════════════════════════════════════════════════════════
#  DATA STRUCTURES
# ═════════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class TreatmentProtocol:
    """
    Treatment protocol for a single diagnosis.
    Specifies primary treatment, alternatives, medications, and follow-up.
    """

    diagnosis_code: str
    diagnosis_name: str
    primary_treatment: TreatmentType
    primary_category: TreatmentCategory
    alternative_treatments: list[tuple[TreatmentType, TreatmentCategory]] = field(
        default_factory=list
    )
    recommended_medications: list[MedicationType] = field(default_factory=list)
    follow_up_days: int = 7
    success_rate_baseline: float = 0.8  # Placeholder for Phase 3 ML
    treatment_notes: str = ""


# ═════════════════════════════════════════════════════════════════════════════════
#  TREATMENT PROTOCOL LIBRARY
# ═════════════════════════════════════════════════════════════════════════════════

TREATMENT_PROTOCOLS = {
    # ─────────────────────────────────────────────────────────────────────────────
    # DX-01: Irreversible Pulpitis
    # ─────────────────────────────────────────────────────────────────────────────
    "DX-01": TreatmentProtocol(
        diagnosis_code="DX-01",
        diagnosis_name="Irreversible Pulpitis",
        primary_treatment=TreatmentType.ROOT_CANAL,
        primary_category=TreatmentCategory.ENDODONTIC,
        alternative_treatments=[
            (TreatmentType.EXTRACTION, TreatmentCategory.SURGICAL),
        ],
        recommended_medications=[
            MedicationType.ANALGESIC,
            MedicationType.ANTI_INFLAMMATORY,
        ],
        follow_up_days=7,
        success_rate_baseline=0.92,
        treatment_notes="Root canal therapy is treatment of choice. Extraction if tooth not restorable.",
    ),

    # ─────────────────────────────────────────────────────────────────────────────
    # DX-02: Pulp Necrosis
    # ─────────────────────────────────────────────────────────────────────────────
    "DX-02": TreatmentProtocol(
        diagnosis_code="DX-02",
        diagnosis_name="Pulp Necrosis",
        primary_treatment=TreatmentType.ROOT_CANAL,
        primary_category=TreatmentCategory.ENDODONTIC,
        alternative_treatments=[
            (TreatmentType.ROOT_CANAL_RETREATMENT, TreatmentCategory.ENDODONTIC),
            (TreatmentType.EXTRACTION, TreatmentCategory.SURGICAL),
        ],
        recommended_medications=[
            MedicationType.ANTIBIOTIC,
            MedicationType.ANALGESIC,
        ],
        follow_up_days=14,
        success_rate_baseline=0.85,
        treatment_notes="Assess periapical status before treatment. May require surgical intervention.",
    ),

    # ─────────────────────────────────────────────────────────────────────────────
    # DX-03: Acute Periapical Abscess
    # ─────────────────────────────────────────────────────────────────────────────
    "DX-03": TreatmentProtocol(
        diagnosis_code="DX-03",
        diagnosis_name="Acute Periapical Abscess",
        primary_treatment=TreatmentType.ROOT_CANAL,
        primary_category=TreatmentCategory.ENDODONTIC,
        alternative_treatments=[
            (TreatmentType.EXTRACTION, TreatmentCategory.SURGICAL),
            (TreatmentType.ANTIBIOTICS, TreatmentCategory.MEDICAL_MANAGEMENT),
        ],
        recommended_medications=[
            MedicationType.ANTIBIOTIC,
            MedicationType.ANALGESIC,
            MedicationType.ANTI_INFLAMMATORY,
        ],
        follow_up_days=7,
        success_rate_baseline=0.88,
        treatment_notes="Start antibiotics immediately if systemic signs. Consider emergency drainage.",
    ),

    # ─────────────────────────────────────────────────────────────────────────────
    # DX-04: Chronic Periapical Abscess
    # ─────────────────────────────────────────────────────────────────────────────
    "DX-04": TreatmentProtocol(
        diagnosis_code="DX-04",
        diagnosis_name="Chronic Periapical Abscess",
        primary_treatment=TreatmentType.ROOT_CANAL,
        primary_category=TreatmentCategory.ENDODONTIC,
        alternative_treatments=[
            (TreatmentType.EXTRACTION, TreatmentCategory.SURGICAL),
            (TreatmentType.MANAGEMENT_CONSERVATIVE, TreatmentCategory.MEDICAL_MANAGEMENT),
        ],
        recommended_medications=[
            MedicationType.ANALGESIC,
            MedicationType.ANTI_INFLAMMATORY,
        ],
        follow_up_days=30,
        success_rate_baseline=0.82,
        treatment_notes="Chronic lesions may resolve spontaneously. Monitor radiographically.",
    ),

    # ─────────────────────────────────────────────────────────────────────────────
    # DX-05: Periodontal Abscess
    # ─────────────────────────────────────────────────────────────────────────────
    "DX-05": TreatmentProtocol(
        diagnosis_code="DX-05",
        diagnosis_name="Periodontal Abscess",
        primary_treatment=TreatmentType.SCALING_ROOT_PLANING,
        primary_category=TreatmentCategory.PERIODONTAL,
        alternative_treatments=[
            (TreatmentType.PROFESSIONAL_CLEANING, TreatmentCategory.PREVENTATIVE),
            (TreatmentType.PERIODONTAL_SURGERY, TreatmentCategory.SURGICAL),
            (TreatmentType.EXTRACTION, TreatmentCategory.SURGICAL),
        ],
        recommended_medications=[
            MedicationType.ANTIBIOTIC,
            MedicationType.ANALGESIC,
        ],
        follow_up_days=7,
        success_rate_baseline=0.85,
        treatment_notes="Drainage and scaling critical. May need systemic antibiotics if severe.",
    ),

    # ─────────────────────────────────────────────────────────────────────────────
    # DX-06: Cellulitis
    # ─────────────────────────────────────────────────────────────────────────────
    "DX-06": TreatmentProtocol(
        diagnosis_code="DX-06",
        diagnosis_name="Cellulitis",
        primary_treatment=TreatmentType.ANTIBIOTICS,
        primary_category=TreatmentCategory.MEDICAL_MANAGEMENT,
        alternative_treatments=[
            (TreatmentType.EXTRACTION, TreatmentCategory.SURGICAL),
            (TreatmentType.ROOT_CANAL, TreatmentCategory.ENDODONTIC),
        ],
        recommended_medications=[
            MedicationType.ANTIBIOTIC,
            MedicationType.ANALGESIC,
            MedicationType.ANTI_INFLAMMATORY,
        ],
        follow_up_days=3,
        success_rate_baseline=0.90,
        treatment_notes="EMERGENCY: Start broad-spectrum antibiotics immediately. Refer if facial swelling.",
    ),

    # ─────────────────────────────────────────────────────────────────────────────
    # DX-07: Reversible Pulpitis
    # ─────────────────────────────────────────────────────────────────────────────
    "DX-07": TreatmentProtocol(
        diagnosis_code="DX-07",
        diagnosis_name="Reversible Pulpitis",
        primary_treatment=TreatmentType.RESTORATION_COMPOSITE,
        primary_category=TreatmentCategory.RESTORATIVE,
        alternative_treatments=[
            (TreatmentType.PROFESSIONAL_CLEANING, TreatmentCategory.PREVENTATIVE),
            (TreatmentType.ROOT_CANAL, TreatmentCategory.ENDODONTIC),
        ],
        recommended_medications=[
            MedicationType.ANALGESIC,
            MedicationType.ANTI_INFLAMMATORY,
        ],
        follow_up_days=7,
        success_rate_baseline=0.94,
        treatment_notes="Conservative restoration sufficient. Remove irritant (decay/margins).",
    ),

    # ─────────────────────────────────────────────────────────────────────────────
    # DX-08: Cracked Tooth
    # ─────────────────────────────────────────────────────────────────────────────
    "DX-08": TreatmentProtocol(
        diagnosis_code="DX-08",
        diagnosis_name="Cracked Tooth",
        primary_treatment=TreatmentType.CROWN,
        primary_category=TreatmentCategory.PROSTHETIC,
        alternative_treatments=[
            (TreatmentType.EXTRACTION, TreatmentCategory.SURGICAL),
            (TreatmentType.ROOT_CANAL, TreatmentCategory.ENDODONTIC),
        ],
        recommended_medications=[
            MedicationType.ANALGESIC,
            MedicationType.ANTI_INFLAMMATORY,
        ],
        follow_up_days=14,
        success_rate_baseline=0.88,
        treatment_notes="Crown placement prevents progression. May need RCT if pulp involved.",
    ),

    # ─────────────────────────────────────────────────────────────────────────────
    # DX-09: Pericoronitis
    # ─────────────────────────────────────────────────────────────────────────────
    "DX-09": TreatmentProtocol(
        diagnosis_code="DX-09",
        diagnosis_name="Pericoronitis",
        primary_treatment=TreatmentType.EXTRACTION,
        primary_category=TreatmentCategory.SURGICAL,
        alternative_treatments=[
            (TreatmentType.ANTIBIOTICS, TreatmentCategory.MEDICAL_MANAGEMENT),
            (TreatmentType.PROFESSIONAL_CLEANING, TreatmentCategory.PREVENTATIVE),
        ],
        recommended_medications=[
            MedicationType.ANTIBIOTIC,
            MedicationType.ANALGESIC,
            MedicationType.ANTI_INFLAMMATORY,
        ],
        follow_up_days=7,
        success_rate_baseline=0.92,
        treatment_notes="Extraction is definitive. Treat infection first if severe.",
    ),

    # ─────────────────────────────────────────────────────────────────────────────
    # DX-10: Traumatic Occlusion
    # ─────────────────────────────────────────────────────────────────────────────
    "DX-10": TreatmentProtocol(
        diagnosis_code="DX-10",
        diagnosis_name="Traumatic Occlusion",
        primary_treatment=TreatmentType.MANAGEMENT_CONSERVATIVE,
        primary_category=TreatmentCategory.MEDICAL_MANAGEMENT,
        alternative_treatments=[
            (TreatmentType.PROFESSIONAL_CLEANING, TreatmentCategory.PREVENTATIVE),
            (TreatmentType.ROOT_CANAL, TreatmentCategory.ENDODONTIC),
        ],
        recommended_medications=[
            MedicationType.ANALGESIC,
            MedicationType.ANTI_INFLAMMATORY,
        ],
        follow_up_days=7,
        success_rate_baseline=0.85,
        treatment_notes="Occlusal adjustment may be needed. Monitor for symptoms.",
    ),

    # ─────────────────────────────────────────────────────────────────────────────
    # DX-11: Periapical Cyst
    # ─────────────────────────────────────────────────────────────────────────────
    "DX-11": TreatmentProtocol(
        diagnosis_code="DX-11",
        diagnosis_name="Periapical Cyst",
        primary_treatment=TreatmentType.ROOT_CANAL,
        primary_category=TreatmentCategory.ENDODONTIC,
        alternative_treatments=[
            (TreatmentType.EXTRACTION, TreatmentCategory.SURGICAL),
            (TreatmentType.BONE_GRAFT, TreatmentCategory.SURGICAL),
        ],
        recommended_medications=[
            MedicationType.ANALGESIC,
            MedicationType.ANTI_INFLAMMATORY,
        ],
        follow_up_days=30,
        success_rate_baseline=0.80,
        treatment_notes="RCT treats causative tooth. Surgical intervention if cyst large.",
    ),

    # ─────────────────────────────────────────────────────────────────────────────
    # DX-12: ANUG (Acute Necrotizing Ulcerative Gingivitis)
    # ─────────────────────────────────────────────────────────────────────────────
    "DX-12": TreatmentProtocol(
        diagnosis_code="DX-12",
        diagnosis_name="Acute Necrotizing Ulcerative Gingivitis (ANUG)",
        primary_treatment=TreatmentType.PROFESSIONAL_CLEANING,
        primary_category=TreatmentCategory.PREVENTATIVE,
        alternative_treatments=[
            (TreatmentType.SCALING_ROOT_PLANING, TreatmentCategory.PERIODONTAL),
            (TreatmentType.ANTIBIOTICS, TreatmentCategory.MEDICAL_MANAGEMENT),
        ],
        recommended_medications=[
            MedicationType.ANTIBIOTIC,
            MedicationType.ANTIMICROBIAL_RINSE,
            MedicationType.ANALGESIC,
        ],
        follow_up_days=7,
        success_rate_baseline=0.88,
        treatment_notes="Urgent debridement and instruction. Rule out immunosuppression.",
    ),

    # ─────────────────────────────────────────────────────────────────────────────
    # DX-13: TMJ Disorder
    # ─────────────────────────────────────────────────────────────────────────────
    "DX-13": TreatmentProtocol(
        diagnosis_code="DX-13",
        diagnosis_name="Temporomandibular Joint (TMJ) Disorder",
        primary_treatment=TreatmentType.MANAGEMENT_CONSERVATIVE,
        primary_category=TreatmentCategory.MEDICAL_MANAGEMENT,
        alternative_treatments=[
            (TreatmentType.PROFESSIONAL_CLEANING, TreatmentCategory.PREVENTATIVE),
            (TreatmentType.ANTIBIOTICS, TreatmentCategory.MEDICAL_MANAGEMENT),
        ],
        recommended_medications=[
            MedicationType.ANALGESIC,
            MedicationType.ANTI_INFLAMMATORY,
        ],
        follow_up_days=14,
        success_rate_baseline=0.75,
        treatment_notes="Conservative treatment: rest, ice, analgesics. Physical therapy referral.",
    ),
}


# ═════════════════════════════════════════════════════════════════════════════════
#  HELPER FUNCTION
# ═════════════════════════════════════════════════════════════════════════════════

def get_treatment_protocol(diagnosis_code: str) -> TreatmentProtocol | None:
    """
    Retrieve treatment protocol for a given diagnosis code.

    Args:
        diagnosis_code: Diagnosis code (e.g., "DX-01")

    Returns:
        TreatmentProtocol or None if not found
    """
    return TREATMENT_PROTOCOLS.get(diagnosis_code)
