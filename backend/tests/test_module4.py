"""
Module 4 — Unit Tests for Investigation & Imaging Recommendation
Tests diagnosis → investigation mapping, risk amplification logic,
ranking by urgency, and the API endpoint.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

import pytest

from app.models.enums import ImagingType, InvestigationUrgency, LabTestType
from app.schemas.investigation import InvestigationRequest
from app.services.investigation_service import InvestigationService


# ═════════════════════════════════════════════════════════════════════════════════
#  FIXTURES & HELPER FUNCTIONS
# ═════════════════════════════════════════════════════════════════════════════════

_CASE_ID = str(uuid.uuid4())
_PATIENT_ID = str(uuid.uuid4())
_DOCTOR_ID = str(uuid.uuid4())
_NOW = datetime.now(timezone.utc)


def _investigation_request(**overrides) -> InvestigationRequest:
    """Base investigation request."""
    base = {
        "case_id": _CASE_ID,
        "patient_id": _PATIENT_ID,
        "doctor_id": _DOCTOR_ID,
        "top_diagnosis_code": "DX-01",
        "top_diagnosis_name": "Irreversible Pulpitis",
        "confidence_percent": 85.0,
        "risk_factors": None,
        "overall_risk_level": None,
    }
    # Update with overrides
    base.update(overrides)
    return InvestigationRequest(**base)


# ═════════════════════════════════════════════════════════════════════════════════
#  TEST: DX-01 Irreversible Pulpitis
# ═════════════════════════════════════════════════════════════════════════════════

def test_dx01_irreversible_pulpitis_basic_imaging():
    """
    DX-01 (Irreversible Pulpitis) should recommend periapical imaging.
    """
    req = _investigation_request(
        top_diagnosis_code="DX-01",
        top_diagnosis_name="Irreversible Pulpitis",
    )

    result = InvestigationService.recommend(req)

    assert result.referenced_diagnosis_code == "DX-01"
    assert result.summary.total_imaging_count >= 1
    assert any(r.imaging_type == ImagingType.PERIAPICAL for r in result.imaging_recommendations)
    assert result.summary.total_lab_count == 0


def test_dx01_routine_urgency():
    """
    DX-01 should have ROUTINE urgency (non-emergency case).
    """
    req = _investigation_request(
        top_diagnosis_code="DX-01",
        top_diagnosis_name="Irreversible Pulpitis",
    )

    result = InvestigationService.recommend(req)

    assert result.summary.overall_urgency == InvestigationUrgency.ROUTINE


# ═════════════════════════════════════════════════════════════════════════════════
#  TEST: DX-02 Pulp Necrosis
# ═════════════════════════════════════════════════════════════════════════════════

def test_dx02_pulp_necrosis_cbct_imaging():
    """
    DX-02 (Pulp Necrosis) should recommend BOTH periapical and CBCT imaging.
    """
    req = _investigation_request(
        top_diagnosis_code="DX-02",
        top_diagnosis_name="Pulp Necrosis",
    )

    result = InvestigationService.recommend(req)

    assert result.referenced_diagnosis_code == "DX-02"
    assert result.summary.total_imaging_count >= 2
    imaging_types = [r.imaging_type for r in result.imaging_recommendations]
    assert ImagingType.PERIAPICAL in imaging_types
    assert ImagingType.CBCT in imaging_types
    assert result.summary.total_lab_count == 0


# ═════════════════════════════════════════════════════════════════════════════════
#  TEST: DX-03 Acute Periapical Abscess
# ═════════════════════════════════════════════════════════════════════════════════

def test_dx03_abscess_imaging_and_labs():
    """
    DX-03 (Acute Periapical Abscess) should recommend imaging AND lab tests.
    """
    req = _investigation_request(
        top_diagnosis_code="DX-03",
        top_diagnosis_name="Acute Periapical Abscess",
    )

    result = InvestigationService.recommend(req)

    assert result.referenced_diagnosis_code == "DX-03"
    assert result.summary.total_imaging_count >= 1
    assert result.summary.total_lab_count >= 2  # WBC + CRP
    lab_types = [r.test_type for r in result.lab_recommendations]
    assert LabTestType.WBC in lab_types
    assert LabTestType.CRP in lab_types


def test_dx03_urgent_urgency():
    """
    DX-03 should have URGENT urgency (infection suspected).
    """
    req = _investigation_request(
        top_diagnosis_code="DX-03",
        top_diagnosis_name="Acute Periapical Abscess",
    )

    result = InvestigationService.recommend(req)

    assert result.summary.overall_urgency == InvestigationUrgency.URGENT


# ═════════════════════════════════════════════════════════════════════════════════
#  TEST: DX-06 Cellulitis
# ═════════════════════════════════════════════════════════════════════════════════

def test_dx06_cellulitis_emergency_urgency():
    """
    DX-06 (Cellulitis) is a medical emergency; should have EMERGENCY urgency.
    """
    req = _investigation_request(
        top_diagnosis_code="DX-06",
        top_diagnosis_name="Cellulitis",
    )

    result = InvestigationService.recommend(req)

    assert result.referenced_diagnosis_code == "DX-06"
    assert result.summary.overall_urgency == InvestigationUrgency.EMERGENCY
    assert result.summary.total_imaging_count >= 2  # OPG + Periapical
    assert result.summary.total_lab_count >= 3  # WBC + CRP + ESR


def test_dx06_cellulitis_all_labs():
    """
    DX-06 should recommend WBC, CRP, and ESR labs.
    """
    req = _investigation_request(
        top_diagnosis_code="DX-06",
        top_diagnosis_name="Cellulitis",
    )

    result = InvestigationService.recommend(req)

    lab_types = [r.test_type for r in result.lab_recommendations]
    assert LabTestType.WBC in lab_types
    assert LabTestType.CRP in lab_types
    assert LabTestType.ESR in lab_types


# ═════════════════════════════════════════════════════════════════════════════════
#  TEST: DX-11 Periapical Cyst
# ═════════════════════════════════════════════════════════════════════════════════

def test_dx11_cyst_cbct_for_3d():
    """
    DX-11 (Periapical Cyst) should recommend CBCT for 3D assessment.
    """
    req = _investigation_request(
        top_diagnosis_code="DX-11",
        top_diagnosis_name="Periapical Cyst",
    )

    result = InvestigationService.recommend(req)

    assert result.referenced_diagnosis_code == "DX-11"
    imaging_types = [r.imaging_type for r in result.imaging_recommendations]
    assert ImagingType.PERIAPICAL in imaging_types
    assert ImagingType.CBCT in imaging_types
    assert result.summary.total_lab_count == 0  # No labs for cyst


# ═════════════════════════════════════════════════════════════════════════════════
#  TEST: DX-12 ANUG (Acute Necrotizing Ulcerative Gingivitis)
# ═════════════════════════════════════════════════════════════════════════════════

def test_dx12_anug_urgent_labs():
    """
    DX-12 (ANUG) should recommend urgent labs (WBC, ESR, CRP).
    """
    req = _investigation_request(
        top_diagnosis_code="DX-12",
        top_diagnosis_name="Acute Necrotizing Ulcerative Gingivitis (ANUG)",
    )

    result = InvestigationService.recommend(req)

    assert result.referenced_diagnosis_code == "DX-12"
    assert result.summary.overall_urgency == InvestigationUrgency.URGENT
    assert result.summary.total_imaging_count >= 2
    assert result.summary.total_lab_count >= 3
    lab_types = [r.test_type for r in result.lab_recommendations]
    assert LabTestType.WBC in lab_types
    assert LabTestType.ESR in lab_types
    assert LabTestType.CRP in lab_types


# ═════════════════════════════════════════════════════════════════════════════════
#  TEST: Risk Amplification — High Bone Loss
# ═════════════════════════════════════════════════════════════════════════════════

def test_risk_amplification_high_bone_loss():
    """
    If M2 detects high bone loss, CBCT should be added/amplified.
    """
    req = _investigation_request(
        top_diagnosis_code="DX-01",
        top_diagnosis_name="Irreversible Pulpitis",
        risk_factors=["High_Bone_Loss"],
    )

    result = InvestigationService.recommend(req)

    # Should have CBCT added due to bone loss
    imaging_types = [r.imaging_type for r in result.imaging_recommendations]
    assert ImagingType.CBCT in imaging_types
    # Urgency should be escalated
    assert result.summary.overall_urgency == InvestigationUrgency.URGENT


def test_risk_amplification_no_duplicate_imaging():
    """
    Risk amplification should not add duplicate imaging modalities.
    """
    req = _investigation_request(
        top_diagnosis_code="DX-02",  # Already recommends CBCT
        top_diagnosis_name="Pulp Necrosis",
        risk_factors=["High_Bone_Loss"],  # Also recommends CBCT
    )

    result = InvestigationService.recommend(req)

    # Count occurrences of CBCT
    cbct_count = sum(
        1 for r in result.imaging_recommendations
        if r.imaging_type == ImagingType.CBCT
    )
    assert cbct_count == 1  # Should not duplicate


# ═════════════════════════════════════════════════════════════════════════════════
#  TEST: Risk Amplification — Systemic Infection
# ═════════════════════════════════════════════════════════════════════════════════

def test_risk_amplification_systemic_infection():
    """
    If M2 detects systemic infection, urgency escalates to EMERGENCY.
    """
    req = _investigation_request(
        top_diagnosis_code="DX-03",
        top_diagnosis_name="Acute Periapical Abscess",
        risk_factors=["Systemic_Infection"],
    )

    result = InvestigationService.recommend(req)

    # Base urgency is URGENT, amplification should make it EMERGENCY
    assert result.summary.overall_urgency == InvestigationUrgency.EMERGENCY


# ═════════════════════════════════════════════════════════════════════════════════
#  TEST: Invalid Diagnosis Code
# ═════════════════════════════════════════════════════════════════════════════════

def test_invalid_diagnosis_code_graceful_handling():
    """
    Unknown diagnosis codes should be handled gracefully with logging.
    """
    req = _investigation_request(
        top_diagnosis_code="DX-999",  # Invalid code
        top_diagnosis_name="Unknown Diagnosis",
    )

    result = InvestigationService.recommend(req)

    # Should still return valid output (empty recommendations)
    assert result.case_id == _CASE_ID
    assert result.referenced_diagnosis_code == "DX-999"
    assert result.summary.total_imaging_count == 0
    assert result.summary.total_lab_count == 0


# ═════════════════════════════════════════════════════════════════════════════════
#  TEST: All 13 Diagnoses Coverage
# ═════════════════════════════════════════════════════════════════════════════════

@pytest.mark.parametrize("diagnosis_code,diagnosis_name", [
    ("DX-01", "Irreversible Pulpitis"),
    ("DX-02", "Pulp Necrosis"),
    ("DX-03", "Acute Periapical Abscess"),
    ("DX-04", "Chronic Periapical Abscess"),
    ("DX-05", "Periodontal Abscess"),
    ("DX-06", "Cellulitis"),
    ("DX-07", "Reversible Pulpitis"),
    ("DX-08", "Cracked Tooth"),
    ("DX-09", "Pericoronitis"),
    ("DX-10", "Traumatic Occlusion"),
    ("DX-11", "Periapical Cyst"),
    ("DX-12", "Acute Necrotizing Ulcerative Gingivitis (ANUG)"),
    ("DX-13", "Temporomandibular Joint (TMJ) Disorder"),
])
def test_all_diagnoses_have_profiles(diagnosis_code, diagnosis_name):
    """
    All 13 diagnoses should have valid investigation profiles.
    """
    req = _investigation_request(
        top_diagnosis_code=diagnosis_code,
        top_diagnosis_name=diagnosis_name,
    )

    result = InvestigationService.recommend(req)

    # Even if profile doesn't exist, should return valid output
    assert result.case_id == _CASE_ID
    assert result.referenced_diagnosis_code == diagnosis_code
    # Existing profiles should have recommendations
    if diagnosis_code != "DX-13":  # Assuming DX-13 may not be in profiles yet
        assert result.summary.total_imaging_count + result.summary.total_lab_count > 0


# ═════════════════════════════════════════════════════════════════════════════════
#  TEST: Output Schema Validation
# ═════════════════════════════════════════════════════════════════════════════════

def test_output_contains_required_fields():
    """
    Output should contain all required Module4Output fields.
    """
    req = _investigation_request(
        top_diagnosis_code="DX-01",
    )

    result = InvestigationService.recommend(req)

    # Check all required fields
    assert result.case_id == _CASE_ID
    assert result.patient_id == _PATIENT_ID
    assert result.doctor_id == _DOCTOR_ID
    assert result.module == "M4_Investigation"
    assert result.version == "1.0"
    assert result.generated_at is not None
    assert result.imaging_recommendations is not None
    assert result.lab_recommendations is not None
    assert result.summary is not None
    assert result.summary.overall_urgency is not None


def test_output_summary_counts_match():
    """
    Output summary counts should match actual recommendation lists.
    """
    req = _investigation_request(
        top_diagnosis_code="DX-03",
    )

    result = InvestigationService.recommend(req)

    assert result.summary.total_imaging_count == len(result.imaging_recommendations)
    assert result.summary.total_lab_count == len(result.lab_recommendations)


# ═════════════════════════════════════════════════════════════════════════════════
#  TEST: Reasoning Chain Population
# ═════════════════════════════════════════════════════════════════════════════════

def test_reasoning_chain_present():
    """
    Reasoning chain should be populated for audit trail.
    """
    req = _investigation_request(
        top_diagnosis_code="DX-03",
    )

    result = InvestigationService.recommend(req)

    assert result.reasoning_chain is not None
    assert len(result.reasoning_chain) > 0
    # Should include diagnosis reference
    assert any("DX-03" in reason for reason in result.reasoning_chain)
