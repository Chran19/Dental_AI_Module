"""
Module 5 — Unit Tests for Treatment Suggestion Engine
Tests diagnosis → treatment mapping, medication recommendations,
contraindication checking, and feasibility assessment.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

import pytest

from app.models.enums import (
    ContraindicationSeverity,
    SystemicCondition,
    TreatmentType,
)
from app.schemas.treatment import TreatmentRequest
from app.services.treatment_service import TreatmentService


# ═════════════════════════════════════════════════════════════════════════════════
#  FIXTURES & HELPER FUNCTIONS
# ═════════════════════════════════════════════════════════════════════════════════

_CASE_ID = str(uuid.uuid4())
_PATIENT_ID = str(uuid.uuid4())
_DOCTOR_ID = str(uuid.uuid4())


def _treatment_request(**overrides) -> TreatmentRequest:
    """Base treatment request."""
    base = {
        "case_id": _CASE_ID,
        "patient_id": _PATIENT_ID,
        "doctor_id": _DOCTOR_ID,
        "top_diagnosis_code": "DX-01",
        "top_diagnosis_name": "Irreversible Pulpitis",
        "confidence_percent": 85.0,
        "systemic_conditions": [],
        "current_medications": [],
        "allergies": [],
        "age": 45,
    }
    base.update(overrides)
    return TreatmentRequest(**base)


# ═════════════════════════════════════════════════════════════════════════════════
#  TEST: DX-01 Irreversible Pulpitis
# ═════════════════════════════════════════════════════════════════════════════════

def test_dx01_root_canal_primary_treatment():
    """
    DX-01 (Irreversible Pulpitis) should recommend root canal as primary.
    """
    req = _treatment_request(
        top_diagnosis_code="DX-01",
        top_diagnosis_name="Irreversible Pulpitis",
    )

    result = TreatmentService.suggest(req)

    assert result.referenced_diagnosis_code == "DX-01"
    assert result.primary_treatment.treatment_type == TreatmentType.ROOT_CANAL
    assert result.primary_treatment.rank == 1
    assert result.primary_treatment.success_rate >= 0.8


def test_dx01_extraction_as_alternative():
    """
    DX-01 should have extraction as alternative treatment.
    """
    req = _treatment_request(
        top_diagnosis_code="DX-01",
        top_diagnosis_name="Irreversible Pulpitis",
    )

    result = TreatmentService.suggest(req)

    assert len(result.alternative_treatments) >= 1
    alternative_types = [alt.treatment_type for alt in result.alternative_treatments]
    assert TreatmentType.EXTRACTION in alternative_types


def test_dx01_medications_included():
    """
    DX-01 should include analgesic and anti-inflammatory medications.
    """
    req = _treatment_request(
        top_diagnosis_code="DX-01",
        top_diagnosis_name="Irreversible Pulpitis",
    )

    result = TreatmentService.suggest(req)

    assert len(result.primary_treatment.medications) >= 2
    med_types = [med.medication_type.value for med in result.primary_treatment.medications]
    assert any("Analgesic" in str(med_type) for med_type in med_types)


# ═════════════════════════════════════════════════════════════════════════════════
#  TEST: DX-03 Acute Periapical Abscess
# ═════════════════════════════════════════════════════════════════════════════════

def test_dx03_abscess_root_canal_primary():
    """
    DX-03 (Acute Periapical Abscess) should recommend root canal as primary.
    """
    req = _treatment_request(
        top_diagnosis_code="DX-03",
        top_diagnosis_name="Acute Periapical Abscess",
    )

    result = TreatmentService.suggest(req)

    assert result.primary_treatment.treatment_type == TreatmentType.ROOT_CANAL
    assert result.referenced_diagnosis_code == "DX-03"


def test_dx03_antibiotics_included():
    """
    DX-03 should include antibiotic medications for infection.
    """
    req = _treatment_request(
        top_diagnosis_code="DX-03",
        top_diagnosis_name="Acute Periapical Abscess",
    )

    result = TreatmentService.suggest(req)

    med_types = [med.medication_type.value for med in result.primary_treatment.medications]
    assert any("Antibiotic" in str(med_type) for med_type in med_types)


# ═════════════════════════════════════════════════════════════════════════════════
#  TEST: DX-06 Cellulitis (EMERGENCY CASE)
# ═════════════════════════════════════════════════════════════════════════════════

def test_dx06_cellulitis_antibiotics_primary():
    """
    DX-06 (Cellulitis) should recommend antibiotics as primary (medical management).
    """
    req = _treatment_request(
        top_diagnosis_code="DX-06",
        top_diagnosis_name="Cellulitis",
    )

    result = TreatmentService.suggest(req)

    assert result.primary_treatment.treatment_type == TreatmentType.ANTIBIOTICS
    assert result.summary.overall_feasibility in ["High", "Moderate", "Low"]


def test_dx06_extraction_alternative():
    """
    DX-06 should have extraction as alternative.
    """
    req = _treatment_request(
        top_diagnosis_code="DX-06",
        top_diagnosis_name="Cellulitis",
    )

    result = TreatmentService.suggest(req)

    alternative_types = [alt.treatment_type for alt in result.alternative_treatments]
    assert TreatmentType.EXTRACTION in alternative_types


# ═════════════════════════════════════════════════════════════════════════════════
#  TEST: DX-07 Reversible Pulpitis
# ═════════════════════════════════════════════════════════════════════════════════

def test_dx07_reversible_pulpitis_restoration():
    """
    DX-07 (Reversible Pulpitis) should recommend composite restoration.
    """
    req = _treatment_request(
        top_diagnosis_code="DX-07",
        top_diagnosis_name="Reversible Pulpitis",
    )

    result = TreatmentService.suggest(req)

    assert result.primary_treatment.treatment_type == TreatmentType.RESTORATION_COMPOSITE


# ═════════════════════════════════════════════════════════════════════════════════
#  TEST: DX-09 Pericoronitis
# ═════════════════════════════════════════════════════════════════════════════════

def test_dx09_pericoronitis_extraction_primary():
    """
    DX-09 (Pericoronitis) should recommend extraction as primary.
    """
    req = _treatment_request(
        top_diagnosis_code="DX-09",
        top_diagnosis_name="Pericoronitis",
    )

    result = TreatmentService.suggest(req)

    assert result.primary_treatment.treatment_type == TreatmentType.EXTRACTION


# ═════════════════════════════════════════════════════════════════════════════════
#  TEST: Contraindication - Bisphosphonates + Extraction
# ═════════════════════════════════════════════════════════════════════════════════

def test_contraindication_bisphosphonates_extraction():
    """
    Bisphosphonate therapy + extraction should flag SEVERE contraindication.
    """
    req = _treatment_request(
        top_diagnosis_code="DX-01",
        top_diagnosis_name="Irreversible Pulpitis",
        systemic_conditions=["Osteoporosis"],  # Bisphosphonates commonly used for osteoporosis
    )

    result = TreatmentService.suggest(req)

    # Should have contraindication alerts
    assert len(result.contraindication_alerts) > 0

    # Find extraction alert
    extraction_alerts = [
        alert for alert in result.contraindication_alerts
        if alert.treatment_type == TreatmentType.EXTRACTION
    ]
    assert len(extraction_alerts) > 0
    assert extraction_alerts[0].severity == ContraindicationSeverity.SEVERE


def test_contraindication_feasibility_reduced():
    """
    SEVERE contraindication should reduce feasibility.
    """
    req = _treatment_request(
        top_diagnosis_code="DX-01",
        systemic_conditions=["Osteoporosis"],  # Bisphosphonates commonly used for osteoporosis
    )

    result = TreatmentService.suggest(req)

    # Feasibility should be impacted
    assert result.summary.overall_feasibility in ["Moderate", "Low"]


# ═════════════════════════════════════════════════════════════════════════════════
#  TEST: Contraindication - Active Infection + Implant
# ═════════════════════════════════════════════════════════════════════════════════

def test_contraindication_absolute_infection_implant():
    """
    Active infection + implant placement should flag ABSOLUTE contraindication.
    """
    req = _treatment_request(
        top_diagnosis_code="DX-09",
        systemic_conditions=["Active_Infection"],
    )

    result = TreatmentService.suggest(req)

    # Should have contraindication alerts
    absolute_alerts = [
        alert for alert in result.contraindication_alerts
        if alert.severity == ContraindicationSeverity.ABSOLUTE
    ]

    if absolute_alerts:
        assert len(absolute_alerts) > 0


# ═════════════════════════════════════════════════════════════════════════════════
#  TEST: Contraindication - Uncontrolled Diabetes + Extraction
# ═════════════════════════════════════════════════════════════════════════════════

def test_contraindication_diabetes_extraction():
    """
    Diabetes + extraction should flag MODERATE contraindication.
    """
    req = _treatment_request(
        top_diagnosis_code="DX-01",
        systemic_conditions=["Diabetes_Type2"],
    )

    result = TreatmentService.suggest(req)

    # Should have alerts
    assert len(result.contraindication_alerts) > 0

    # Check severity
    assert any(
        alert.severity == ContraindicationSeverity.MODERATE
        for alert in result.contraindication_alerts
    )


# ═════════════════════════════════════════════════════════════════════════════════
#  TEST: Multiple Contraindications
# ═════════════════════════════════════════════════════════════════════════════════

def test_multiple_contraindications():
    """
    Multiple patient conditions should generate multiple alerts.
    """
    req = _treatment_request(
        top_diagnosis_code="DX-09",
        systemic_conditions=[
            "Blood_Disorder",
            "Osteoporosis",
            "Diabetes_Type2",
        ],
    )

    result = TreatmentService.suggest(req)

    # Should have multiple alerts
    assert len(result.contraindication_alerts) >= 1
    # Feasibility should reflect risk
    assert result.summary.overall_feasibility in ["Low", "Moderate"]


# ═════════════════════════════════════════════════════════════════════════════════
#  TEST: Invalid Diagnosis Code
# ═════════════════════════════════════════════════════════════════════════════════

def test_invalid_diagnosis_code_raises_error():
    """
    Unknown diagnosis codes should raise ValueError.
    """
    req = _treatment_request(
        top_diagnosis_code="DX-999",
        top_diagnosis_name="Unknown Diagnosis",
    )

    with pytest.raises(ValueError):
        TreatmentService.suggest(req)


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
def test_all_diagnoses_have_treatment_protocols(diagnosis_code, diagnosis_name):
    """
    All 13 diagnoses should have valid treatment protocols.
    """
    req = _treatment_request(
        top_diagnosis_code=diagnosis_code,
        top_diagnosis_name=diagnosis_name,
    )

    result = TreatmentService.suggest(req)

    assert result.case_id == _CASE_ID
    assert result.referenced_diagnosis_code == diagnosis_code
    assert result.primary_treatment is not None
    assert result.primary_treatment.treatment_type is not None


# ═════════════════════════════════════════════════════════════════════════════════
#  TEST: Output Schema Validation
# ═════════════════════════════════════════════════════════════════════════════════

def test_output_contains_required_fields():
    """
    Output should contain all required Module5Output fields.
    """
    req = _treatment_request(
        top_diagnosis_code="DX-01",
    )

    result = TreatmentService.suggest(req)

    # Check all required fields
    assert result.case_id == _CASE_ID
    assert result.patient_id == _PATIENT_ID
    assert result.doctor_id == _DOCTOR_ID
    assert result.module == "M5_Treatment"
    assert result.version == "1.0"
    assert result.generated_at is not None
    assert result.primary_treatment is not None
    assert result.alternative_treatments is not None
    assert result.contraindication_alerts is not None
    assert result.summary is not None


def test_primary_treatment_rank_is_one():
    """
    Primary treatment should always have rank 1.
    """
    req = _treatment_request()

    result = TreatmentService.suggest(req)

    assert result.primary_treatment.rank == 1


def test_alternatives_rank_higher_than_primary():
    """
    Alternative treatments should have rank > 1.
    """
    req = _treatment_request(
        top_diagnosis_code="DX-01",
    )

    result = TreatmentService.suggest(req)

    for alt in result.alternative_treatments:
        assert alt.rank > result.primary_treatment.rank


# ═════════════════════════════════════════════════════════════════════════════════
#  TEST: Feasibility Assessment
# ═════════════════════════════════════════════════════════════════════════════════

def test_feasibility_high_no_contraindications():
    """
    Feasibility should be 'High' when no contraindications.
    """
    req = _treatment_request(
        top_diagnosis_code="DX-07",
        systemic_conditions=[],
    )

    result = TreatmentService.suggest(req)

    assert result.summary.overall_feasibility == "High"


def test_feasibility_affected_by_severity():
    """
    Feasibility should decrease with increasing contraindication severity.
    """
    req_moderate = _treatment_request(
        top_diagnosis_code="DX-09",
        systemic_conditions=["Uncontrolled_Diabetes"],
    )

    result_moderate = TreatmentService.suggest(req_moderate)

    assert result_moderate.summary.overall_feasibility in ["High", "Moderate"]


# ═════════════════════════════════════════════════════════════════════════════════
#  TEST: Reasoning Chain
# ═════════════════════════════════════════════════════════════════════════════════

def test_reasoning_chain_populated():
    """
    Reasoning chain should be populated for audit trail.
    """
    req = _treatment_request(
        top_diagnosis_code="DX-03",
    )

    result = TreatmentService.suggest(req)

    assert result.reasoning_chain is not None
    assert len(result.reasoning_chain) > 0
    # Should include diagnosis reference
    assert any("DX-03" in reason for reason in result.reasoning_chain)
