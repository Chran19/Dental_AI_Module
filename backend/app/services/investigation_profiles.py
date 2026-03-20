"""
Module 4 — Investigation Profile Library
Maps diagnosis codes to recommended imaging and lab tests with urgency and justification.
Pure data structures — consumed by investigation_service.py, no logic here.

References:
    - Roadmap §Phase 2, M4
    - Each diagnosis code (DX-01 to DX-13) is mapped to appropriate investigations
"""

from app.models.enums import ImagingType, LabTestType, InvestigationUrgency


# ═════════════════════════════════════════════════════════════════════════════════
#  INVESTIGATION PROFILES LIBRARY
# ═════════════════════════════════════════════════════════════════════════════════

INVESTIGATION_PROFILES = {
    # ─────────────────────────────────────────────────────────────────────────────
    # DX-01: Irreversible Pulpitis
    # ─────────────────────────────────────────────────────────────────────────────
    "DX-01": {
        "diagnosis_name": "Irreversible Pulpitis",
        "imaging": [ImagingType.PERIAPICAL],
        "labs": [],
        "urgency": InvestigationUrgency.ROUTINE,
        "justification": "Periapical radiograph to rule out periapical pathology and assess bone levels. Confirm pulpal vitality status.",
    },

    # ─────────────────────────────────────────────────────────────────────────────
    # DX-02: Pulp Necrosis
    # ─────────────────────────────────────────────────────────────────────────────
    "DX-02": {
        "diagnosis_name": "Pulp Necrosis",
        "imaging": [ImagingType.PERIAPICAL, ImagingType.CBCT],
        "labs": [],
        "urgency": InvestigationUrgency.ROUTINE,
        "justification": "Periapical to confirm necrosis; CBCT for detailed assessment of periapical lesion extent and anatomical considerations.",
    },

    # ─────────────────────────────────────────────────────────────────────────────
    # DX-03: Acute Periapical Abscess
    # ─────────────────────────────────────────────────────────────────────────────
    "DX-03": {
        "diagnosis_name": "Acute Periapical Abscess",
        "imaging": [ImagingType.PERIAPICAL],
        "labs": [LabTestType.WBC, LabTestType.CRP],
        "urgency": InvestigationUrgency.URGENT,
        "justification": "Periapical imaging to localize abscess. Labs to assess systemic inflammatory response and severity.",
    },

    # ─────────────────────────────────────────────────────────────────────────────
    # DX-04: Chronic Periapical Abscess
    # ─────────────────────────────────────────────────────────────────────────────
    "DX-04": {
        "diagnosis_name": "Chronic Periapical Abscess",
        "imaging": [ImagingType.PERIAPICAL, ImagingType.CBCT],
        "labs": [],
        "urgency": InvestigationUrgency.ROUTINE,
        "justification": "Periapical to identify chronic lesion; CBCT for better assessment of lesion size, extent, and relationship to adjacent structures.",
    },

    # ─────────────────────────────────────────────────────────────────────────────
    # DX-05: Periodontal Abscess
    # ─────────────────────────────────────────────────────────────────────────────
    "DX-05": {
        "diagnosis_name": "Periodontal Abscess",
        "imaging": [ImagingType.PERIAPICAL],
        "labs": [LabTestType.WBC, LabTestType.CRP],
        "urgency": InvestigationUrgency.URGENT,
        "justification": "Periapical to assess bone levels and periodontal defect. Labs to evaluate systemic inflammatory response.",
    },

    # ─────────────────────────────────────────────────────────────────────────────
    # DX-06: Cellulitis
    # ─────────────────────────────────────────────────────────────────────────────
    "DX-06": {
        "diagnosis_name": "Cellulitis",
        "imaging": [ImagingType.PERIAPICAL, ImagingType.OPG],
        "labs": [LabTestType.WBC, LabTestType.CRP, LabTestType.ESR],
        "urgency": InvestigationUrgency.EMERGENCY,
        "justification": "OPG and periapical to identify source of infection. Labs for systemic infection severity and antibiotic therapy monitoring.",
    },

    # ─────────────────────────────────────────────────────────────────────────────
    # DX-07: Reversible Pulpitis
    # ─────────────────────────────────────────────────────────────────────────────
    "DX-07": {
        "diagnosis_name": "Reversible Pulpitis",
        "imaging": [ImagingType.PERIAPICAL],
        "labs": [],
        "urgency": InvestigationUrgency.ROUTINE,
        "justification": "Periapical radiograph to rule out caries, restore margins, and assess bone levels.",
    },

    # ─────────────────────────────────────────────────────────────────────────────
    # DX-08: Cracked Tooth
    # ─────────────────────────────────────────────────────────────────────────────
    "DX-08": {
        "diagnosis_name": "Cracked Tooth",
        "imaging": [ImagingType.PERIAPICAL],
        "labs": [],
        "urgency": InvestigationUrgency.ROUTINE,
        "justification": "Periapical radiograph to assess extent of crack and detect any associated periapical pathology.",
    },

    # ─────────────────────────────────────────────────────────────────────────────
    # DX-09: Pericoronitis
    # ─────────────────────────────────────────────────────────────────────────────
    "DX-09": {
        "diagnosis_name": "Pericoronitis",
        "imaging": [ImagingType.OPG, ImagingType.CBCT],
        "labs": [LabTestType.WBC, LabTestType.CRP],
        "urgency": InvestigationUrgency.URGENT,
        "justification": "OPG to assess third molar position and CBCT for detailed bone anatomy. Labs to assess inflammatory severity.",
    },

    # ─────────────────────────────────────────────────────────────────────────────
    # DX-10: Traumatic Occlusion
    # ─────────────────────────────────────────────────────────────────────────────
    "DX-10": {
        "diagnosis_name": "Traumatic Occlusion",
        "imaging": [ImagingType.PERIAPICAL, ImagingType.BITEWING],
        "labs": [],
        "urgency": InvestigationUrgency.ROUTINE,
        "justification": "Periapical and bitewing films to assess occlusal forces, bone levels, and detect any secondary pathology.",
    },

    # ─────────────────────────────────────────────────────────────────────────────
    # DX-11: Periapical Cyst
    # ─────────────────────────────────────────────────────────────────────────────
    "DX-11": {
        "diagnosis_name": "Periapical Cyst",
        "imaging": [ImagingType.PERIAPICAL, ImagingType.CBCT],
        "labs": [],
        "urgency": InvestigationUrgency.ROUTINE,
        "justification": "Periapical for initial assessment; CBCT for detailed 3D evaluation of cyst size, extent, and impacts on adjacent structures.",
    },

    # ─────────────────────────────────────────────────────────────────────────────
    # DX-12: ANUG (Acute Necrotizing Ulcerative Gingivitis)
    # ─────────────────────────────────────────────────────────────────────────────
    "DX-12": {
        "diagnosis_name": "Acute Necrotizing Ulcerative Gingivitis (ANUG)",
        "imaging": [ImagingType.PERIAPICAL, ImagingType.OPG],
        "labs": [LabTestType.WBC, LabTestType.ESR, LabTestType.CRP],
        "urgency": InvestigationUrgency.URGENT,
        "justification": "OPG and periapical to assess bone loss and lesion extent. Labs to evaluate systemic status and immunocompetence.",
    },

    # ─────────────────────────────────────────────────────────────────────────────
    # DX-13: TMJ Disorder
    # ─────────────────────────────────────────────────────────────────────────────
    "DX-13": {
        "diagnosis_name": "Temporomandibular Joint (TMJ) Disorder",
        "imaging": [ImagingType.PERIAPICAL, ImagingType.OPG],
        "labs": [],
        "urgency": InvestigationUrgency.ROUTINE,
        "justification": "OPG to assess TMJ structures and dental occlusion. Periapical if odontogenic source suspected.",
    },
}


# ═════════════════════════════════════════════════════════════════════════════════
#  HELPER FUNCTION
# ═════════════════════════════════════════════════════════════════════════════════

def get_investigation_profile(diagnosis_code: str) -> dict | None:
    """
    Retrieve investigation profile for a given diagnosis code.

    Args:
        diagnosis_code: Diagnosis code (e.g., "DX-01")

    Returns:
        Investigation profile dict or None if not found
    """
    return INVESTIGATION_PROFILES.get(diagnosis_code)
